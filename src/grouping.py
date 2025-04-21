from datetime import datetime, timedelta

def group_intervals(intervals, min_break_duration=300, duration_tolerance=5):
    """
    Groups intervals based on proximity and similarity.
    Args:
        intervals (list of dicts): A list of intervals.
        min_break_duration (int): Minimum rest duration to start a new group.
        duration_tolerance (int): Tolerance for effort duration similarity.

    Returns:
        list of dicts: A list of grouped intervals.
    """
    if not intervals:
        return []

    grouped_intervals = []
    current_group = [intervals[0]]

    for i in range(1, len(intervals)):
        prev_end_time = datetime.fromisoformat(intervals[i - 1]["end_time"])
        curr_start_time = datetime.fromisoformat(intervals[i]["start_time"])
        time_difference = (curr_start_time - prev_end_time).total_seconds()
        duration_difference = abs(intervals[i]["duration"] - intervals[i - 1]["duration"])

        if time_difference >= min_break_duration or duration_difference > duration_tolerance:
            grouped_intervals.append({
                "intervals": current_group,
                "number_of_intervals": len(current_group),
                "average_duration": sum(interval["duration"] for interval in current_group) / len(current_group)
            })
            current_group = [intervals[i]]  # Start new group
        else:
            current_group.append(intervals[i])

    grouped_intervals.append({
        "intervals": current_group,
        "number_of_intervals": len(current_group),
        "average_duration": sum(interval["duration"] for interval in current_group) / len(current_group)
    })

    return grouped_intervals




