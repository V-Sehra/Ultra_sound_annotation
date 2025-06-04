import re


def cancer_type(label: str) -> int:
    """
    Maps a cancer annotation string to an integer label.

    Parameters
    ----------
    label : str
        A short string representing the cancer type (e.g., 'hcc', 'ccc', 'era').

    Returns
    -------
    int
        An integer corresponding to the cancer type.
        Returns None if the input is not recognized.
    """
    return {
        'hcc': 0,
        'ccc': 1,
        'era': 2,
    }.get(label.lower())  # Lowercase to make it case-insensitive


def stroc_editor(json_file: str) -> list:
    """
    Parses the JSON-like stroke annotation string and extracts a list of strokes and their types.

    Each stroke is represented as a pair of (cancer_type, list of (x, y) coordinates).

    Parameters
    ----------
    json_file : str
        A string representation of the user's stroke data.
        Example format: '{"stroke":[{"color":"hcc", "startx":..., "starty":..., ...}]}'

    Returns
    -------
    list
        A list of parsed strokes in the form [[cancer_type_id, [[x1, y1], [x2, y2], ...]], ...].
    """
    if json_file.strip() == '{"stroke":[]}':
        return []

    fig_array = []

    # Locate each 'startx' occurrence to split the strokes
    stroke_starts = [i for i in range(len(json_file)) if json_file[i:i + 6] == 'startx']

    for i in range(len(stroke_starts)):
        # Define the stroke segment
        start_idx = stroke_starts[i]
        end_idx = stroke_starts[i + 1] if i + 1 < len(stroke_starts) else len(json_file)
        stroke_str = json_file[start_idx:end_idx]

        # Try to infer the cancer type from a few characters before 'startx'
        color_key = json_file[start_idx - 6:start_idx - 3]
        label_id = cancer_type(color_key)

        # Extract numeric values (x/y positions)
        coords = re.findall(r'\d+', stroke_str)
        coords = list(map(int, coords))

        # Group into (x, y) coordinate pairs
        if len(coords) >= 2:
            stroke_coords = [[coords[j - 1], coords[j]] for j in range(1, len(coords), 2)]
            fig_array.append([label_id, stroke_coords])

    return fig_array
