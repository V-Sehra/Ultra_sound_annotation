"""
Flask-based GUI application for video annotation with cropping and frame-level feedback.
Primary use case: Processing and annotating microscopy or patient-derived video data.

Functionality:
- Upload videos with patient and index metadata.
- Allow user to select a preferred crop based on test crops.
- Annotate frames using canvas-based feedback (strokes, flags).
- Save annotations as a pickle file.

Author: Vivek Sehra
Initial Version: 21 June 2022
"""

from pathlib import Path
import pickle
import base64
import re
import io

import numpy as np
from PIL import Image
from flask import Flask, render_template, request, redirect, Response

from utils.annotation_utils import stroc_editor
from utils.video_utils import disp_frame, get_frame, check_form, check_dir
from utils.cropping_utils import crop_single, mask_sizer

# Flask app setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Path('static') / 'crop_templets'

# Global state variables (minimal persistence for simplicity)
filename = ""
s_path = ''
pat_id = ''
index = ''
prev_click = ""
crop_test = True
crop_test_vid = ""
crop_test_frames = []
crop_test_counter = 0
crop_mask = []
canv_data = {}
frame_list_read = []
vid_file = ''
body_bool = ""

# Annotation state tracking
counter = 0


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Initial page to upload video and metadata."""
    global frame_list_read, s_path, pat_id, index, counter, canv_data, prev_click, vid_file, filename, body_bool

    if request.method == 'GET':
        return render_template('start.html')

    if request.method == 'POST':
        pat_id = request.form['p_id']
        index = request.form['index']
        angle = request.form['angle']
        vid_file = request.files['vid_file']
        body_bool = 'pictograph' in request.form

        if not check_form(vid_file.filename, pat_id, index, angle):
            return redirect('/wrong_input')

        s_path = check_dir(pat_id, index)
        filename = str(s_path / f"{pat_id}_{index}_raw.avi")

        vid_file.save(filename)
        with open(s_path / 'angle.pkl', 'wb') as f:
            pickle.dump(angle, f)

        canv_data = {}
        counter = 0
        prev_click = ""

        return redirect('/correct_crop')


@app.route('/wrong_input', methods=['GET', 'POST'])
def wrong_input():
    """Display form again if invalid inputs are given."""
    return render_template('wrong_input.html')


@app.route('/collect_body_bool', methods=['POST'])
def collect_body_bool():
    """Handle pictograph upload if present."""
    global body_bool
    body_bool = request.files['pictograph']
    return ''


@app.route('/correct_crop', methods=['GET'])
def correct_crop():
    """Display test crops for user to select best one."""
    global s_path, pat_id, index, crop_test_vid, crop_test_frames, crop_test, crop_mask, filename, body_bool

    s_path = check_dir(pat_id, index)
    filename = str(s_path / f"{pat_id}_{index}_raw.avi")

    crop_test = True
    crop_test_vid, crop_mask = crop_single(filename, s_path, pat_id, index, body_bool)
    crop_test_frames = get_frame(crop_test_vid)

    return render_template('correct_crop.html')


@app.route('/next_crop', methods=['GET'])
def next_crop():
    """Cycle through available crop variants."""
    global crop_test_counter
    crop_test_counter = (crop_test_counter + 1) % len(crop_test_frames)
    return render_template('correct_crop.html')


@app.route('/crop_good', methods=['GET'])
def good_grop():
    """Apply selected crop settings to entire video and extract all frames."""
    global filename, s_path, pat_id, index, crop_test_counter, crop_test, frame_list_read, body_bool

    crop_test = False
    best_mask = crop_mask[crop_test_counter]
    video_name = mask_sizer(filename, s_path, pat_id, index, best_mask, body_bool)
    frame_list_read = get_frame(video_name)

    return redirect('/annotator')


@app.route('/annotator', methods=['GET'])
def anotator():
    """Render annotator interface with prior annotations loaded if available."""
    global counter
    idx = counter
    prev = idx - 1

    if f'raw_frame_{idx}' in canv_data:
        return render_template('anotator.html', Number=idx + 1, Totalframes=len(frame_list_read),
                               prev_canv=canv_data.get(f'strokes_{idx}', []),
                               prev_ck=prev_click,
                               prev_check_unsure=int(canv_data.get(f'unsure_{idx}', 0)),
                               prev_check_bad_frame=canv_data.get(f'bad_frame_{idx}', 0))
    elif idx != 0:
        return render_template('anotator.html', Number=idx + 1, Totalframes=len(frame_list_read),
                               prev_canv=canv_data.get(f'strokes_{prev}', []),
                               prev_ck=prev_click, prev_check_unsure=0, prev_check_bad_frame=0)
    else:
        return render_template('anotator.html', Number=1, Totalframes=len(frame_list_read),
                               prev_canv=[], prev_ck=prev_click, prev_check_unsure=0, prev_check_bad_frame=0)


@app.route('/get_prev_mark', methods=['GET'])
def get_prev_mark():
    """Carry forward previous marking if available."""
    global counter
    if counter > 0:
        canv_data[f'strokes_{counter}'] = canv_data.get(f'strokes_{counter - 1}', [])
    return redirect('/annotator')


@app.route('/frame')
def frame():
    """Video feed streaming endpoint."""
    global counter, crop_test_counter, crop_test
    idx = crop_test_counter if crop_test else counter
    return Response(disp_frame(idx, crop_test, crop_test_frames, frame_list_read),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/can_im', methods=['POST'])
def can_im():
    """Receive and process annotation canvas data from client."""
    global canv_data, counter, prev_click

    image_b64 = request.values['imageBase64']
    image_data = re.sub('^data:image/.+;base64,', '', image_b64)
    image = base64.b64decode(image_data)
    image_np = np.array(Image.open(io.BytesIO(image)))

    canv_data[f'img_{counter}'] = image_np
    canv_data[f'raw_frame_{counter}'] = np.array(Image.open(io.BytesIO(frame_list_read[counter])))
    canv_data[f'unsure_{counter}'] = request.values['un_sure']
    canv_data[f'bad_frame_{counter}'] = request.values['bad_frame']
    canv_data[f'raw_marking_{counter}'] = request.values['data']
    canv_data[f'strokes_{counter}'] = stroc_editor(request.values['data'])
    prev_click = request.values['prev_ck']

    return ''


@app.route('/next_frame')
def next_frame():
    """Go to the next frame in sequence."""
    global counter
    counter = min(counter + 1, len(frame_list_read) - 1)
    return redirect('/annotator')


@app.route('/prev_frame')
def prev_frame():
    """Return to the previous frame."""
    global counter
    counter = max(counter - 1, 0)
    return redirect('/annotator')


@app.route('/save_and_exit')
def save_and_exit():
    """Save annotations and exit workflow."""
    global counter, canv_data, frame_list_read, s_path, pat_id

    # Fill in skipped annotations
    for idx in range(counter + 1, len(frame_list_read)):
        canv_data[f'img_{idx}'] = np.zeros((720, 896, 4))
        canv_data[f'raw_frame_{idx}'] = np.array(Image.open(io.BytesIO(frame_list_read[idx])))
        canv_data[f'raw_marking_{idx}'] = None
        canv_data[f'unsure_{idx}'] = 0
        canv_data[f'bad_frame_{idx}'] = 0

    with open(s_path / f"{pat_id}_{index}_anotations.pkl", 'wb') as f:
        pickle.dump(canv_data, f)

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=False)
