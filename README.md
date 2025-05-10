# FakePrinter

A 3D printing simulator that processes print layer data and generates outputs for testing and visualization.

## Overview

FakePrinter is a simulation tool designed to mimic 3D printing processes. It reads print layer data from CSV files, processes them layer by layer, and outputs the results to an organized file system structure.

## Features

- Two operational modes: supervised and automatic
- CSV format print layer data processing with embedded image content
- Well-organized file system output structure
- Supports large-scale data processing (up to 2 million layers)
- Provides statistical summary reports (text and charts)
- Comprehensive error handling system

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Command Format

```bash
python main.py <print_name> <output_folder> [--mode=<supervised|automatic>] [--data=<data_file.csv>]
```

### Parameters

- `print_name`: Name of the print job
- `output_folder`: Path to output directory
- `--mode`: Operation mode, either "supervised" or "automatic" (default: "automatic")
- `--data`: Path to CSV data file (default: "print_data.csv")

### Examples

```bash
# Run in automatic mode
python main.py TestPrint ./output --data=fl_coding_challenge_v1.csv

# Run in supervised mode
python main.py TestPrint ./output --mode=supervised --data=fl_coding_challenge_v1.csv
```

## Output Structure

FakePrinter generates the following output structure:

```
output/
└─ PrintName/
   ├─ layers.csv            # Summary of layer data records
   ├─ layers.json           # Layer data in JSON format
   ├─ images/               # Directory for image files
   │   ├─ 000001-001000/    # Images grouped by batch
   │   │   ├─ fl_layer_200000.png
   │   │   ├─ fl_layer_200001.png
   │   │   └─ ...
   │   └─ ...
   └─ error.log             # Error log file
```

## Operating Modes

### Supervised Mode

- Waits for user confirmation after processing each layer
- Prompts user to ignore or terminate on errors
- Ideal for debugging and testing

### Automatic Mode

- Processes all layers automatically without user intervention
- Logs errors and continues processing subsequent layers
- Suitable for batch processing or unattended operation

## Project Structure

- `main.py` - Main entry point
- `data_parser.py` - Data parsing module
- `image_processor.py` - Image processing module
- `output_manager.py` - Output management module
- `error_handler.py` - Error handling module
- `summary_generator.py` - Statistics and summary module
- `utils.py` - Utility functions
