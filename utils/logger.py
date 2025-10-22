import logging
import colorlog
from datetime import datetime
import json
import os
import sys

class BacklinkLogger:
    """Custom logger for backlink automation"""
    
    def __init__(self, log_file='backlink_automation.log'):
        self.log_file = log_file
        self.results = []
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup colorful console and file logging"""
        # Fix Windows encoding issues
        if sys.platform == 'win32':
            # Force UTF-8 encoding for Windows console
            if hasattr(sys.stdout, 'reconfigure'):
                try:
                    sys.stdout.reconfigure(encoding='utf-8')
                except:
                    pass
        
        # Console handler with colors
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        ))
        
        # File handler with UTF-8 encoding
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        
        # Setup logger
        self.logger = logging.getLogger('BacklinkAutomator')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def _safe_print(self, message):
        """Safely print message, removing emojis on Windows if needed"""
        if sys.platform == 'win32':
            # Remove emojis for Windows console
            emoji_map = {
                '🚀': '[START]',
                '📊': '[REPORT]',
                '✅': '[DONE]',
                '✓': '[OK]',
                '✗': '[FAIL]',
                '⚠': '[WARN]',
                '📸': '[SCREENSHOT]',
                '⏳': '[WAIT]',
                '🧪': '[TEST]',
                '🎉': '[SUCCESS]',
                '⊘': '[SKIP]',
            }
            for emoji, replacement in emoji_map.items():
                message = message.replace(emoji, replacement)
        return message
    
    def info(self, message):
        """Log info message"""
        safe_message = self._safe_print(message)
        self.logger.info(safe_message)
    
    def error(self, message):
        """Log error message"""
        safe_message = self._safe_print(message)
        self.logger.error(safe_message)
    
    def warning(self, message):
        """Log warning message"""
        safe_message = self._safe_print(message)
        self.logger.warning(safe_message)
    
    def success(self, message):
        """Log success message"""
        if sys.platform == 'win32':
            self.logger.info(f"[OK] {message}")
        else:
            self.logger.info(f"✓ {message}")
    
    def failure(self, message):
        """Log failure message"""
        if sys.platform == 'win32':
            self.logger.error(f"[FAIL] {message}")
        else:
            self.logger.error(f"✗ {message}")
    
    def log_site_result(self, site_name, domain, status, profile_url=None, error=None):
        """Log result for a specific site"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'site_name': site_name,
            'domain': domain,
            'status': status,  # 'success', 'failed', 'skipped'
            'profile_url': profile_url,
            'error': error
        }
        self.results.append(result)
        
        if status == 'success':
            self.success(f"{site_name}: Profile created - {profile_url}")
        elif status == 'failed':
            self.failure(f"{site_name}: {error}")
        else:
            self.warning(f"{site_name}: Skipped - {error}")
    
    def generate_report(self, output_file='backlink_report.json'):
        """Generate JSON report of all results"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_sites': len(self.results),
            'successful': len([r for r in self.results if r['status'] == 'success']),
            'failed': len([r for r in self.results if r['status'] == 'failed']),
            'skipped': len([r for r in self.results if r['status'] == 'skipped']),
            'results': self.results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        self.info(f"Report saved to {output_file}")
        return report
    
    def print_summary(self):
        """Print summary of results"""
        successful = [r for r in self.results if r['status'] == 'success']
        failed = [r for r in self.results if r['status'] == 'failed']
        skipped = [r for r in self.results if r['status'] == 'skipped']
        
        print("\n" + "="*60)
        print("AUTOMATION SUMMARY")
        print("="*60)
        print(f"Total Sites Processed: {len(self.results)}")
        
        if sys.platform == 'win32':
            print(f"[OK] Successful: {len(successful)}")
            print(f"[FAIL] Failed: {len(failed)}")
            print(f"[SKIP] Skipped: {len(skipped)}")
        else:
            print(f"✓ Successful: {len(successful)}")
            print(f"✗ Failed: {len(failed)}")
            print(f"⊘ Skipped: {len(skipped)}")
        
        print("="*60)
        
        if successful:
            if sys.platform == 'win32':
                print("\n[OK] SUCCESSFUL BACKLINKS:")
            else:
                print("\n✓ SUCCESSFUL BACKLINKS:")
            for result in successful:
                print(f"  • {result['site_name']}: {result['profile_url']}")
        
        if failed:
            if sys.platform == 'win32':
                print("\n[FAIL] FAILED SITES:")
            else:
                print("\n✗ FAILED SITES:")
            for result in failed:
                print(f"  • {result['site_name']}: {result['error']}")