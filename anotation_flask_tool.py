#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 19:39:03 2022

@author: Vivek
"""

import os

from flask import Flask, render_template, request, redirect, Response

cwd = os.getcwd()
import cv2
import pickle
from PIL import Image
import base64
import re
import io
import numpy as np
from cropper import cropper
from crop_single import crop_single
from crop_single import mask_sizer
import copy

ip = 'http://127.0.0.1:5000/'

ALLOWED_EXTENSIONS = {'avi'}


def get_frame(video_path):
    f_list = []

    cap = cv2.VideoCapture(video_path)

    while True:

        err, img = cap.read()
        if err:

            ret, buffer = cv2.imencode('.jpg', img)
            f_list.append(buffer)

        else:
            break

    return (f_list)


def disp_frame(number, cop_test):
    # show the current frame on the webapp
    if cop_test:
        disp = crop_test_frames[number].tobytes()
    else:
        disp = frame_list_read[number].tobytes()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + disp + b'\r\n')


def cancer_type(str_):
    # switch between the different cancer anotations
    switch = {
        'hcc': 0,
        'ccc': 1,
        'era': 2,
    }
    return switch.get(str_)


def stroc_editor(json_file):
    # draw the previous markings

    if json_file == '{"stroke":[]}':
        return ([])
    else:
        fig_array = []
        #collect the induvidual markings startx = first stroke
        counts = [count_id for count_id in range(len(json_file)) if json_file[count_id:count_id + 6] == 'startx']

        for fig_id in range(len(counts) - 1):
            #what color was used?
            c_type = cancer_type(json_file[counts[fig_id] - 6:counts[fig_id] - 3])
            str_ = json_file[counts[fig_id]:counts[fig_id + 1]]
            nums = [(int, re.findall(r'\d+', str_))[1]]
            ob_vec = [[nums[0][i - 1], nums[0][i]] for i in range(1, len(nums[0]), 2)]
            fig_array.append([c_type, ob_vec])

        c_type = cancer_type(json_file[counts[-1] - 6:counts[-1] - 3])
        str_ = json_file[counts[-1]:]
        nums = [(int, re.findall(r'\d+', str_))[1]]
        ob_vec = [[nums[0][i - 1], nums[0][i]] for i in range(1, len(nums[0]), 2)]
        fig_array.append([c_type, ob_vec])

        return (fig_array)


def check_form(v_name, p_id, z, a):
    if v_name is None or \
            p_id is None or \
            z is None or \
            a is None:
        return False

    if not v_name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        return False

    return True


def check_dir(p_id, z):
    # create the directory where the files will be saved

    if not os.path.exists(cwd + '/anotation/'):
        os.mkdir(cwd + '/anotation/')

    if not os.path.exists(cwd + '/anotation/' + str(p_id) + '/'):
        os.mkdir(cwd + '/anotation/' + str(p_id) + '/')

    if not os.path.exists(cwd + '/anotation/' + str(p_id) + '/' + str(p_id) + '_' + str(z) + '/'):
        os.mkdir(cwd + '/anotation/' + str(p_id) + '/' + str(p_id) + '_' + str(z) + '/')

    save_path = f"{cwd}/anotation/{p_id}/{p_id}_{z}/"
    return (save_path)


crop_folder = os.path.join('static', 'crop_templets')

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = crop_folder

filename = ""
s_path = ''
pat_id = ''
index = ''
prev_click = ""

crop_test = True

counter = 0
crop_test_vid = ""

crop_test_frames = []
crop_test_counter = 0
crop_mask = []

canv_data = {}
frame_list_read = []
vid_file = ''
body_bool = ""

crop_img_bool = {}


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global frame_list_read, s_path, pat_id, index, raw_frames, counter, canv_data, prev_click, vid_file, filename, body_bool

    if request.method == 'GET':
        return (render_template('start.html'))

    if request.method == 'POST':
        pat_id = request.form['p_id']
        index = request.form['index']
        angle = request.form['angle']
        vid_file = request.files['vid_file']
        body_bool = 'pictograph' in request.form
        print(body_bool)

        if not check_form(vid_file.filename, pat_id, index, angle):
            return redirect('/wrong_input')

        s_path = check_dir(pat_id, index)

        filename = s_path + pat_id + '_' + index + '_raw.avi'

        vid_file.save(filename)
        with open(s_path + '/angle.pkl', 'wb') as f:
            pickle.dump(angle, f)

        canv_data = {}
        counter = 0
        prev_click = ""

        return redirect('/correct_crop')

    return (render_template('done.html'))


@app.route('/wrong_input', methods=['GET', 'POST'])
def wrong_input():
    if request.method == 'GET':
        return (render_template('wrong_input.html'))

    if request.method == 'POST':
        pat_id = request.form['p_id']
        index = request.form['index']
        angle = request.form['angle']
        vid_file = request.files['vid_file']

        if not check_form(vid_file, pat_id, index, angle):
            return redirect('/wrong_input')
        else:
            return redirect(ip)


@app.route('/collect_body_bool', methods=['POST'])
def collect_body_bool():
    # is the pictogram present?
    global body_bool

    body_bool = request.files['pictograph']

    return ''


@app.route('/correct_crop', methods=['GET', 'POST'])
def correct_crop():
    global s_path, pat_id, index, crop_test_vid, crop_test_frames, crop_test, crop_mask, filename, body_bool
    #let the user choose which crop was well done
    if request.method == 'GET':
        s_path = check_dir(pat_id, index)

        filename = s_path + pat_id + '_' + index + '_raw.avi'

        crop_test = True

        crop_test_vid, crop_mask = crop_single(filename, s_path, pat_id, index, body_bool)
        crop_test_frames = get_frame(crop_test_vid)

        return render_template('correct_crop.html')


@app.route('/next_crop', methods=['GET', 'POST'])
def next_crop():
    global crop_test_counter
    # switch between the different test crops
    if crop_test_counter < len(crop_test_frames) - 1:
        crop_test_counter = crop_test_counter + 1
    else:
        crop_test_counter = 0

    return render_template('correct_crop.html')


@app.route('/crop_good', methods=['GET', 'POST'])
def good_grop():
    global filename, s_path, pat_id, index, crop_test_counter, crop_test, frame_list_read, body_bool
    # if the user chose one to be good select the cropping parameteres and apply them to all frames
    crop_test = False

    best_mask = crop_mask[crop_test_counter]
    print(crop_mask[crop_test_counter])

    video_name = mask_sizer(filename, s_path, pat_id, index, best_mask, body_bool)

    frame_list_read = get_frame(video_name)

    return redirect('/annotator')


@app.route('/annotator', methods=['GET', 'POST'])
def anotator():
    # render the annotation and corresponding frame
    if 'raw_frame_' + str(counter) in canv_data.keys():

        return render_template('anotator.html', Number=counter + 1,
                               Totalframes=len(frame_list_read),
                               prev_canv=canv_data['strokes_' + str(counter)],
                               prev_ck=prev_click,
                               prev_check_unsure=int(canv_data['unsure_' + str(counter)]),
                               prev_check_bad_frame=canv_data['bad_frame_' + str(counter)])

    elif (not 'raw_frame_' + str(counter) in canv_data.keys()) and counter != 0:

        return render_template('anotator.html', Number=counter + 1,
                               Totalframes=len(frame_list_read),
                               prev_canv=canv_data['strokes_' + str(counter - 1)],
                               prev_ck=prev_click,
                               prev_check_unsure=0,
                               prev_check_bad_frame=0)

    elif len(canv_data) == 0:

        return render_template('anotator.html', Number=counter + 1,
                               Totalframes=len(frame_list_read),
                               prev_canv=[],
                               prev_ck=prev_click,
                               prev_check_unsure=0,
                               prev_check_bad_frame=0)


@app.route('/get_prev_mark', methods=['GET', 'POST'])
def get_prev_mark():
    global counter
    # provide the markings done
    if counter != 0:
        canv_data['strokes_' + str(counter)] = canv_data['strokes_' + str(counter - 1)]

    return redirect('/annotator')


@app.route('/frame')
def frame():
    global counter, crop_test_counter, crop_test

    if crop_test:
        return Response(disp_frame(crop_test_counter, crop_test), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response(disp_frame(counter, crop_test), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/can_im', methods=['POST'])
def can_im():
    global can_data, counter, prev_click
    # collect all data presented on the canvas from the user
    image_b64 = request.values['imageBase64']
    image_data = re.sub('^data:image/.+;base64,', '', image_b64)
    image = base64.b64decode(image_data)

    image_np = np.array(Image.open(io.BytesIO(image)))

    canv_data['img_' + str(counter)] = image_np

    canv_data['raw_frame_' + str(counter)] = np.array(Image.open(io.BytesIO(frame_list_read[counter])))

    canv_data['unsure_' + str(counter)] = request.values['un_sure']
    canv_data['bad_frame_' + str(counter)] = request.values['bad_frame']
    canv_data['raw_marking_' + str(counter)] = request.values['data']
    canv_data['strokes_' + str(counter)] = stroc_editor(canv_data['raw_marking_' + str(counter)])

    prev_click = request.values['prev_ck']

    return ''


@app.route('/next_frame')
def next_frame():
    global counter
    if counter < len(frame_list_read) - 1:
        counter = counter + 1

    return redirect('/annotator')


@app.route('/prev_frame')
def prev_frame():
    global counter

    if counter > 0:
        counter = counter - 1

    else:
        counter = 0
    return redirect('/annotator')


@app.route('/save_and_exit')
def save_and_exit():
    global counter, canv_data, frame_list_read, s_path, pat_id
    # go through all the not annotated frames left and save them 
    for idx in range(counter + 1, len(frame_list_read)):
        canv_data['img_' + str(idx)] = np.zeros((720, 896, 4))

        canv_data['raw_frame_' + str(idx)] = np.array(Image.open(io.BytesIO(frame_list_read[idx])))
        canv_data['raw_marking_' + str(idx)] = None
        canv_data['unsure_' + str(idx)] = 0
        canv_data['bad_frame_' + str(idx)] = 0

    with open(s_path + pat_id + '_' + str(index) + '_anotations.pkl', 'wb') as f:
        pickle.dump(canv_data, f)

    return redirect(ip)


if __name__ == "__main__":
    app.run()