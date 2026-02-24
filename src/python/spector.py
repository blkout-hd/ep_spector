"""
SPECTOR Core - Semantic Pipeline for Entity Correlation and Topological Organization Research

Main entry point for the SPECTOR document analysis and knowledge graph system.
"""

__version__ = "1.0.0"
__author__ = "SPECTOR Contributors"
__license__ = "MIT"

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent.parent / "spector.log")
    ]
)

logger = logging.getLogger("spector")


def check_system_capabilities() -> dict:
    """
    Probe system for available capabilities (CUDA, libraries, etc.)
    
    Returns:
        dict: Capability matrix with detected features
    """
    import importlib.util
    
    capabilities = {
        "python_version": sys.version,
        "cuda_tier": "cpu",
        "has_cudf": False,
        "has_cuml": False,
        "has_cugraph": False,
        "has_julia": False,
        "has_neo4j": False,
        "has_qdrant": False,
    }
    
    # Check CUDA tier
    if importlib.util.find_spec("cupy_cuda13x"):
        capabilities["cuda_tier"] = "cuda13x"
    elif importlib.util.find_spec("cupy_cuda12x"):
        capabilities["cuda_tier"] = "cuda12x"
    elif importlib.util.find_spec("cupy"):
        capabilities["cuda_tier"] = "cuda_toolkit"
    
    # Check RAPIDS
    capabilities["has_cudf"] = importlib.util.find_spec("cudf") is not None
    capabilities["has_cuml"] = importlib.util.find_spec("cuml") is not None
    capabilities["has_cugraph"] = importlib.util.find_spec("cugraph") is not None
    
    # Check Julia
    try:
        import subprocess
        result = subprocess.run(["julia", "--version"], capture_output=True, timeout=5)
        capabilities["has_julia"] = result.returncode == 0
    except Exception:
        capabilities["has_julia"] = False
    
    # Check databases
    capabilities["has_neo4j"] = importlib.util.find_spec("neo4j") is not None
    capabilities["has_qdrant"] = importlib.util.find_spec("qdrant_client") is not None
    
    logger.info(f"System capabilities: {capabilities}")
    return capabilities


def main():
    """Main entry point for SPECTOR CLI."""
    logger.info("Starting SPECTOR v%s", __version__)
    
    # Check capabilities
    caps = check_system_capabilities()
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    SPECTOR v{__version__}                          ║
║  Semantic Pipeline for Entity Correlation and                 ║
║  Topological Organization Research                            ║
╠═══════════════════════════════════════════════════════════════╣
║  System Capabilities:                                          ║
║    Python: {caps['python_version'][:50]:<42} ║
║    CUDA:   {caps['cuda_tier']:<42} ║
║    cuDF:   {str(caps['has_cudf']):<42} ║
║    Julia:  {str(caps['has_julia']):<42} ║
╠═══════════════════════════════════════════════════════════════╣
║  See DISCLAIMER.md for legal framework                        ║
║  See TODO.md for current tasks                                ║
║  See AGENTS.md for AI agent system prompt                     ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
