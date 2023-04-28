'''
Created on 9.11.2016

@author: Samuli Rahkonen
'''

import xevacam.camera as camera
# import matplotlib
# import pylab  # Shows the figure in Eclipse + PyDev
# from ctypes import create_string_buffer, c_char_p
# import numpy as np
import io
import xevacam.utils as utils
import xevacam.streams as streams


'''
def image(stream, size, dims, pixel_size_bytes):
    while True:
        img = stream.read(size)
        if img == b'':
            continue
        break
    frame_buffer = np.frombuffer(img, dtype='u%d' % pixel_size_bytes, count=int(frame_size/2))
    frame_buffer = np.reshape(frame_buffer, frame_dims)
    return frame_buffer
'''


if __name__ == '__main__':
    # cam = camera.XevaCam(calibration='C:\\MyTemp\\envs\\xevacam\\Lib\\site-packages\\3ms_196_xeneth3.xca')
    # print('C:\\Program Files\\Xeneth\\Calibrations\\XR[-20-120]-18mm-(29-05-2018)_10551.xca')
    cam = camera.XevaCam(calibration='C:\\Program Files\\Xeneth\\Calibrations\\XR[-20-120]-18mm-(29-05-2018)_10551.xca')
    # cam = camera.XevaCam()
    # print('C:\\Program Files\\Xeneth\\Calibrations\\nov30-test1-1130-30us_10551.xca')
    # cam = camera.XevaCam(calibration='C:\\Program Files\\Xeneth\\Calibrations\\nov30-test1-1130-30us_10551.xca')

    # # Open connection to camera
    # with cam.opened() as c:
    #     # Create a window and connect it to the camera output
    #     # Line scanner view. Show 30th line in the frame (30th band in data cube)
    #     window = utils.LineScanWindow(cam, 30)
    #     c.start_recording()
    #     window.show()  # Show it
    #     c.wait_recording(5)
    #     meta = c.stop_recording()

    # stream = streams.XevaStream()
    file_stream = open('./../../../../data/xevacam/myfile.bin', 'wb')
    # bytes_stream = io.BytesIO()

    # cam.set_handler(stream)
    cam.set_handler(file_stream)
    # cam.set_handler(bytes_stream)
    # cam.set_handler(preview_stream)
    with cam.opened(sw_correction=True) as c:
        window = utils.LineScanWindow(cam, 30)
        c.start_recording()
        window.show()
        c.wait_recording(5)
        meta = c.stop_recording()

        utils.create_envi_hdr(meta, 'myfile.hdr')
    # window.close()
    # from xevacam.envi import ENVIImage
    # with ENVIImage('myfile.bin').open() as img:
    #     print(img.read_numpy_array())

    # window.wait()
    # input('Press enter')
