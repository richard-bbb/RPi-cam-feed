""""
Script that opens live camera feed on the RPi
'q' or 'esc' to quit the script
"""

import time
import numpy as np
import cv2 as cv
import v4l2
import arducam_mipicamera as arducam

TEST_NR = 17.0
ENCODING = 'raw'
RESOLUTION = [1600, 1080]
EXPOSURE = 0
GAIN = 255


def align_up(size, align):
    """Returns the closest value greater than 'size' that is dividable by 'align'."""
    return (size + align - 1) & ~(align - 1)


def set_controls(camera):
    """Sets the control variables for the camera."""
    # camera.software_auto_exposure(enable=True)
    camera.set_control(v4l2.V4L2_CID_EXPOSURE, EXPOSURE)
    camera.set_control(v4l2.V4L2_CID_VFLIP, 1)
    camera.set_control(v4l2.V4L2_CID_HFLIP, 1)
    camera.set_control(v4l2.V4L2_CID_GAIN, GAIN)


def open_frame(img, header, pos_x, pos_y):
    """Resizes frame, and puts it in the specified position on screen"""
    cv.namedWindow(header, cv.WINDOW_NORMAL)
    # cv.resizeWindow(header, 534, 360)
    cv.resizeWindow(header, 130, 90)
    cv.imshow(header, img)
    cv.moveWindow(header, pos_x, pos_y)


if __name__ == "__main__":
    print('Test: {}'.format(TEST_NR))
    cam = arducam.mipi_camera()
    cam.init_camera()
    FMT = cam.set_resolution(RESOLUTION[0], RESOLUTION[1])
    print('Current resolution = {}'.format(FMT))
    set_controls(cam)
    if ENCODING == 'raw':
        f_height = int(align_up(FMT[1], 16))
        f_width = int(align_up(FMT[0], 32))
    elif ENCODING == 'i420':
        f_height = int(align_up(FMT[1], 16) * 1.5)
        f_width = int(align_up(FMT[0], 32))

    start_time = time.time()
    x = 1
    fps = 0

    while True:
        frame = cam.capture(encoding=ENCODING)
        image = frame.as_array.reshape(f_height, f_width)
        open_frame(image, 'Live feed', 0, 0)
        fps += 1
        current_time = time.time()
        if (current_time - start_time) > x:
            print(fps)
            fps = 0
            start_time = current_time

        KEY = cv.waitKey(1)
        if KEY in (27, 113):  # pressing 'esc' or 'q' exits loop
            print('Quit program')
            break

    del frame
    cv.destroyWindow('Live feed')
    cam.close_camera()
