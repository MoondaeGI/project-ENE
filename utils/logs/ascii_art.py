"""ASCII Art 유틸리티"""
from colorama import Fore, Style


def print_startup_banner():
    """서버 시작 시 ASCII art 배너 출력"""
    banner = f"""
{Fore.GREEN}██████╗{Style.RESET_ALL} {Fore.MAGENTA}███╗   ██╗{Style.RESET_ALL} {Fore.GREEN}██████╗{Style.RESET_ALL}
{Fore.GREEN}██╔═══╝{Style.RESET_ALL} {Fore.MAGENTA}████╗  ██║{Style.RESET_ALL} {Fore.GREEN}██╔═══╝{Style.RESET_ALL}
{Fore.GREEN}█████╗ {Style.RESET_ALL} {Fore.MAGENTA}██╔██╗ ██║{Style.RESET_ALL} {Fore.GREEN}█████╗ {Style.RESET_ALL}
{Fore.GREEN}██╔══╝ {Style.RESET_ALL} {Fore.MAGENTA}██║╚██╗██║{Style.RESET_ALL} {Fore.GREEN}██╔══╝ {Style.RESET_ALL}
{Fore.GREEN}██████╗{Style.RESET_ALL} {Fore.MAGENTA}██║ ╚████║{Style.RESET_ALL} {Fore.GREEN}██████╗{Style.RESET_ALL}
{Fore.GREEN}╚═════╝{Style.RESET_ALL} {Fore.MAGENTA}╚═╝  ╚═══╝{Style.RESET_ALL} {Fore.GREEN}╚═════╝{Style.RESET_ALL}

{Fore.CYAN}     REST API Server with WebSocket{Style.RESET_ALL}
{Fore.CYAN}            Version 0.1.0{Style.RESET_ALL}
"""
    print(banner)

