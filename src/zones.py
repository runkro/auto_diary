from datetime import datetime

def analyze_zones(data_points, zone_definitions, analysis_type="power"):
    """
    Analyzes the time spent in different power or heart rate zones.

    Args:
        data_points (list of tuples): A list of (timestamp, value) where value is power or heart rate.
        zone_definitions (dict): A dictionary defining the zones.
                                  For power, keys are zone names and values are lists [lower_bound_percent, upper_bound_percent] of FTP.
                                  For heart rate, keys are zone names and values are lists [lower_bound_percent, upper_bound_percent] of Max HR or LTHR.
        analysis_type (str): Either "power" or "heart_rate", indicating the type of data being analyzed.

    Returns:
        dict: A dictionary where keys are zone names and values are the time spent in that zone (in seconds).
              Also includes the athlete's FTP or Max HR/LTHR if applicable and provided.
    """
    if not data_points or not zone_definitions:
        print("analyze_zones: No data points or zone definitions provided.")
        return {}

    time_in_zones = {zone: 0 for zone in zone_definitions}
    previous_time = None

    # Get athlete-specific reference value if available in definitions
    reference_value = zone_definitions.get("ftp") if analysis_type == "power" else zone_definitions.get("max_hr") or zone_definitions.get("lthr")

    print(f"analyze_zones: Analysis type: {analysis_type}, Reference value: {reference_value}")

    # Create absolute zone boundaries based on percentages (if reference value exists)
    absolute_zones = {}
    if reference_value is not None:
        for zone, bounds in zone_definitions.items():
            if zone in ["ftp", "max_hr", "lthr"]:  # Skip reference value keys
                continue
            if isinstance(bounds, list) and len(bounds) == 2:
                lower_bound = reference_value * (bounds[0] / 100.0)
                upper_bound = reference_value * (bounds[1] / 100.0)
                absolute_zones[zone] = [lower_bound, upper_bound]
            else:
                absolute_zones[zone] = bounds  # Assume already absolute if not a percentage list
    else:
        absolute_zones = zone_definitions  # Assume already absolute if no reference value

    for i, (timestamp_str, value) in enumerate(data_points):
        try:
            current_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))  # Handle potential 'Z' timezone
        except ValueError:
            try:
                current_time = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                try:
                    current_time = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S%z')
                except ValueError:
                    print(f"analyze_zones: Warning: Could not parse timestamp: {timestamp_str}")
                    continue

        if previous_time:
            duration = (current_time - previous_time).total_seconds()
            if value is not None:
                found_zone = False
                for zone, bounds in absolute_zones.items():
                    if isinstance(bounds, list) and len(bounds) == 2:
                        lower_bound = min(bounds)
                        upper_bound = max(bounds)
                        if reference_value is not None:
                            # Handle percentage-based zones
                            lower_bound_abs = reference_value * (lower_bound / 100.0)
                            upper_bound_abs = reference_value * (upper_bound / 100.0)
                            if lower_bound_abs <= value < upper_bound_abs:
                                time_in_zones[zone] += duration
                                found_zone = True
                                break
                        else:
                            # Handle direct BPM ranges
                            if lower_bound <= value < upper_bound:
                                time_in_zones[zone] += duration
                                found_zone = True
                                break
                if not found_zone and value is not None:
                    print(f"analyze_zones: Time: {current_time}, HR: {value}, No zone matched")

        previous_time = current_time

    results = time_in_zones
    if reference_value is not None:
        results[f"{analysis_type.upper()} Reference Value"] = reference_value

    print(f"analyze_zones: Final time in zones: {results}")

    return results

