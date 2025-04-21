import numpy as np

def smooth_data(data, window_size):
    """
    Applies a simple moving average smoothing to a time series.

    Args:
        data (list of tuples): A list of (timestamp, value) pairs.
        window_size (int): The size of the moving average window.

    Returns:
        list of tuples: A new list with smoothed values. The first
                       `window_size - 1` values will be the same as the
                       original data.
    """
    if len(data) < window_size:
        return data  # Cannot smooth if data is shorter than the window

    smoothed_data = []
    values = np.array([item[1] for item in data])
    timestamps = [item[0] for item in data]

    for i in range(len(values)):
        if i < window_size - 1:
            smoothed_data.append((timestamps[i], values[i]))
        else:
            window = values[i - window_size + 1 : i + 1]
            average = np.mean(window)
            smoothed_data.append((timestamps[i], average))

    return smoothed_data
