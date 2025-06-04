#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 10:38:51 2022
Author: Vivek Sehra
Refactored to use pathlib, improved readability, fixed typos, and added docstrings.
"""

import cv2
import numpy as np
from pathlib import Path
import imutils
import imageio

# Set working directory
cwd = Path.cwd()


def crop_single(f_name, s_path, pat_id, index, body_bool):
    """
    Runs a cropping test on a single video by removing fixed UI elements
    based on template matching, saving a test cropped video.

    Args:
        f_name (Path or str): Path to the input video file.
        s_path (Path): Directory to save the test video.
        pat_id (str): Patient ID.
        index (str or int): Session/index identifier.
        body_bool (bool): Whether to mask out the body pictogram.

    Returns:
        Tuple: (Path to test video, list of detected regions with labels)
    """

    def sizer(matrix_resize, image_resize, cord, label, body_bool):
        """Apply masking to the frame based on the region label."""
        y1, y2, x1, x2 = cord
        if label == 'body.png' and body_bool:
            matrix_resize[y1 - 10:y2 + 10, x1 - 10:x2 + 10] = 0
        elif label == 'T_box.png':
            matrix_resize[y1 - 10:y2 + 10, x1 - 10:x2 + 10] = 0
        elif label == 'upper_box.png':
            matrix_resize[:y2 - 5, :] = 0
        elif label == 'left_box.png':
            matrix_resize[:, :x2 + 10] = 0
        return matrix_resize

    def remover(matrix, image):
        """Detect and mask UI elements using template matching."""
        remove_id = []
        template_labels = ['upper_box.png', 'left_box.png', 'body.png', 'T_box.png']
        template_paths = [cwd / 'crop_templets' / label for label in template_labels]

        for idx, template_path in enumerate(template_paths):
            label = template_labels[idx]
            template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
            template = cv2.Canny(template, 50, 200)
            (tH, tW) = template.shape[:2]

            if label == 'T_box.png':
                region = image[0:int(image.shape[0] * 0.2), int(image.shape[1] * 0.5):]
            else:
                region = image

            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            found = None

            for scale in np.linspace(0.2, 1.0, 5)[::-1]:
                resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
                r = gray.shape[1] / float(resized.shape[1])

                if resized.shape[0] < tH or resized.shape[1] < tW:
                    break

                edged = cv2.Canny(resized, 50, 200)
                result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
                (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

                if found is None or maxVal > found[0]:
                    found = (maxVal, maxLoc, r)

            if found is not None:
                (_, maxLoc, r) = found
                startX, startY = int(maxLoc[0] * r), int(maxLoc[1] * r)
                endX, endY = int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r)

                if label == 'T_box.png':
                    startX += int(image.shape[1] * 0.5)
                    endX += int(image.shape[1] * 0.5)

                coords = [startY, endY, startX, endX]
                remove_id.append([coords, label])
                matrix = sizer(matrix, image, coords, label, body_bool)

        return matrix, remove_id

    # --- Read video frames
    cap = cv2.VideoCapture(str(f_name))
    frames = []
    while True:
        ret, img = cap.read()
        if not ret:
            break
        img = img[:, :885]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        frames.append([gray, img])
    cap.release()

    # --- Apply template masking to selected frames
    single_frames = []
    remove_metadata = []
    for i in range(0, len(frames), max(1, len(frames) // 7)):
        processed, removed = remover(frames[i][0], frames[i][1])
        single_frames.append(processed)
        remove_metadata.append(removed)

    # --- Save test video
    video_path = s_path / f"{pat_id}_{index}_cropped_test.mp4"
    imageio.mimwrite(str(video_path), single_frames, fps=30)

    return video_path, remove_metadata


def mask_sizer(vid_name, s_path, pat_id, index, mask, body_bool):
    """
    Applies final cropping based on user-chosen mask and saves new video.

    Args:
        vid_name (Path or str): Input test video path.
        s_path (Path): Save directory.
        pat_id (str): Patient ID.
        index (str or int): Session identifier.
        mask (List): Regions to be masked.
        body_bool (bool): Whether body template was used.

    Returns:
        Path to cropped video.
    """

    def sizer(matrix_resize, mask_):
        """Apply all masks to a single frame."""
        for region in mask_:
            coords = region[0]
            label = region[1]
            y1, y2, x1, x2 = coords

            if label == 'body.png' and body_bool:
                matrix_resize[y1 - 10:y2 + 10, x1 - 10:x2 + 10] = 0
            elif label == 'T_box.png':
                matrix_resize[y1 - 10:y2 + 10, x1 - 10:x2 + 10] = 0
            elif label == 'upper_box.png':
                matrix_resize[:y2 - 5, :] = 0
            elif label == 'left_box.png':
                matrix_resize[:, :x2 + 10] = 0

        return matrix_resize

    # --- Read and crop all frames
    cap = cv2.VideoCapture(str(vid_name))
    cropped_frames = []
    while True:
        ret, img = cap.read()
        if not ret:
            break
        img = img[:, :885]
        cropped_frames.append(sizer(img, mask))
    cap.release()

    # --- Save final cropped video
    final_path = s_path / f"{pat_id}_{index}_cropped.mp4"
    imageio.mimwrite(str(final_path), cropped_frames, fps=30)

    # Clean up
    Path(vid_name).unlink()

    return final_path
