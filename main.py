#!/usr/bin/env python
"""
FakePrinter - A simulator for 3D printing processes
"""

import os
import argparse
import logging
import sys
import time
from pathlib import Path

from data_parser import DataParser
from image_processor import ImageProcessor
from output_manager import OutputManager
from error_handler import ErrorHandler
from summary_generator import SummaryGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='FakePrinter - 3D Print Simulator')
    parser.add_argument('print_name', type=str, help='Print job name')
    parser.add_argument('output_folder', type=str, help='Output folder path')
    parser.add_argument('--mode', type=str, default='automatic',
                        choices=['supervised', 'automatic'],
                        help='Run mode: supervised (user confirmation) or automatic')    
    parser.add_argument('--data', type=str, default='fl_coding_challenge_v1.csv',
                        help='Path to the print data CSV file (default: fl_coding_challenge_v1.csv)')
    
    args = parser.parse_args()
    
    try:
        output_dir = Path(args.output_folder)
        if not output_dir.exists():
            logger.info(f"Output directory '{output_dir}' does not exist, creating...")
            output_dir.mkdir(parents=True, exist_ok=True)
        elif not output_dir.is_dir():
            parser.error(f"Specified output path '{output_dir}' is not a directory")    
    except Exception as e:
        parser.error(f"Error creating output directory: {e}")
        
    data_file = Path(args.data)
    if not data_file.exists():
        parser.error(f"Data file '{data_file}' does not exist")
    
    return args


def run_supervised_mode(data_parser, output_manager, error_handler, summary_generator):
    """
    Run in supervised mode - wait for user to press Enter to process each layer
    """
    logger.info("Running in supervised mode. Press Enter to process next layer, 'q' to quit")
    
    total_height = 0
    processed_layers = 0
    error_count = 0
    
    # start
    start_time = time.time()
    try:        # Process layer by layer
        for layer_data in data_parser.parse():
            # wait for user input
            user_input = input(f"\nReady to process layer {layer_data.get('layer_id', processed_layers + 1)}. Press Enter to continue, 'q' to quit: ")
            if user_input.lower() == 'q':
                logger.info("User manually terminated processing")
                break
            try:
                has_predefined_error = False
                if 'layer_error' in layer_data and layer_data['layer_error'] != 'SUCCESS':
                    has_predefined_error = True
                    error_msg = f"layer {layer_data.get('layer_id')} error: {layer_data['layer_error']}"
                    choice = error_handler.handle_error(error_msg, layer_data)
                    if choice == 'end':
                        logger.info("stop")
                        break

                image_path = None
                if ('image_data' in layer_data and layer_data['image_data']) or ('image_url' in layer_data and layer_data['image_url']):
                    image_path = output_manager.process_image(layer_data)
                
                output_manager.output_layer(layer_data, image_path)
                
                if 'height' in layer_data:
                    total_height += float(layer_data['height'])
                elif 'layer_height' in layer_data:
                    total_height += float(layer_data['layer_height'])
                    
                processed_layers += 1
                logger.info(f" {layer_data.get('layer_id', processed_layers)} finish")
                
                if has_predefined_error:
                    error_count += 1
                
            except Exception as e:
                error_count += 1
                # ask user, continue or not
                choice = error_handler.handle_error(
                    f"layer {layer_data.get('layer_id', processed_layers + 1)} error: {str(e)}",
                    layer_data
                )
                
                if choice == 'end':
                    logger.info("end print")
                    break
    except Exception as e:
        logger.error(f"error: {e}")
        return False
        
    elapsed_time = time.time() - start_time
    
    summary_generator.generate(
        processed_layers=processed_layers, 
        total_height=total_height,
        error_count=error_count,
        elapsed_time=elapsed_time,
        terminated_early=(processed_layers < data_parser.get_estimated_total_layers())
    )
    
    return True


def run_automatic_mode(data_parser, output_manager, error_handler, summary_generator):
    """
    auto mode
    """
    logger.info("start auto mode")
    
    total_height = 0
    processed_layers = 0
    error_count = 0
    
    start_time = time.time()
    
    try:
        for layer_data in data_parser.parse():
            try:
                has_predefined_error = False
                if 'layer_error' in layer_data and layer_data['layer_error'] != 'SUCCESS':
                    has_predefined_error = True
                    error_msg = f"layer {layer_data.get('layer_id')} error: {layer_data['layer_error']}"
                    error_handler.handle_error(error_msg, layer_data, automatic=True)
                
                image_path = None
                if ('image_data' in layer_data and layer_data['image_data']) or ('image_url' in layer_data and layer_data['image_url']):
                    image_path = output_manager.process_image(layer_data)
                
                output_manager.output_layer(layer_data, image_path)
                
                if 'height' in layer_data:
                    total_height += float(layer_data['height'])
                elif 'layer_height' in layer_data:
                    total_height += float(layer_data['layer_height'])
                    
                processed_layers += 1
                
                if processed_layers % 100 == 0:
                    logger.info(f"already {processed_layers} done...")
                
                if has_predefined_error:
                    error_count += 1
                
            except Exception as e:
                error_count += 1
                error_handler.handle_error(
                    f"process {layer_data.get('layer_id', processed_layers + 1)} error: {str(e)}",
                    layer_data,
                    automatic=True
                )
    except Exception as e:
        logger.error(f"error: {e}")
        return False
        
    elapsed_time = time.time() - start_time
    
    summary_generator.generate(
        processed_layers=processed_layers, 
        total_height=total_height,
        error_count=error_count,
        elapsed_time=elapsed_time,
        terminated_early=False
    )
    
    return True


def main():
    args = parse_arguments()
    
    print(f"\n===== FakePrinter =====")
    print(f"task name: {args.print_name}")
    print(f"output path: {args.output_folder}")
    print(f"mode: {args.mode}")
    print(f"data file: {args.data}")
    print(f"==============================\n")
    
    print_dir = os.path.join(args.output_folder, args.print_name)
    os.makedirs(print_dir, exist_ok=True)
    
    images_dir = os.path.join(print_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    error_log_path = os.path.join(print_dir, "error.log")
    
    data_parser = DataParser(args.data)
    output_manager = OutputManager(print_dir, images_dir, args.print_name)
    error_handler = ErrorHandler(error_log_path)
    summary_generator = SummaryGenerator(print_dir)
    
    success = False
    if args.mode == 'supervised':
        success = run_supervised_mode(data_parser, output_manager, error_handler, summary_generator)
    else:  # automatic mode
        success = run_automatic_mode(data_parser, output_manager, error_handler, summary_generator)
    
    if success:
        logger.info(f"task '{args.print_name}' finished，store in '{print_dir}'")
    else:
        logger.error(f"task '{args.print_name}' fail")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
