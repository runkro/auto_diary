# main.py
import os
import json
import data_parser
import interval_detection
import grouping
import summary_generation
import zones
import utils
import yaml
from datetime import datetime

# --- Configuration ---
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
try:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
        power_interval_config = config.get('power_interval_thresholds', {})
        heart_rate_interval_config = config.get('heart_rate_interval_thresholds', {})
        power_zone_definitions = config.get('power_zones', {})
        heart_rate_zone_definitions = config.get('heart_rate_zones', {})
except FileNotFoundError:
    print(f"Warning: Configuration file '{CONFIG_FILE}' not found. Using default settings.")
    power_interval_config = {}
    heart_rate_interval_config = {}
    power_zone_definitions = {}
    heart_rate_zone_definitions = {}

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')

# Ensure processed data directory exists
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def analyze_workout(file_path):
    """Analyzes a single workout file."""
    filename = os.path.basename(file_path)
    print(f"Analyzing: {filename}")

    data = data_parser.parse_workout_file(file_path)

    if not data:
        print(f"Error: Could not parse data from {filename}.")
        return

    power_data = [(item['timestamp'], item['power']) for item in data if 'power' in item and item['power'] is not None]
    heart_rate_data = [(item['timestamp'], item['heart_rate']) for item in data if 'heart_rate' in item and item['heart_rate'] is not None]

    intervals = []
    analysis_type = "none"
    raw_values = []

    if power_data:
        analysis_type = "power"
        raw_values = power_data
        smoothed_power = utils.smooth_data(power_data, window_size=5)
        intervals = interval_detection.detect_intervals(smoothed_power, power_interval_config, zones=power_zone_definitions)
        zone_analysis = zones.analyze_zones(power_data, power_zone_definitions, analysis_type)
    elif heart_rate_data:
        analysis_type = "heart_rate"
        raw_values = heart_rate_data
        smoothed_hr = utils.smooth_data(heart_rate_data, window_size=10)
        intervals = interval_detection.detect_intervals(smoothed_hr, heart_rate_interval_config, zones=heart_rate_zone_definitions)
        zone_analysis = zones.analyze_zones(heart_rate_data, heart_rate_zone_definitions, analysis_type)
    else:
        print("No power or heart rate data found in the file.")
        return

    grouped_intervals = grouping.group_intervals(intervals)
    workout_summary = summary_generation.generate_summary(raw_values, intervals, grouped_intervals, analysis_type, zone_analysis=zone_analysis)
    # Generate the title and add it to the summary
    title = summary_generation.generate_workout_title(workout_summary)
    workout_summary['title'] = title
    output_filename = os.path.splitext(filename)[0] + "_summary.json"
    output_path = os.path.join(PROCESSED_DATA_DIR, output_filename)

    with open(output_path, 'w') as f:
        json.dump(workout_summary, f, indent=4)

    print(f"Analysis saved to: {output_path}\n")


def main():
    """Main function to process all workout files in the raw data directory."""
    if not os.path.exists(RAW_DATA_DIR):
        print(f"Error: Raw data directory '{RAW_DATA_DIR}' not found.")
        return

    for filename in os.listdir(RAW_DATA_DIR):
        file_path = os.path.join(RAW_DATA_DIR, filename)
        if os.path.isfile(file_path):
            analyze_workout(file_path)

if __name__ == "__main__":
    main()
