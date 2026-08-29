from fastapi import Request
from time import time
from collections import defaultdict

_request_times: dict[str, list[float]] = defaultdict(list)


def _is_inhuman_request_rate(ip: str, window_seconds=5, max_requests=15) -> bool:
    now = time()
    times = _request_times[ip]
    times.append(now)
    # prune old entries
    _request_times[ip] = [t for t in times if now - t < window_seconds]
    return len(_request_times[ip]) > max_requests


def _inconsistent_referer(normalized: dict) -> bool:
    referer = normalized.get("referer", "")
    origin = normalized.get("origin", "")
    sec_site = normalized.get("sec-fetch-site", "")

    # if sec-fetch-site says same-origin, referer and origin should share host
    if sec_site == "same-origin" and referer and origin:
        if not referer.startswith(origin):
            return True

    # bots sometimes send referer but no origin on a POST, which browsers don't do
    if referer and not origin and sec_site == "":
        return True

    return False


def _missing_browser_headers(request_headers: dict) -> list[str]:
    normalized = {k.lower(): v for k, v in request_headers.items()}

    # these should almost always be present in a real browser request
    required = [
        "sec-fetch-site",
        "sec-fetch-mode",
        "sec-fetch-dest",
        "accept-language",
        "accept-encoding",
        "cache-control",
        "upgrade-insecure-requests",
    ]

    missing = [h for h in required if h not in normalized]
    return missing


def _present_llm_headers(request_headers: dict) -> list[str]:
    normalized = {k.lower(): v.lower() for k, v in request_headers.items()}
    indicators = []
    # check user-agent for known bot signatures
    ua = normalized.get("user-agent", "")
    bot_ua_signatures = [
        "claudebot",
        "claude-web-fetcher",
        "chatgpt-user",
        "gptbot",
        "perplexitybot",
        "youbot",
        "coherebot",
        "python-httpx",
        "python-requests",
        "headlesschrome",
        "langchainbot",
        "applebot",
        "googlebot",
    ]
    for sig in bot_ua_signatures:
        if sig in ua:
            indicators.append(f"user-agent:{sig}")
            break

    # python httpx/requests don't send accept with mime priorities
    accept = normalized.get("accept", "")
    if accept in ("*/*", ""):
        indicators.append("accept:wildcard-only")

    # bots often omit accept-language entirely
    if "accept-language" not in normalized:
        indicators.append("accept-language:missing")

    # bots often send a flat connection:keep-alive with no other context
    if "connection" in normalized and normalized.get("connection") == "keep-alive":
        indicators.append("connection:keep-alive-only")

    # python-requests sends this; browsers never do
    if (
        normalized.get("accept-encoding", "") == "gzip, deflate, br"
        and "sec-fetch-site" not in normalized
    ):
        indicators.append("accept-encoding:bot-pattern")

    # real browsers on http/2+ never send this
    if "pragma" in normalized and "cache-control" not in normalized:
        indicators.append("pragma:without-cache-control")

    return indicators


def is_human(request: Request) -> bool:
    request_headers = dict(request.headers)
    normalized = {k.lower(): v for k, v in request_headers.items()}

    if len(_missing_browser_headers(request_headers)) >= 2:
        return False
    if len(_present_llm_headers(request_headers)) >= 2:
        return False
    if _inconsistent_referer(normalized):
        return False

    client_ip = request.client.host if request.client else ""
    # if client_ip and _is_datacenter_ip(client_ip): # implementing ipapi.is to be done later
    #     return False
    if client_ip and _is_inhuman_request_rate(client_ip):
        return False

    # existing sec-fetch-mode and encoding checks
    if normalized.get("sec-fetch-mode") not in ("navigate", None):
        if normalized.get("sec-fetch-dest") == "document":
            return False
    encoding = normalized.get("accept-encoding", "")
    if encoding and "gzip" not in encoding:
        return False

    return True
