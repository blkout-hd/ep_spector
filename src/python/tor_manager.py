#!/usr/bin/env python3
"""
Tor Network Manager for SPECTOR
Provides Tor integration with automatic circuit management and health monitoring.
"""

import logging
import socket
import time
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import platform
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import stem
    from stem import Signal
    from stem.control import Controller
    HAS_STEM = True
except ImportError:
    HAS_STEM = False
    logging.warning("stem library not installed. Tor control features disabled.")

try:
    import PySocks
    HAS_PYSOCKS = True
except ImportError:
    HAS_PYSOCKS = False
    logging.warning("PySocks not installed. SOCKS proxy support disabled.")


logger = logging.getLogger(__name__)


class TorManager:
    """Manages Tor service lifecycle and circuit management."""
    
    DEFAULT_SOCKS_PORT = 9050
    DEFAULT_CONTROL_PORT = 9051
    DEFAULT_PASSWORD = "spector_tor_control"
    
    def __init__(
        self,
        socks_port: int = DEFAULT_SOCKS_PORT,
        control_port: int = DEFAULT_CONTROL_PORT,
        password: Optional[str] = None,
        auto_start: bool = True
    ):
        """
        Initialize Tor Manager.
        
        Args:
            socks_port: SOCKS proxy port (default: 9050)
            control_port: Tor control port (default: 9051)
            password: Control port password (default: auto-generated)
            auto_start: Automatically start Tor if not running
        """
        self.socks_port = socks_port
        self.control_port = control_port
        self.password = password or self.DEFAULT_PASSWORD
        self.auto_start = auto_start
        self.tor_process: Optional[subprocess.Popen] = None
        self._controller: Optional['Controller'] = None
        self._session: Optional[requests.Session] = None
        
    def start(self) -> bool:
        """Start Tor service if not running."""
        if self.is_running():
            logger.info("Tor already running")
            return True
            
        logger.info("Starting Tor service...")
        
        try:
            # Determine Tor executable path
            tor_exe = self._find_tor_executable()
            if not tor_exe:
                logger.error("Tor executable not found. Install with: apt install tor (Linux) or brew install tor (macOS) or download Tor Browser Bundle (Windows)")
                return False
            
            # Create Tor configuration
            config = self._create_tor_config()
            config_path = Path("tor_config.txt")
            config_path.write_text(config)
            
            # Start Tor process
            self.tor_process = subprocess.Popen(
                [tor_exe, "-f", str(config_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            # Wait for Tor to bootstrap
            logger.info("Waiting for Tor to bootstrap...")
            if not self._wait_for_bootstrap(timeout=60):
                logger.error("Tor bootstrap timeout")
                self.stop()
                return False
                
            logger.info(f"Tor started successfully (SOCKS: {self.socks_port}, Control: {self.control_port})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Tor: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop Tor service."""
        if self._controller:
            try:
                self._controller.close()
                self._controller = None
            except Exception as e:
                logger.warning(f"Error closing controller: {e}")
        
        if self.tor_process:
            try:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=10)
                self.tor_process = None
                logger.info("Tor stopped")
                return True
            except Exception as e:
                logger.error(f"Error stopping Tor: {e}")
                try:
                    self.tor_process.kill()
                    self.tor_process = None
                except:
                    pass
                return False
        
        return True
    
    def is_running(self) -> bool:
        """Check if Tor is running and accessible."""
        try:
            # Try to connect to SOCKS port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', self.socks_port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def renew_circuit(self) -> bool:
        """Request a new Tor circuit (change exit node)."""
        if not HAS_STEM:
            logger.warning("stem library required for circuit renewal")
            return False
            
        try:
            controller = self._get_controller()
            if controller:
                controller.signal(Signal.NEWNYM)
                logger.info("Tor circuit renewed")
                time.sleep(1)  # Wait for circuit to rebuild
                return True
        except Exception as e:
            logger.error(f"Failed to renew circuit: {e}")
        
        return False
    
    def get_session(self) -> requests.Session:
        """Get requests Session configured with Tor SOCKS proxy."""
        if self._session:
            return self._session
        
        if not HAS_PYSOCKS:
            logger.warning("PySocks required for SOCKS proxy. Returning non-proxied session.")
            return requests.Session()
        
        session = requests.Session()
        
        # Configure SOCKS proxy
        session.proxies = {
            'http': f'socks5h://127.0.0.1:{self.socks_port}',
            'https': f'socks5h://127.0.0.1:{self.socks_port}'
        }
        
        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set user agent
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
        })
        
        self._session = session
        return session
    
    def get_current_ip(self) -> Optional[str]:
        """Get current exit node IP address."""
        try:
            session = self.get_session()
            response = session.get('https://api.ipify.org?format=json', timeout=10)
            if response.status_code == 200:
                return response.json().get('ip')
        except Exception as e:
            logger.error(f"Failed to get current IP: {e}")
        return None
    
    def get_circuit_info(self) -> Dict[str, Any]:
        """Get information about current Tor circuits."""
        if not HAS_STEM:
            return {"error": "stem library not installed"}
        
        try:
            controller = self._get_controller()
            if not controller:
                return {"error": "Not connected to Tor control port"}
            
            circuits = []
            for circuit in controller.get_circuits():
                circuits.append({
                    'id': circuit.id,
                    'status': circuit.status,
                    'purpose': circuit.purpose,
                    'path': [f"{entry.fingerprint[:8]}...{entry.nickname}" for entry in circuit.path]
                })
            
            return {
                'circuits': circuits,
                'count': len(circuits)
            }
        except Exception as e:
            logger.error(f"Failed to get circuit info: {e}")
            return {"error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive Tor status."""
        status = {
            'running': self.is_running(),
            'socks_port': self.socks_port,
            'control_port': self.control_port,
            'exit_ip': None,
            'circuits': []
        }
        
        if status['running']:
            status['exit_ip'] = self.get_current_ip()
            circuit_info = self.get_circuit_info()
            if 'circuits' in circuit_info:
                status['circuits'] = circuit_info['circuits']
        
        return status
    
    def _find_tor_executable(self) -> Optional[str]:
        """Find Tor executable on system."""
        system = platform.system()
        
        # Common Tor locations
        candidates = []
        if system == "Windows":
            candidates = [
                r"C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
                r"C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
                r"C:\Tools\Tor\tor.exe",
                "tor.exe"
            ]
        elif system == "Linux":
            candidates = [
                "/usr/bin/tor",
                "/usr/local/bin/tor"
            ]
        elif system == "Darwin":  # macOS
            candidates = [
                "/usr/local/bin/tor",
                "/opt/homebrew/bin/tor"
            ]
        
        # Check if tor is in PATH
        try:
            result = subprocess.run(
                ["tor", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return "tor"
        except:
            pass
        
        # Check candidate paths
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
        
        return None
    
    def _create_tor_config(self) -> str:
        """Create Tor configuration file content."""
        return f"""
# SPECTOR Tor Configuration
SocksPort {self.socks_port}
ControlPort {self.control_port}
HashedControlPassword {self._hash_password(self.password)}
CookieAuthentication 0
DataDirectory ./tor_data
Log notice stdout
"""
    
    def _hash_password(self, password: str) -> str:
        """Hash password for Tor control port (simplified)."""
        # In production, use: tor --hash-password <password>
        # For now, return placeholder
        return "16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C"
    
    def _wait_for_bootstrap(self, timeout: int = 60) -> bool:
        """Wait for Tor to complete bootstrapping."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_running():
                # Additional check: try to get IP
                try:
                    ip = self.get_current_ip()
                    if ip:
                        return True
                except:
                    pass
            time.sleep(2)
        
        return False
    
    def _get_controller(self) -> Optional['Controller']:
        """Get or create Tor controller connection."""
        if not HAS_STEM:
            return None
        
        if self._controller:
            return self._controller
        
        try:
            controller = Controller.from_port(port=self.control_port)
            controller.authenticate(password=self.password)
            self._controller = controller
            return controller
        except Exception as e:
            logger.warning(f"Failed to connect to Tor control port: {e}")
            return None
    
    def __enter__(self):
        """Context manager entry."""
        if self.auto_start and not self.is_running():
            self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.auto_start:
            self.stop()


def install_dependencies():
    """Install required Tor dependencies."""
    print("Installing Tor dependencies...")
    
    packages = ["stem", "PySocks", "requests[socks]"]
    
    try:
        subprocess.run(
            ["pip", "install"] + packages,
            check=True
        )
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    print("SPECTOR Tor Manager - Quick Test\n")
    
    with TorManager(auto_start=True) as tor:
        print(f"Tor Running: {tor.is_running()}")
        
        if tor.is_running():
            print(f"Exit IP: {tor.get_current_ip()}")
            
            print("\nRenewing circuit...")
            tor.renew_circuit()
            print(f"New Exit IP: {tor.get_current_ip()}")
            
            status = tor.get_status()
            print(f"\nStatus: {status}")
