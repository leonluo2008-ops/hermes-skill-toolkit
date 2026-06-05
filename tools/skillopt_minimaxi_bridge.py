"""
Tool: skillopt-minimaxi-bridge
================================

Monkey-patch SkillOpt minimax backend to call minimaxi-cn (Anthropic protocol)
instead of the default (dead) api.minimax.io (OpenAI protocol).

**Why this exists**: See ADR 0005 and `docs/research/2026-06-05-skillopt-dogfood-gardener.md`.
- SkillOpt 0.1.0 minimax backend default endpoint (`api.minimax.io`) is dead
- minimaxi-cn is at `api.minimaxi.com/anthropic` and uses Anthropic protocol
- This wrapper translates OpenAI chat.completions payload <-> Anthropic messages
- Does NOT fork SkillOpt (per ADR 0001)

**Usage** (call BEFORE importing skillopt.engine.trainer):

    from skillopt_minimaxi_bridge import patch_skillopt_minimax_backend
    patch_skillopt_minimax_backend()
    # then normal SkillOpt usage
    from skillopt.engine.trainer import ReflACTTrainer

**Self-test** (run as a script):

    python tools/skillopt_minimaxi_bridge.py
    # expects: "OK content: OK" or similar in output

**Required env vars**:
- MINIMAX_CN_API_KEY (required): minimaxi-cn API key
- MINIMAX_BRIDGE_BASE_URL (optional, default: https://api.minimaxi.com/anthropic)
- MINIMAX_BRIDGE_API_VERSION (optional, default: 2023-06-01)

**Stability warning**: This patches `skillopt.model.minimax_backend._post_chat_completion`
which is a private API. SkillOpt upgrades may break this. See ADR 0005 §"后果/负向" mitigation.

License: Apache-2.0 (same as monorepo)
"""
from __future__ import annotations

import os
import sys
import json
import time
import urllib.request
import urllib.error
from typing import Any


# minimaxi-cn 走 Anthropic 协议
DEFAULT_BASE_URL = "https://api.minimaxi.com/anthropic"
DEFAULT_API_VERSION = "2023-06-01"


def _post_chat_completion_anthropic(
    payload: dict[str, Any],
    timeout: float | None,
) -> dict[str, Any]:
    """OpenAI-completions-style payload → call minimaxi-cn Anthropic API
    → convert response back to OpenAI chat.completions format.

    SkillOpt's minimax backend internally builds an OpenAI-format payload
    (with `chat_template_kwargs`, `messages`, `model`, `max_tokens`), then
    hands it to `_post_chat_completion`. We:
      1. Strip OpenAI-only fields
      2. Build Anthropic /v1/messages payload (extract system message)
      3. POST to minimaxi-cn with x-api-key header
      4. Convert response (Anthropic `content[].text`) back to
         OpenAI `choices[0].message.content`
    """
    # 1. Extract messages
    raw_messages = payload.get("messages", [])
    system_text = None
    user_messages = []
    for m in raw_messages:
        if m.get("role") == "system":
            sys_content = m.get("content", "")
            if isinstance(sys_content, str):
                system_text = (system_text + "\n\n" + sys_content) if system_text else sys_content
            elif isinstance(sys_content, list):
                # Anthropic 也支持 system blocks, 但简单起见拼成文本
                texts = [p.get("text", "") for p in sys_content if p.get("type") == "text"]
                joined = "\n\n".join(texts)
                system_text = (system_text + "\n\n" + joined) if system_text else joined
        else:
            user_messages.append({
                "role": m.get("role", "user"),
                "content": m.get("content", ""),
            })

    # 2. Build Anthropic payload
    if system_text is None:
        system_text = "You are a helpful assistant."
    anthropic_payload = {
        "model": payload.get("model", "MiniMax-M3"),
        "max_tokens": payload.get("max_tokens", 4096),
        "system": system_text,
        "messages": user_messages,
    }
    if "temperature" in payload:
        anthropic_payload["temperature"] = payload["temperature"]
    # thinking 透传 (minimaxi 兼容)
    ctk = payload.get("chat_template_kwargs", {})
    if ctk.get("enable_thinking"):
        anthropic_payload["thinking"] = {"type": "enabled"}

    # 3. POST request
    api_key = os.environ.get("MINIMAX_CN_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("MINIMAX_CN_API_KEY env var not set")

    base = os.environ.get("MINIMAX_BRIDGE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    url = f"{base}/v1/messages"
    req = urllib.request.Request(
        url,
        data=json.dumps(anthropic_payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": os.environ.get(
                "MINIMAX_BRIDGE_API_VERSION", DEFAULT_API_VERSION
            ),
        },
        method="POST",
    )
    timeout_s = timeout or 300
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"minimaxi-cn Anthropic API returned HTTP {e.code}: {body[:500]}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"minimaxi-cn Anthropic API request failed: {e}"
        ) from e

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"minimaxi-cn returned non-JSON: {raw[:500]}"
        ) from e

    # 4. Anthropic → OpenAI chat.completions 格式
    content_blocks = data.get("content", [])
    text = ""
    for block in content_blocks:
        if block.get("type") == "text":
            text += block.get("text", "")

    openai_response = {
        "id": data.get("id", ""),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": data.get("model", anthropic_payload["model"]),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": data.get("stop_reason", "stop"),
            }
        ],
        "usage": {
            "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
            "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
            "total_tokens": (
                data.get("usage", {}).get("input_tokens", 0)
                + data.get("usage", {}).get("output_tokens", 0)
            ),
        },
    }
    return openai_response


def patch_skillopt_minimax_backend() -> None:
    """Monkey-patch `skillopt.model.minimax_backend._post_chat_completion`
    to call minimaxi-cn via Anthropic protocol instead of the default
    (dead) OpenAI endpoint.

    MUST be called before importing `skillopt.engine.trainer` (or any module
    that imports it transitively).

    Raises ImportError if SkillOpt is not installed.
    """
    try:
        from skillopt.model import minimax_backend
    except ImportError as e:
        raise ImportError(
            "SkillOpt not installed. Run: pip install skillopt"
        ) from e

    minimax_backend._post_chat_completion = _post_chat_completion_anthropic
    print(
        "[minimaxi-bridge] SkillOpt minimax backend → "
        "patched to minimaxi-cn Anthropic protocol"
    )


if __name__ == "__main__":
    # Self-test: simulate SkillOpt minimax backend's internal payload shape
    test_payload = {
        "model": "MiniMax-M3",
        "messages": [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Reply with just OK"},
        ],
        "max_tokens": 30,
    }
    if not os.environ.get("MINIMAX_CN_API_KEY"):
        print("MINIMAX_CN_API_KEY not set, cannot self-test")
        sys.exit(1)
    result = _post_chat_completion_anthropic(test_payload, timeout=30)
    print("Test result:", json.dumps(result, indent=2)[:400])
