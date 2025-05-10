#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具函数模块
提供各种辅助函数
"""

import os
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_dir(dir_path):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        dir_path: 目录路径
        
    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录 {dir_path} 时出错: {e}")
        return False
        
        
def format_time(seconds):
    """
    将秒数格式化为可读时间字符串
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化后的时间字符串 (hh:mm:ss)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"
        
        
def format_file_size(size_bytes):
    """
    将字节大小格式化为可读大小字符串
    
    Args:
        size_bytes: 字节大小
        
    Returns:
        str: 格式化后的大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"
        
        
def get_file_info(file_path):
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        dict: 包含文件信息的字典，或者 None（如果文件不存在）
    """
    try:
        if not os.path.exists(file_path):
            return None
            
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'modified': time.ctime(stat.st_mtime),
            'created': time.ctime(stat.st_ctime),
        }
    except Exception as e:
        logger.error(f"获取文件 {file_path} 信息时出错: {e}")
        return None
        
        
def safe_filename(filename):
    """
    生成安全的文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 安全的文件名
    """
    # 移除非法字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
