"""로그 포맷터 모듈"""
import logging
from colorama import init, Fore, Style

# colorama 초기화
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """색상이 적용된 로그 포맷터"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        # 로그 레벨에 따라 색상 적용
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        
        # 메시지 내용에 특수 문자에 따라 색상 적용
        message = record.getMessage()
        if '✓' in message:
            # 성공 메시지는 초록색
            message = message.replace('✓', f'{Fore.GREEN}✓{Style.RESET_ALL}')
        elif '⚠' in message:
            # 경고 메시지는 노란색
            message = message.replace('⚠', f'{Fore.YELLOW}⚠{Style.RESET_ALL}')
        elif '✗' in message:
            # 에러 메시지는 빨간색
            message = message.replace('✗', f'{Fore.RED}✗{Style.RESET_ALL}')
        
        record.msg = message
        record.args = ()
        
        return super().format(record)

