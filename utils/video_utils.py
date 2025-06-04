from __future__ import annotations

import cv2
from pathlib import Path

# Allowed video file extensions
ALLOWED_EXTENSIONS = {'avi'}

# Set current working directory
cwd = Path.cwd()


def get_frame(video_path: str | Path) -> list:
    """
    Extracts and encodes all frames of a video into JPEG format.

    Parameters
    ----------
    video_path : str or Path
        Path to the video file.

    Returns
    -------
    list
        A list of JPEG-encoded frames (as numpy byte buffers).
    """
    f_list = []
    cap = cv2.VideoCapture(str(video_path))

    while True:
        success, img = cap.read()

        if not success:
            break

        ret, buffer = cv2.imencode('.jpg', img)
        if ret:
            f_list.append(buffer)

    cap.release()
    return f_list


def disp_frame(number: int, is_crop_test: bool, crop_test_frames: list, frame_list_read: list):
    """
    Yields a JPEG-encoded frame for streaming in a Flask app.

    Parameters
    ----------
    number : int
        Index of the frame to display.
    is_crop_test : bool
        Whether to use the crop test frames or the final frame list.
    crop_test_frames : list
        Frames generated during the crop test.
    frame_list_read : list
        Final annotated frames to display.

    Yields
    ------
    bytes
        HTTP multipart image data for Flask streaming.
    """
    frame = crop_test_frames[number] if is_crop_test else frame_list_read[number]
    disp = frame.tobytes()

    yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + disp + b'\r\n'
    )


def check_form(v_name: str, p_id: str, z: str, a: str) -> bool:
    """
    Validates the form inputs for patient ID, video, etc.

    Parameters
    ----------
    v_name : str
        Name of the uploaded video file.
    p_id : str
        Patient ID.
    z : str
        Index number.
    a : str
        Angle or other metadata.

    Returns
    -------
    bool
        True if all inputs are valid, False otherwise.
    """
    if not all([v_name, p_id, z, a]):
        return False

    if '.' not in v_name or v_name.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
        return False

    return True


def check_dir(p_id: str, z: str) -> Path:
    """
    Creates and returns the output directory path.

    Parameters
    ----------
    p_id : str
        Patient ID.
    z : str
        Index number.

    Returns
    -------
    Path
        Path to the output directory.
    """
    save_path = Path.cwd() / 'anotation' / p_id / f"{p_id}_{z}"
    save_path.mkdir(parents=True, exist_ok=True)
    return save_path
