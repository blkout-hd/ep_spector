#!/usr/bin/env python3
"""
SPECTOR Bootstrap Script

Probes system capabilities at startup and installs the correct
GPU acceleration tier (cuda13x, cuda12x, or CPU fallback).
Writes capabilities to ~/.spector/caps.json for other modules to read.

Safe to run multiple times (idempotent).
"""
from __future__ import annotations

import importlib.util
import json
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("spector.bootstrap")

CAPS_FILE = Path.home() / ".spector" / "caps.json"


def detect_cuda_version() -> str | None:
    """Detect CUDA version from nvcc or nvidia-smi."""
    for cmd in (["nvcc", "--version"], ["nvidia-smi"]):
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
            if "13." in out or "535" in out or "550" in out:
                return "13x"
            if "12." in out or "520" in out or "525" in out or "530" in out:
                return "12x"
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    return None


def detect_capabilities() -> dict:
    cuda = detect_cuda_version()
    caps = {
        "cuda_version": cuda,
        "gpu_tier": f"cuda{cuda}" if cuda else "cpu",
        "has_cudf": importlib.util.find_spec("cudf") is not None,
        "has_cuml": importlib.util.find_spec("cuml") is not None,
        "has_cugraph": importlib.util.find_spec("cugraph") is not None,
        "has_julia": False,
        "has_neo4j": importlib.util.find_spec("neo4j") is not None,
        "has_qdrant": importlib.util.find_spec("qdrant_client") is not None,
        "has_paddle": importlib.util.find_spec("paddleocr") is not None,
    }
    try:
        result = subprocess.run(["julia", "--version"], capture_output=True, timeout=5)
        caps["has_julia"] = result.returncode == 0
    except Exception:
        pass
    return caps


def install_gpu_tier(tier: str):
    """Install GPU-specific packages if not already present."""
    if tier == "cuda13x" and importlib.util.find_spec("cupy_cuda13x") is None:
        logger.info("Installing cupy-cuda13x...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "cupy-cuda13x", "--quiet"
        ])
    elif tier == "cuda12x" and importlib.util.find_spec("cupy_cuda12x") is None:
        logger.info("Installing cupy-cuda12x...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "cupy-cuda12x", "--quiet"
        ])


def main():
    CAPS_FILE.parent.mkdir(parents=True, exist_ok=True)
    caps = detect_capabilities()
    logger.info("Capabilities: %s", caps)

    if caps["gpu_tier"] != "cpu":
        install_gpu_tier(caps["gpu_tier"])

    CAPS_FILE.write_text(json.dumps(caps, indent=2))
    logger.info("Capabilities written to %s", CAPS_FILE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
