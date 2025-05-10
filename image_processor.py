#!/usr/bin/env python
"""
image_processor.py
"""

import os
import base64
import logging
import requests
from io import BytesIO
from PIL import Image
import uuid
import time

logger = logging.getLogger(__name__)


class ImageProcessor:
    
    @staticmethod
    def decode_image(image_data, image_format='png'):
        if not image_data:
            return None
            
        try:
            if image_data.startswith(('http://', 'https://')):
                return ImageProcessor.download_image(image_data)

        except Exception as e:
            logger.error(f"decode error: {e}")
            return None
            
    @staticmethod
    def download_image(url, max_retries=3, retry_delay=1):
        if not url:
            return None
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()  
                
                image = Image.open(BytesIO(response.content))
                logger.info(f"download success: {url}")
                return image
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"download error (try {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(f"downlaod fail: {url}")
                    return None
            except Exception as e:
                logger.error(f"prcess fail: {e}")
                return None
    
    @staticmethod
    def save_image(image, output_path, image_format='png'):
        if image is None:
            return False
            
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            image.save(output_path, format=image_format)
            logger.debug(f"image save as: {output_path}")
            return True
        except Exception as e:
            logger.error(f"image save error: {e}")
            return False
    
    @staticmethod
    def process_layer_image(layer_data, output_dir, layer_id):
        image_data = None
        image_filename = None
        
        if 'file_name' in layer_data and layer_data['file_name']:
            image_filename = layer_data['file_name']
        
        image_field_names = ['image_url', 'image_data', 'image', 'imagedata', 'img']
        for field_name in image_field_names:
            if field_name in layer_data and layer_data[field_name]:
                image_data = layer_data[field_name]
                break
                
        if not image_data:
            logger.warning(f"layer {layer_id} not found")
            return None
            
        if not image_filename:
            image_filename = f"layer_{str(layer_id).zfill(6)}.png"
        
        image_path = os.path.join(output_dir, image_filename)
        
        image = ImageProcessor.decode_image(image_data)
        if image and ImageProcessor.save_image(image, image_path):
            return image_path
        else:
            logger.error(f"process {layer_id} fail")
            return None
