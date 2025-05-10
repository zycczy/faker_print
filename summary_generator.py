#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
summary_
"""

import os
import json
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

logger = logging.getLogger(__name__)


class SummaryGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.summary_txt_path = os.path.join(output_dir, 'summary.txt')
        self.summary_img_path = os.path.join(output_dir, 'summary.png')
        
    def generate(self, processed_layers, total_height, error_count=0, elapsed_time=0, terminated_early=False):

        try:            # text
            self._generate_text_summary(processed_layers, total_height, error_count, elapsed_time, terminated_early)
            
            # table
            self._generate_chart_summary(total_height, processed_layers, error_count)
            
            logger.info(f"Report generated: {self.summary_txt_path}")
            return True
        except Exception as e:
            logger.error(f"Generate error: {e}")
            return False
    def _generate_text_summary(self, processed_layers, total_height, error_count, elapsed_time, terminated_early):
        with open(self.summary_txt_path, 'w', encoding='utf-8') as f:
            f.write("# FakePrinter Print Task Summary Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 40 + "\n\n")
            
            f.write("## Print Task Information\n")
            f.write(f"- Output Directory: {self.output_dir}\n")              # Statistics
            f.write("\n## Statistics\n")
            f.write(f"- Processed Layers: {processed_layers}\n")
            f.write(f"- Total Height: {total_height:.2f} mm\n")
            if processed_layers > 0:
                f.write(f"- Average Layer Thickness: {total_height / processed_layers:.4f} mm\n")
            
            # Error statistics
            f.write(f"- Error Count: {error_count}\n")
            if error_count > 0:
                f.write(f"- Error Rate: {(error_count / processed_layers * 100):.2f}%\n")
              # Error information
            f.write("\n## Error Statistics\n")
            f.write(f"- Encountered Errors: {error_count}\n")
            if terminated_early:
                f.write("- Status: Print terminated early\n")
            else:
                f.write("- Status: Print completed normally\n")
                
            # Performance statistics
            f.write("\n## Performance Statistics\n")
            f.write(f"- Total Processing Time: {elapsed_time:.2f} seconds\n")
            if elapsed_time > 0 and processed_layers > 0:
                f.write(f"- Average Processing Time Per Layer: {(elapsed_time / processed_layers) * 1000:.2f} milliseconds\n")
                
            # Summary chart
            f.write("\n## Visual Summary\n")
            f.write(f"- Chart File: {os.path.basename(self.summary_img_path)}\n")
    def _generate_chart_summary(self, total_height, processed_layers, error_count):
        try:
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Create subplot 1: Print height
            plt.subplot(1, 2, 1)            
            plt.bar(['Total Height (mm)'], [total_height], color='blue')
            plt.title('Print Model Total Height')
            plt.ylabel('Height (mm)')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            plt.subplot(1, 2, 2)
            plt.bar(['Processed Layers', 'Error Count'], [processed_layers, error_count], color=['green', 'red'])
            plt.title('Layer Processing Stats')
            plt.ylabel('Count')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            plt.suptitle('FakePrinter Print Task Summary', fontsize=16)
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            
            plt.savefig(self.summary_img_path, dpi=120)
            plt.close()
            logger.info(f"Summary chart saved: {self.summary_img_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating summary chart: {e}")
            return False
