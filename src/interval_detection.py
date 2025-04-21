from datetime import datetime, timedelta

def detect_intervals(data, config, zones=None):
    """
    Detects intervals based on power/heart rate crossing thresholds and collects all zones spanned.
    Args:
        data (list of tuples): A list of (timestamp, value) pairs.
        config (dict): Interval detection configuration.
        zones (dict): Power/heart rate zones.

    Returns:
        list of dicts: A list of detected intervals.
    """
    if not data or not config or not zones:
        return []

    intervals = []
    interval_start = None
    interval_values = []
    interval_zones = set()  # Use a set to collect unique zones

    def determine_zone(value):
        """Determine zone for a given value."""
        for zone_name, (lower_bound, upper_bound) in zones.items():
            if lower_bound <= value < upper_bound:
                return zone_name
        return None

    for timestamp, value in data:
        current_zone = determine_zone(value)  # Assign zone for the current value
        if value >= config.get("sustain_above", 0):  # Start interval
            if interval_start is None:
                interval_start = timestamp
                interval_values = [value]
                interval_zones = {current_zone} if current_zone else set()
            else:
                interval_values.append(value)
                if current_zone:  # Add zone to the set
                    interval_zones.add(current_zone)
        elif interval_start and value < config.get("sustain_above", 0):  # End interval
            interval_end = timestamp
            duration = (datetime.fromisoformat(interval_end) - datetime.fromisoformat(interval_start)).total_seconds()
            if duration >= config.get("sustain_duration", 15):  # Ensure minimum interval duration
                intervals.append({
                    "start_time": interval_start,
                    "end_time": interval_end,
                    "duration": duration,
                    "average_value": sum(interval_values) / len(interval_values),
                    "max_value": max(interval_values),
                    "zones": sorted(interval_zones)  # Include all unique zones spanned
                })
            interval_start = None
            interval_values = []
            interval_zones = set()

    return intervals







