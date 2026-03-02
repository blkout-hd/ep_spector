"""
SPECTOR Media Probe Agent

Probes source URLs for related media files by substituting extensions.
Only operates on publicly accessible URLs with no authentication.

Rate limiting: 1 request/second per domain (configurable via env).
Robots.txt: checked and respected per domain before probing.
Tor: optional, disabled for .gov domains.

This agent does NOT:
  - Bypass authentication or access controls
  - Access sealed or non-public records
  - Violate robots.txt Disallow rules
"""
from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from typing import Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

logger = logging.getLogger("spector.agents.media_probe")

# Rate limit: seconds between requests to the same domain
RATE_LIMIT_SECS = float(os.environ.get("SPECTOR_RATE_LIMIT", "1.0")) if True else 1.0

PROBE_EXTENSIONS = [
    ".mp4", ".mp3", ".wav", ".mov", ".avi",
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".zip", ".tar.gz", ".7z",
    ".xlsx", ".csv", ".json",
    "-redacted.pdf", "-unredacted.pdf", "-full.pdf",
]

_robots_cache: dict[str, RobotFileParser] = {}
_domain_last_request: dict[str, float] = defaultdict(float)


def _is_gov_domain(url: str) -> bool:
    return urlparse(url).netloc.endswith(".gov")


def _robots_allows(url: str) -> bool:
    """Check robots.txt for the given URL. Cache per domain."""
    import requests
    parsed = urlparse(url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    if domain not in _robots_cache:
        rp = RobotFileParser()
        try:
            rp.set_url(f"{domain}/robots.txt")
            rp.read()
        except Exception:
            rp = RobotFileParser()  # empty = allow all
        _robots_cache[domain] = rp
    return _robots_cache[domain].can_fetch("SpectorBot/1.0", url)


def _rate_limit(domain: str):
    """Block until rate limit window has elapsed for this domain."""
    elapsed = time.monotonic() - _domain_last_request[domain]
    if elapsed < RATE_LIMIT_SECS:
        time.sleep(RATE_LIMIT_SECS - elapsed)
    _domain_last_request[domain] = time.monotonic()


def _probe_url(base_url: str, use_tor: bool) -> dict:
    """Probe one base URL for related media extensions."""
    import requests

    proxies = None
    # Never use Tor for .gov domains
    if use_tor and not _is_gov_domain(base_url):
        proxies = {"http": "socks5h://127.0.0.1:9050",
                   "https": "socks5h://127.0.0.1:9050"}

    stem = base_url.rsplit(".", 1)[0] if "." in base_url.split("/")[-1] else base_url
    domain = urlparse(base_url).netloc
    found_urls = []
    status_codes = {}

    for ext in PROBE_EXTENSIONS:
        probe_url = stem + ext
        if not _robots_allows(probe_url):
            logger.debug("robots.txt disallows %s", probe_url)
            continue
        _rate_limit(domain)
        try:
            resp = requests.head(probe_url, proxies=proxies,
                                 timeout=10, allow_redirects=True)
            status_codes[probe_url] = resp.status_code
            if resp.status_code in (200, 301, 302, 403):
                found_urls.append(probe_url)
                logger.info("Found: %s [%d]", probe_url, resp.status_code)
        except Exception as exc:
            logger.debug("Probe failed %s: %s", probe_url, exc)

    return {
        "base_url": base_url,
        "found_urls": found_urls,
        "status_codes": status_codes,
        "via_tor": proxies is not None,
    }


def run(state: dict) -> dict:
    """
    Pipeline node: probe source URLs for related media files.

    Returns dict patch:
      - media_probes: list[MediaProbeResult]
      - errors: list[str]
    """
    import os
    global RATE_LIMIT_SECS
    RATE_LIMIT_SECS = float(os.environ.get("SPECTOR_RATE_LIMIT", "1.0"))

    urls = state.get("source_urls", [])
    use_tor = state.get("use_tor", False)
    probes = []
    errors = []

    for url in urls:
        try:
            result = _probe_url(url, use_tor)
            probes.append(result)
        except Exception as exc:
            logger.error("Media probe failed for %s: %s", url, exc)
            errors.append(f"media_probe:{url}:{exc}")

    logger.info("Media probe complete: %d probed, %d found total",
                len(probes), sum(len(p["found_urls"]) for p in probes))
    return {"media_probes": probes, "errors": errors}
