import xml.etree.ElementTree as ET
import gpxpy
import gpxpy.gpx

def parse_tcx_file(file_path):
    """Parses a TCX file and extracts timestamp, power, and heart rate data."""
    data = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        namespace = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
                     'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'}  # Add the ns3 namespace

        for lap in root.findall('.//ns:Lap', namespace):
            for track in lap.findall('.//ns:Track', namespace):
                for trackpoint in track.findall('.//ns:Trackpoint', namespace):
                    timestamp_elem = trackpoint.find('ns:Time', namespace)
                    hr_elem = trackpoint.find('ns:HeartRateBpm/ns:Value', namespace)
                    power_elem = trackpoint.find('ns:Extensions/ns3:TPX/ns3:Watts', namespace) # Use the namespace

                    timestamp = timestamp_elem.text if timestamp_elem is not None else None
                    heart_rate = int(hr_elem.text) if hr_elem is not None and hr_elem.text.isdigit() else None
                    power = int(power_elem.text) if power_elem is not None and power_elem.text.isdigit() else None

                    if timestamp:
                        data.append({'timestamp': timestamp, 'power': power, 'heart_rate': heart_rate})

    except FileNotFoundError:
        print(f"Error: TCX file not found at {file_path}")
    except ET.ParseError:
        print(f"Error: Could not parse TCX file at {file_path}")
    return data

def parse_gpx_file(file_path):
    """Parses a GPX file and extracts timestamp and heart rate data (if available)."""
    data = []
    try:
        with open(file_path, 'r') as f:
            gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        timestamp = point.time.isoformat() if point.time else None
                        heart_rate = None
                        for extension in point.extensions:
                            if extension.tag.endswith('TrackPointExtension'):
                                for child in extension:
                                    if child.tag.endswith('hr'):
                                        if child.text and child.text.isdigit():
                                            heart_rate = int(child.text)
                                        break
                                break
                        if timestamp:
                            data.append({'timestamp': timestamp, 'power': None, 'heart_rate': heart_rate})

    except FileNotFoundError:
        print(f"Error: GPX file not found at {file_path}")
    except gpxpy.gpx.GPXException as e:
        print(f"Error parsing GPX file at {file_path}: {e}")
    return data

def parse_workout_file(file_path):
    """Parses a workout file and returns a list of data points."""
    if file_path.lower().endswith('.tcx'):
        return parse_tcx_file(file_path)
    elif file_path.lower().endswith('.gpx'):
        return parse_gpx_file(file_path)
    else:
        print(f"Warning: Unsupported file format for {file_path}. Skipping.")
        return []

if __name__ == "__main__":
    # Example usage (assuming you have sample TCX and GPX files in the data/raw directory)
    tcx_file = '../data/raw/activity_18223135043.tcx'  # Use your actual file name
    gpx_file = '../data/raw/workout2.gpx'

    tcx_data = parse_tcx_file(tcx_file)
    if tcx_data:
        print(f"Parsed {len(tcx_data)} data points from {tcx_file}. First 10:")
        for item in tcx_data[:10]:
            print(item)

    gpx_data = parse_gpx_file(gpx_file)
    if gpx_data:
        print(f"\nParsed {len(gpx_data)} data points from {gpx_file}. First 5:")
        for item in gpx_data[:5]:
            print(item)