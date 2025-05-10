#!/usr/bin/env python

"""
error_handler.py
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorHandler:
    def __init__(self, error_log_path):
        self.error_log_path = error_log_path
        self.error_count = 0
        
        self._init_error_log()
        
    def _init_error_log(self):
        try:
            with open(self.error_log_path, 'w', encoding='utf-8') as f:
                f.write(f"# FakePrinter error log\n")
                f.write(f"# time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("layer id,error type, error description,reslut\n")
                f.write("-" * 80 + "\n")
        except Exception as e:
            logger.error(f"init log error: {e}")
            
    def log_error(self, layer_id, error_type, error_message, action):
        try:
            with open(self.error_log_path, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%H:%M:%S')
                f.write(f"{layer_id},{error_type},{error_message},{action},{timestamp}\n")
        except Exception as e:
            logger.error(f"write log error: {e}")
            
    def handle_error(self, error_message, layer_data, automatic=False):
        self.error_count += 1
        layer_id = layer_data.get('layer_id', 'unknown')
        if 'error_type' in layer_data:
            error_type = layer_data['error_type']
        elif 'layer_error' in layer_data and layer_data['layer_error'] != 'SUCCESS':
            error_type = layer_data['layer_error']
        elif 'height' not in layer_data or not layer_data['height']:
            error_type = 'no hight'
        elif 'image_data' not in layer_data and 'image_url' not in layer_data:
            error_type = 'no image data'
        else:
            error_type = 'image process fail'
            
        if automatic:
            logger.warning(f"[auto mode] {error_message}")
            self.log_error(layer_id, error_type, error_message, 'ignored')
            return 'ignore'
        else:
            print(f"\error: {error_message}")
            print(f"layer {layer_id} error ({error_type})")
            print("\nmode:")
            print("  [I] ignore and skip")
            print("  [E] end print")
            
            while True:
                choice = input("\nplease input [I/E]: ").strip().lower()
                if choice == 'i':
                    self.log_error(layer_id, error_type, error_message, 'ignored')
                    return 'ignore'
                elif choice == 'e':
                    self.log_error(layer_id, error_type, error_message, 'terminated')
                    return 'end'
                else:
                    print("please re-input")
                    
    def get_error_count(self):
        return self.error_count
