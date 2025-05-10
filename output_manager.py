#!/usr/bin/env python

"""
Output Manager Module
Responsible for managing output data to the filesystem
"""

import os
import json
import csv
import logging
import shutil
from pathlib import Path

from image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class OutputManager:
    """
    Output Manager: manages output data to the file system
    """
    
    def __init__(self, output_dir, images_dir, print_name):

        self.output_dir = output_dir
        self.images_dir = images_dir
        self.print_name = print_name
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        self.layers_csv_path = os.path.join(self.output_dir, 'layers.csv')
        self.layers_json_path = os.path.join(self.output_dir, 'layers.json')
        self._init_layers_csv()
        
        # init json
        with open(self.layers_json_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
    def _init_layers_csv(self):
        with open(self.layers_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'layer_id', 'status', 'height', 'material_type', 'extrusion_temperature',
                'print_speed', 'layer_adhesion_quality', 'infill_density', 'infill_pattern',
                'image_file', 'processing_time'
            ])
    
    def process_image(self, layer_data):
        """
        process image
        """
        layer_id = layer_data.get('layer_id', 'unknown')
        
        batch_num = int(int(layer_id) / 1000) if isinstance(layer_id, (int, str)) and str(layer_id).isdigit() else 0
        batch_dir = os.path.join(self.images_dir, f"{batch_num*1000+1:06d}-{(batch_num+1)*1000:06d}")
        os.makedirs(batch_dir, exist_ok=True)
        
        image_filename = None
        if 'file_name' in layer_data and layer_data['file_name']:
            image_filename = layer_data['file_name']
        else:
            image_filename = f"layer_{str(layer_id).zfill(6)}.png"
            
        image_path = os.path.join(batch_dir, image_filename)
        
        # image process
        try:
            image_data = None
            
            if 'image_url' in layer_data and layer_data['image_url']:
                image_data = layer_data['image_url']
            
            if not image_data:
                return None
                
            image = ImageProcessor.decode_image(image_data)
            if image and ImageProcessor.save_image(image, image_path):
                return image_path
            else:
                logger.error(f"layer {layer_id} error")
                return None        
        except Exception as e:
            logger.error(f"layer {layer_id} error: {e}")
            return None
    
    def output_layer(self, layer_data, image_path=None):
        """
        out put to file system
        """
        try:
            # prepare data
            layer_id = layer_data.get('layer_id', 'unknown')
            height = layer_data.get('height', 0)
            status = layer_data.get('layer_error', 'SUCCESS') 
            
            output_data = {k: v for k, v in layer_data.items() if not any(img_field in k.lower() for img_field in ['image_url', 'image', 'img', 'picture'])}
            
            if image_path:
                rel_path = os.path.relpath(image_path, self.output_dir)
                output_data['image_file'] = rel_path
                
            # output csv
            with open(self.layers_csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # info for CSV
                material_type = layer_data.get('material_type', '')
                extrusion_temp = layer_data.get('extrusion_temperature', '')
                print_speed = layer_data.get('print_speed', '')
                adhesion = layer_data.get('layer_adhesion_quality', '')
                infill_density = layer_data.get('infill_density', '')
                infill_pattern = layer_data.get('infill_pattern', '')
                processing_time = layer_data.get('layer_time', '')
                
                # path for csv
                rel_image_path = os.path.relpath(image_path, self.output_dir) if image_path else ''
                
                writer.writerow([
                    layer_id, status, height, material_type, extrusion_temp,
                    print_speed, adhesion, infill_density, infill_pattern,
                    rel_image_path, processing_time
                ])
                
            try:
                with open(self.layers_json_path, 'r+', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []
                    
                    data.append(output_data)
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"write JSON error: {e}")
                
            return True
            
        except Exception as e:
            logger.error(f"output {layer_data.get('layer_id', 'unknown')} error: {e}")
            return False
