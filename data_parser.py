#!/usr/bin/env python

"""
Data Parser Module
Responsible for reading and parsing print layer data sets (CSV files)
"""

import csv
import logging
import os
import requests
from io import BytesIO


logger = logging.getLogger(__name__)


class DataParser:  
    def __init__(self, csv_file_path):

        self.csv_file_path = csv_file_path
        self.total_lines = self._count_lines()
        self.headers = []
        
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"cannot find: {csv_file_path}")
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                self.headers = next(reader)
                logger.info(f"file header: {self.headers}")
        except Exception as e:
            raise
            
    def _count_lines(self):
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f) - 1 
        except Exception as e:
            return -1
            
    def get_estimated_total_layers(self):
        return self.total_lines
        
    def parse(self):
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                next(reader)  
                
                for row_idx, row in enumerate(reader, 1):
                    try:
                        layer_data = {}
                        
                        if len(row) != len(self.headers):
                            raise ValueError(f"not match")
                        
                        for i, field_name in enumerate(self.headers):
                            field_key = field_name.lower().replace(' ', '_')
                            layer_data[field_key] = row[i]
                        
                        if 'layer_number' in layer_data:
                            layer_data['layer_id'] = layer_data['layer_number']
                        else:
                            layer_data['layer_id'] = row_idx
                            
                        if 'layer_height' in layer_data:
                            try:
                                layer_data['height'] = float(layer_data['layer_height'])
                            except ValueError:
                                logger.warning(f"{layer_data['layer_id']} error: {layer_data['layer_height']}")
                        
                        if 'image_url' in layer_data:
                            layer_data['image_data'] = layer_data['image_url']
                        
                        if 'layer_error' in layer_data and layer_data['layer_error'] != 'SUCCESS':
                            layer_data['has_error'] = True
                            layer_data['error_type'] = layer_data['layer_error']
                                
                        self._validate_layer_data(layer_data, row_idx)
                            
                        yield layer_data
                        
                    except Exception as e:
                        layer_data = {
                            'layer_id': row_idx,
                            'error': str(e),
                            'row_data': row,
                            'has_error': True
                        }
                        yield layer_data
                        
        except Exception as e:
            logger.error(f"read csv error: {e}")
            raise
            
    def _validate_layer_data(self, layer_data, row_idx):
        required_fields = ['layer_id']
        for field in required_fields:
            if field not in layer_data or not layer_data[field]:
                raise ValueError(f"field error: {field}")
                
        if 'height' in layer_data:
            if not isinstance(layer_data['height'], (int, float)):
                raise ValueError(f"height error: {layer_data['height']}")
                
        if 'image_url' not in layer_data and 'image_data' not in layer_data:
            logger.warning(f"{layer_data['layer_id']} not image data")
