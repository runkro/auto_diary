from datetime import datetime, timedelta

def format_timedelta(seconds):
    """Formats a duration in seconds as HH:MM:SS."""
    duration = timedelta(seconds=seconds)
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def format_duration_minutes(seconds):
    """Formats a duration in seconds as total minutes (integer)."""
    return int(seconds // 60)


def generate_summary(raw_data, intervals, grouped_intervals, analysis_type="power", zone_analysis=None):
    summary = {}

    # Overall Workout Duration
    if raw_data:
        start_time_str, _ = raw_data[0]
        end_time_str, _ = raw_data[-1]
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            total_duration = end_time - start_time
            summary['workout_duration'] = str(total_duration).split('.')[0]  # Format as HH:MM:SS
        except Exception as e:
            print(f"Error calculating workout duration: {e}")
            summary['workout_duration'] = "N/A"
    else:
        summary['workout_duration'] = "N/A"
    
    # Analysis Type
    summary['analysis_type'] = analysis_type
    
    # Zone Analysis
    if zone_analysis:
        formatted_zone_analysis = {}
        for zone, duration_seconds in zone_analysis.items():
            formatted_zone_analysis[zone] = format_timedelta(duration_seconds)
        summary['zone_analysis'] = formatted_zone_analysis

    # Number of Intervals
    summary['number_of_intervals'] = len(intervals)

    # Grouped Intervals
    summary['grouped_intervals'] = []
    for group in grouped_intervals:  # Group is a dictionary
        group_summary = []
        for interval in group['intervals']:  # Iterate over the list of intervals in the group
            group_summary.append({
                'start_time': interval['start_time'],
                'end_time': interval['end_time'],
                'duration': interval['duration'],
                'zones': interval['zones'],
                'average_value': interval['average_value'],
                'max_value': interval['max_value']
            })
        summary['grouped_intervals'].append({
            'intervals': group_summary,  # Add the interval summaries to this group
            'number_of_intervals': group['number_of_intervals'],  # Access group properties correctly
            'average_duration': group['average_duration']  # Access group properties correctly
        })

    return summary

def generate_workout_title(summary):
    """Generates a workout title with total time, interval groups, and zones."""
    title_parts = []

    def format_duration_mmss(seconds):
        """Helper function to format duration as MM:SSmin or XXsec for times below 60 seconds."""
        if seconds < 60:
            return f"{int(seconds)}sec"  # Display as seconds if under 60
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}:{remaining_seconds:02d}min"  # Display as MM:SSmin otherwise

    # Total Time of Workout
    if 'workout_duration' in summary and summary['workout_duration'] != "N/A":
        title_parts.append(summary['workout_duration'])
    else:
        title_parts.append("Workout")

    # Activity Type
    activity_type = "activity"
    if summary.get('analysis_type') == 'power':
        activity_type = "cycling"
    elif summary.get('analysis_type') == 'heart_rate':
        activity_type = "workout"
    title_parts.append(activity_type)

    # Interval Groups with Zones
    if 'grouped_intervals' in summary and summary['grouped_intervals']:
        grouped_intervals = summary['grouped_intervals']
        
        # Check if we have more than 3 unique interval groups
        if len(grouped_intervals) > 4:
            # Summarize intervals
            total_intervals = sum(group['number_of_intervals'] for group in grouped_intervals)
            shortest_duration = min(group['average_duration'] for group in grouped_intervals)
            longest_duration = max(group['average_duration'] for group in grouped_intervals)
            zones = set()
            for group in grouped_intervals:
                for interval in group['intervals']:
                    if 'zones' in interval:
                        zones.update(interval['zones'])
            zone_description = "-".join(sorted(zones))  # Get range of zones
            interval_description = f"with {total_intervals} intervals of {format_duration_mmss(shortest_duration)}-{format_duration_mmss(longest_duration)} in {zone_description}"
            title_parts.append(interval_description)
        else:
            # Detailed descriptions for 3 or fewer groups
            interval_descriptions = []
            i = 0
            while i < len(grouped_intervals):
                current_group = grouped_intervals[i]
                merged = False

                # Check if the next group can be merged
                if i < len(grouped_intervals) - 1:
                    next_group = grouped_intervals[i + 1]
                    if (current_group['number_of_intervals'] == next_group['number_of_intervals'] and
                        abs(current_group['average_duration'] - next_group['average_duration']) <= 15):
                        # Merge groups
                        merged = True
                        combined_count = 2  # Combine two groups
                        combined_average_duration = round(
                            (current_group['average_duration'] + next_group['average_duration']) / 2
                        )
                        zones = current_group['intervals'][0]['zones'] + next_group['intervals'][0]['zones']
                        zone_description = "-".join(sorted(set(zones)))  # Get unique zones across merged groups
                        interval_descriptions.append(f"{combined_count}x {format_duration_mmss(combined_average_duration)} {zone_description}")
                        i += 1  # Skip the next group as it's merged

                if not merged:
                    # Use current group as-is
                    zones = current_group['intervals'][0]['zones']
                    zone_description = "-".join(sorted(set(zones)))  # Get unique zones for the current group
                    interval_descriptions.append(
                        f"{current_group['number_of_intervals']}x {format_duration_mmss(current_group['average_duration'])} {zone_description}"
                    )

                i += 1  # Move to the next group

            title_parts.append("with " + ", ".join(interval_descriptions))

    return " ".join(title_parts)
