#!/usr/bin/env python3
"""
SPECTOR CLI Launcher with AI Provider Selection

Automatically detects and configures AI providers for agent orchestration.
Supports: Gemini CLI, Qwen CLI, Claude Code, Copilot, Codex, Ollama, and more.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Supported AI providers configuration
SUPPORTED_PROVIDERS = {
    "gemini-cli": {
        "name": "Google Gemini CLI",
        "command": "gemini",
        "check": ["gemini", "--version"],
        "install": "pip install google-generativeai-cli",
        "free": True,
        "env_var": "GOOGLE_API_KEY"
    },
    "qwen-cli": {
        "name": "Alibaba Qwen CLI",
        "command": "qwen",
        "check": ["qwen", "--version"],
        "install": "pip install qwen-cli",
        "free": True,
        "env_var": "QWEN_API_KEY"
    },
    "claude-code": {
        "name": "Anthropic Claude Code",
        "command": "claude",
        "check": ["claude", "--version"],
        "install": "See https://docs.anthropic.com/claude/docs/claude-cli",
        "free": False,
        "env_var": "ANTHROPIC_API_KEY"
    },
    "copilot-cli": {
        "name": "GitHub Copilot CLI",
        "command": "gh-copilot",
        "check": ["gh", "copilot", "--version"],
        "install": "gh extension install github/gh-copilot",
        "free": False,
        "env_var": None
    },
    "codex": {
        "name": "OpenAI Codex",
        "command": "codex",
        "check": ["codex", "--version"],
        "install": "pip install openai-codex-cli",
        "free": False,
        "env_var": "OPENAI_API_KEY"
    },
    "ollama": {
        "name": "Ollama (Local Models)",
        "command": "ollama",
        "check": ["ollama", "--version"],
        "install": "https://ollama.ai/download",
        "free": True,
        "env_var": None
    },
    "lm-studio": {
        "name": "LM Studio (Local Models)",
        "command": "lms",
        "check": ["lms", "status"],
        "install": "https://lmstudio.ai/",
        "free": True,
        "env_var": None
    }
}


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def is_command_available(command: List[str]) -> bool:
    """Check if a command is available."""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        return False


def check_env_var(env_var: Optional[str]) -> bool:
    """Check if environment variable is set."""
    if env_var is None:
        return True  # No env var required
    return bool(os.getenv(env_var))


def detect_available_providers() -> Dict[str, bool]:
    """Detect which AI providers are installed and configured."""
    available = {}
    
    for provider_id, config in SUPPORTED_PROVIDERS.items():
        is_installed = is_command_available(config["check"])
        has_api_key = check_env_var(config.get("env_var"))
        available[provider_id] = is_installed and has_api_key
    
    return available


def print_provider_status():
    """Print status of all providers."""
    print_header("AI Provider Detection")
    
    available_providers = detect_available_providers()
    
    free_providers = []
    paid_providers = []
    
    for provider_id, config in SUPPORTED_PROVIDERS.items():
        is_available = available_providers[provider_id]
        status_icon = "✓" if is_available else "✗"
        status_color = Colors.OKGREEN if is_available else Colors.FAIL
        free_icon = "🆓" if config["free"] else "💰"
        
        provider_list = free_providers if config["free"] else paid_providers
        provider_list.append((provider_id, config, is_available))
        
        print(f"{status_color}{status_icon}{Colors.ENDC} {free_icon} {config['name']}")
        
        if not is_available:
            if config.get("env_var") and not check_env_var(config["env_var"]):
                print(f"     {Colors.WARNING}Missing: {config['env_var']}{Colors.ENDC}")
            if not is_command_available(config["check"]):
                print(f"     {Colors.WARNING}Install: {config['install']}{Colors.ENDC}")
    
    # Summary
    available_count = sum(available_providers.values())
    total_count = len(SUPPORTED_PROVIDERS)
    
    print(f"\n{Colors.BOLD}Available: {available_count}/{total_count} providers{Colors.ENDC}")
    
    return available_providers


def prompt_provider_selection(available_providers: Dict[str, bool]) -> Optional[str]:
    """Interactive provider selection."""
    available_list = [
        (pid, config) 
        for pid, config in SUPPORTED_PROVIDERS.items() 
        if available_providers[pid]
    ]
    
    if not available_list:
        print_error("No AI providers available. Please install at least one.")
        print_info("Recommended for beginners: Ollama (free, local)")
        print_info("  Install: https://ollama.ai/download")
        return None
    
    print("\nAvailable providers:")
    for idx, (provider_id, config) in enumerate(available_list, 1):
        free_icon = "🆓" if config["free"] else "💰"
        print(f"  {idx}. {free_icon} {config['name']}")
    
    while True:
        try:
            choice = input(f"\nSelect provider (1-{len(available_list)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_list):
                selected_provider = available_list[choice_idx][0]
                print_success(f"Selected: {SUPPORTED_PROVIDERS[selected_provider]['name']}")
                return selected_provider
            else:
                print_warning("Invalid selection. Please try again.")
        except (ValueError, KeyboardInterrupt):
            print_warning("\nInvalid input. Please enter a number.")
    
    return None


def configure_provider_env(provider_id: str):
    """Configure environment for selected provider."""
    config = SUPPORTED_PROVIDERS[provider_id]
    
    # Set environment variable for subprocess
    if config.get("env_var"):
        api_key = os.getenv(config["env_var"])
        if api_key:
            print_success(f"{config['env_var']} is set")
        else:
            print_warning(f"{config['env_var']} not found in environment")
            print_info(f"Set it in your .env file or export it:")
            print_info(f"  export {config['env_var']}=your-api-key-here")
    
    return True


def launch_spector(provider: Optional[str] = None, spector_args: List[str] = None):
    """Launch SPECTOR with selected provider."""
    if spector_args is None:
        spector_args = []
    
    # Add provider to environment if specified
    env = os.environ.copy()
    if provider:
        env["SPECTOR_AI_PROVIDER"] = provider
        print_info(f"Using AI provider: {SUPPORTED_PROVIDERS[provider]['name']}")
    
    # Build command
    cmd = ["spector"] + spector_args
    
    print_info(f"Launching: {' '.join(cmd)}")
    
    try:
        # Launch SPECTOR
        result = subprocess.run(cmd, env=env)
        return result.returncode
    except FileNotFoundError:
        print_error("SPECTOR CLI not found. Make sure it's installed:")
        print_info("  pip install -e .")
        return 1
    except KeyboardInterrupt:
        print_warning("\nInterrupted by user")
        return 130


def launch_admin_console(port: int = 8888, host: str = "localhost"):
    """
    Launch the Tornado admin console.
    
    Args:
        port: Port to run admin console on (default: 8888)
        host: Host to bind to (default: localhost)
    """
    try:
        # Import admin console module
        sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))
        from admin_console import TornadoAdminServer
        
        print_header("SPECTOR Admin Console")
        print_info(f"Starting admin console on http://{host}:{port}")
        print_info("Default credentials: admin / spector")
        
        server = TornadoAdminServer(host=host, port=port)
        server.start()
        return 0
    except ImportError as e:
        print_error(f"Failed to import admin console: {e}")
        print_info("Make sure Tornado is installed: pip install tornado")
        return 1
    except Exception as e:
        print_error(f"Failed to start admin console: {e}")
        return 1


def launch_tor_admin(args):
    """Launch Tornado admin console with Tor integration."""
    print(f"\n{Colors.OKCYAN}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.OKCYAN}║    SPECTOR Tor-Enabled Admin Console                    ║{Colors.ENDC}")
    print(f"{Colors.OKCYAN}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
    
    try:
        from src.python.tor_manager import TorManager
        from src.python.tornado_tor_integration import create_tor_routes
        import tornado.web
        import tornado.ioloop
        
        port = getattr(args, 'port', 8889)
        
        # Initialize Tor
        print(f"{Colors.WARNING}Initializing Tor network...{Colors.ENDC}")
        tor = TorManager(auto_start=True)
        if not tor.start():
            print(f"{Colors.FAIL}✗ Failed to start Tor{Colors.ENDC}")
            return 1
        
        print(f"{Colors.OKGREEN}✓ Tor started successfully{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Exit IP: {tor.get_current_ip()}{Colors.ENDC}\n")
        
        # Create Tornado application
        routes = create_tor_routes(tor)
        routes.append((r"/", tornado.web.RedirectHandler, {"url": "/tor/dashboard"}))
        
        app = tornado.web.Application(
            routes,
            template_path="docs",
            debug=True
        )
        
        app.listen(port)
        print(f"{Colors.OKGREEN}✓ Tornado server started on http://localhost:{port}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Dashboard: http://localhost:{port}/tor/dashboard{Colors.ENDC}\n")
        print(f"{Colors.WARNING}Press Ctrl+C to stop...{Colors.ENDC}\n")
        
        # Start periodic status broadcast
        from src.python.tornado_tor_integration import broadcast_tor_status
        tornado.ioloop.IOLoop.current().spawn_callback(broadcast_tor_status, tor)
        
        # Start event loop
        try:
            tornado.ioloop.IOLoop.current().start()
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Shutting down...{Colors.ENDC}")
            tor.stop()
            return 0
            
    except ImportError as e:
        print(f"{Colors.FAIL}✗ Missing dependencies: {e}{Colors.ENDC}")
        print(f"{Colors.WARNING}Install with: pip install tornado stem PySocks{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SPECTOR CLI Launcher with AI Provider Selection",
        epilog="Example: launcher.py --ai-provider gemini-cli index ./documents"
    )
    
    # Add admin subcommand check
    if len(sys.argv) > 1 and sys.argv[1] == "admin":
        # Parse admin-specific arguments
        admin_parser = argparse.ArgumentParser(description="SPECTOR Admin Console")
        admin_parser.add_argument("admin", help="Admin command")
        admin_parser.add_argument("--port", type=int, default=8888, help="Admin console port")
        admin_parser.add_argument("--host", default="localhost", help="Admin console host")
        admin_args = admin_parser.parse_args()
        return launch_admin_console(port=admin_args.port, host=admin_args.host)
    
    # Add tor-admin subcommand check
    if len(sys.argv) > 1 and sys.argv[1] == "tor-admin":
        # Parse tor-admin-specific arguments
        tor_admin_parser = argparse.ArgumentParser(description="SPECTOR Tor-Enabled Admin Console")
        tor_admin_parser.add_argument("tor-admin", help="Tor admin command")
        tor_admin_parser.add_argument("--port", type=int, default=8889, help="Tor admin console port (default: 8889)")
        tor_admin_args = tor_admin_parser.parse_args()
        return launch_tor_admin(tor_admin_args)
    
    parser = argparse.ArgumentParser(
        description="SPECTOR CLI Launcher with AI Provider Selection",
        epilog="Example: launcher.py --ai-provider gemini-cli index ./documents"
    )
    
    parser.add_argument(
        "--ai-provider",
        choices=list(SUPPORTED_PROVIDERS.keys()),
        help="AI provider to use (auto-detect if not specified)"
    )
    
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List available AI providers and exit"
    )
    
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Skip interactive provider selection"
    )
    
    # Parse known args to allow pass-through to SPECTOR
    args, spector_args = parser.parse_known_args()
    
    # Print header
    print_header("SPECTOR - AI Provider Launcher")
    
    # List providers mode
    if args.list_providers:
        print_provider_status()
        return 0
    
    # Detect providers
    available_providers = detect_available_providers()
    
    # Determine which provider to use
    selected_provider = None
    
    if args.ai_provider:
        # User specified provider via flag
        if available_providers.get(args.ai_provider):
            selected_provider = args.ai_provider
        else:
            print_error(f"Provider '{args.ai_provider}' is not available")
            print_provider_status()
            return 1
    elif not args.no_interactive:
        # Interactive selection
        print_provider_status()
        selected_provider = prompt_provider_selection(available_providers)
        
        if selected_provider is None:
            print_warning("No provider selected. Exiting.")
            return 1
    else:
        # Auto-select first available provider
        for pid, is_available in available_providers.items():
            if is_available:
                selected_provider = pid
                break
        
        if selected_provider:
            print_info(f"Auto-selected: {SUPPORTED_PROVIDERS[selected_provider]['name']}")
        else:
            print_error("No providers available and --no-interactive specified")
            return 1
    
    # Configure provider
    if selected_provider:
        configure_provider_env(selected_provider)
    
    # Launch SPECTOR
    return launch_spector(selected_provider, spector_args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        sys.exit(130)
