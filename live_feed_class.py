import time
import numpy as np
from threading import Thread
import cv2 as cv
import v4l2
import arducam_mipicamera as arducam


class CameraFeed():

    def __init__(self, resolution=(1600, 1300), encoding='raw'):
        self.camera = arducam.mipi_camera()
        self.camera.init_camera()
        self.fmt = self.camera.set_resolution(resolution[0], resolution[1])
        self.encoding = encoding
        if self.encoding == 'raw':
            self.height = int(align_up(self.fmt[1], 16))
            self.width = int(align_up(self.fmt[0], 32))
        else:
            self.height = int(align_up(self.fmt[1], 16) * 1.5)
            self.width = int(align_up(self.fmt[0], 32))
        self.frame = None
        self.grabbed = False
        self.stopped = False

    def set_controls(self, exposure='auto', gain=255):
        self.camera.set_control(v4l2.V4L2_CID_VFLIP, 1)
        self.camera.set_control(v4l2.V4L2_CID_HFLIP, 1)
        self.camera.set_control(v4l2.V4L2_CID_GAIN, gain)

        if exposure == 'auto':
            self.camera.software_auto_exposure(enable=True)
        else:
            self.camera.set_control(v4l2.V4L2_CID_EXPOSURE, exposure)

    def start_threads(self):
        thread_get = Thread(target=self.get_frame, args=())
        thread_open = Thread(target=self.open_frame, args=())
        thread_get.setDaemon(True)
        thread_open.setDaemon(True)
        thread_get.start()
        thread_open.start()
        return self

    def get_frame(self):
        while not self.stopped:
            self.frame = self.camera.capture(encoding=self.encoding)
            self.grabbed = True

    def open_frame(self, header='Live Feed', x_pos=0, y_pos=0):
        while not self.stopped:
            if self.grabbed:
                img = self.frame.as_array.reshape(self.height, self.width)
                cv.namedWindow(header, cv.WINDOW_NORMAL)
                cv.resizeWindow(header, 160, 130)
                cv.imshow(header, img)
                cv.moveWindow(header, x_pos, y_pos)
                self.grabbed = False
                if cv.waitKey(10) in (27, 113):  # pressing 'esc' or 'q' exits loop
                    print('Quit script')
                    self.stopped = True

    def close(self):
        del self.frame
        cv.destroyAllWindows()
        self.camera.close_camera()
        print("Camera closed")


def align_up(size, align):
    """Returns the closest value greater than 'size' that is dividable by 'align'."""
    return (size + align - 1) & ~(align - 1)


def main():
    test = 0
    print('Test: {}'.format(test))
    cam = CameraFeed()
    cam.set_controls()
    cam.start_threads()
    cam.close()


if __name__ == "__main__":
    main()
