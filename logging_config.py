"""
日志配置模块
统一管理应用的日志配置
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
import os


class LoggingConfig:
    """日志配置类"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 日志文件配置
        self.log_files = {
            "main": {
                "filename": "doudizhu_api.log",
                "max_bytes": 10 * 1024 * 1024,  # 10MB
                "backup_count": 5,
                "level": logging.INFO
            },
            "error": {
                "filename": "doudizhu_error.log", 
                "max_bytes": 5 * 1024 * 1024,   # 5MB
                "backup_count": 3,
                "level": logging.ERROR
            },
            "game": {
                "filename": "doudizhu_game.log",
                "max_bytes": 20 * 1024 * 1024,  # 20MB
                "backup_count": 5,
                "level": logging.INFO
            }
        }
        
        # 日志格式
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.date_format = '%Y-%m-%d %H:%M:%S'
    
    def setup_logging(self):
        """配置日志系统"""
        # 创建根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # 清除现有的处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 创建格式化器
        formatter = logging.Formatter(self.log_format, self.date_format)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # 文件处理器
        for log_type, config in self.log_files.items():
            file_handler = RotatingFileHandler(
                filename=self.log_dir / config["filename"],
                maxBytes=config["max_bytes"],
                backupCount=config["backup_count"],
                encoding='utf-8'
            )
            file_handler.setLevel(config["level"])
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        return root_logger
    
    def get_game_logger(self):
        """获取游戏专用日志记录器"""
        game_logger = logging.getLogger("game")
        
        # 如果还没有配置游戏日志处理器
        if not any(isinstance(h, RotatingFileHandler) and 
                  "doudizhu_game.log" in str(h.baseFilename) 
                  for h in game_logger.handlers):
            
            formatter = logging.Formatter(self.log_format, self.date_format)
            
            game_handler = RotatingFileHandler(
                filename=self.log_dir / self.log_files["game"]["filename"],
                maxBytes=self.log_files["game"]["max_bytes"],
                backupCount=self.log_files["game"]["backup_count"],
                encoding='utf-8'
            )
            game_handler.setLevel(self.log_files["game"]["level"])
            game_handler.setFormatter(formatter)
            game_logger.addHandler(game_handler)
        
        return game_logger
    
    def get_log_stats(self):
        """获取日志文件统计信息"""
        stats = {
            "log_directory": str(self.log_dir.absolute()),
            "files": [],
            "total_size": 0
        }
        
        if self.log_dir.exists():
            for log_file in self.log_dir.glob("*.log*"):
                file_stat = log_file.stat()
                file_info = {
                    "filename": log_file.name,
                    "size": file_stat.st_size,
                    "size_mb": round(file_stat.st_size / 1024 / 1024, 2),
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat()
                }
                stats["files"].append(file_info)
                stats["total_size"] += file_stat.st_size
        
        stats["total_size_mb"] = round(stats["total_size"] / 1024 / 1024, 2)
        stats["files"] = sorted(stats["files"], key=lambda x: x["modified"], reverse=True)
        
        return stats
    
    def cleanup_old_logs(self, days: int = 30):
        """清理超过指定天数的日志文件"""
        if not self.log_dir.exists():
            return
        
        import time
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 3600)  # days转换为秒
        
        cleaned_files = []
        
        for log_file in self.log_dir.glob("*.log.*"):  # 只清理轮转的备份文件
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    cleaned_files.append(log_file.name)
                except Exception as e:
                    logging.error(f"清理日志文件失败 {log_file}: {e}")
        
        if cleaned_files:
            logging.info(f"清理了 {len(cleaned_files)} 个过期日志文件: {cleaned_files}")
        
        return cleaned_files


# 全局日志配置实例
logging_config = LoggingConfig() 