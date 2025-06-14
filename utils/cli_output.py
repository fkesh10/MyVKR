# cli_output.py

from colorama import Fore, Style, init
import json

init(autoreset=True)

def print_banner():
    banner = f"""{Fore.CYAN}
    SSTI Penetration Testing Framework
    {Style.RESET_ALL}"""
    print(banner)

def print_info(message):
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {message}")

def print_warning(message):
    print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")

def print_success(message):
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}")

def print_verbose(results):
    print(f"{Fore.MAGENTA}[VERBOSE OUTPUT]{Style.RESET_ALL}")
    print(json.dumps(results, indent=4, ensure_ascii=False))

def print_summary(results):
    print(f"{Fore.CYAN}[SUMMARY]{Style.RESET_ALL}")
    url = results.get("url")
    engine = results["steps"].get("detector", {}).get("engine", "Unknown")
    points = results["steps"].get("finder", [])
    exploits = results["steps"].get("injector", [])

    print(f"Target URL: {url}")
    print(f"Detected Template Engine: {engine}")
    print(f"Injection Points Found: {len(points)}")
    print(f"Exploits Performed: {len(exploits)}")
