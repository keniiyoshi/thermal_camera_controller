#!/usr/bin/env python3
# ----------------------------------------------------------------------------
#
# Copyright 2018 EMVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ----------------------------------------------------------------------------


# Standard library imports

# Related third party imports

import numpy as np

from vispy import gloo
from vispy import app
from vispy.gloo import Program
from vispy.util.transforms import ortho

from genicam.gentl import PAYLOADTYPE_INFO_IDS
from genicam.gentl import TimeoutException

# Local application/library specific imports
from harvesters._private.core.helper.system import is_running_on_macos
from harvesters.util.pfnc import is_custom, get_bits_per_pixel, \
    bgr_formats
from harvesters.util.pfnc import mono_location_formats, \
    rgb_formats, bgr_formats, \
    rgba_formats, bgra_formats, \
    bayer_location_formats


class CanvasBase(app.Canvas):
    def __init__(
            self, *,
            image_acquirer=None,
            width=640, height=480,
            display_rate=30.,
            background_color='gray',
            vsync=True
    ):
        """
        As far as we know, Vispy refreshes the canvas every 1/30 sec at the
        fastest no matter which faster number is specified. If we set any
        value which is greater than 30, then Vispy's callback is randomly
        called.
        """

        #
        app.Canvas.__init__(
            self, size=(width, height), vsync=vsync, autoswap=True
        )

        #
        self._ia = image_acquirer

        #
        self._background_color = background_color
        self._has_filled_texture = False
        self._width, self._height = width, height

        #
        self._is_dragging = False

        # If it's True, the canvas keeps image acquisition but do not
        # draw images on the canvas:
        self._pause_drawing = False

        #
        self._origin = [0, 0]

        #
        self._display_rate = display_rate
        self._timer = app.Timer(
            1. / self._display_rate, connect=self.update, start=True
        )

        #
        self._buffers = []

        self._static_arr2 = np.loadtxt("./../../data/sample-vignette-may3.csv", delimiter=",", dtype=np.uint16)
        self._static_arr3 = np.loadtxt("./../../data/sample-noise-may5.csv", delimiter=",", dtype=np.uint16)

    @property
    def display_rate(self):
        return self._display_rate

    @display_rate.setter
    def display_rate(self, value):
        self._display_rate = value
        self._timer.stop()
        self._timer.start(interval=1./self._display_rate)

    def set_canvas_size(self, width, height):
        #
        self._has_filled_texture = False

        #
        updated = False

        #
        if self._width != width or self._height != height:
            self._width = width
            self._height = height
            updated = True

        #
        if updated:
            self.apply_magnification()

    def on_draw(self, event):



        # static_arr2 = np.loadtxt("./../../data/sample-vignette-may3.csv", delimiter = ",", dtype = np.uint16)

        # Update on June 15th, 2018:
        # According to a VisPy developer, they have not finished
        # porting VisPy to PyQt5. Once they finished the development
        # we should try it out if it gives us the maximum refresh rate.
        # See the following URL to check the latest information:
        #
        #     https://github.com/vispy/vispy/issues/1394

        # Clear the canvas in gray.
        gloo.clear(color=self._background_color)

        drew = False
        try:
            if not self._pause_drawing:
                # Fetch a buffer.
                buffer = self.ia.fetch(timeout=0.0001)

                # Prepare a texture to draw:
                self._prepare_texture(buffer,self._static_arr2)

                # Draw the texture until the buffer object exists
                # within this scope:
                # (We keep the buffer until the next one is delivered to
                # keep the current chunk data alive but it depends on the
                # application; we just want to tell you that the texture
                # must be overdrawn until the content is alive:)
                self._draw()

                # Release the buffers that we've kept holding so far:
                self.release_buffers()

                # We have drawn the latest image on the canvas:
                drew = True

                # Keep the buffer alive to keep the chunk data alive until
                # the next one is delivered:
                self._buffers.append(buffer)

        except AttributeError:
            # Calling fetch_buffer() raises AttributeError because
            # the ImageAcquirer object is None.
            pass
        except TimeoutException:
            # We have an ImageAcquirer object but nothing has
            # been fetched, wait for the next round:
            pass

        # Draw the latest texture again if needed:
        if not drew:
            self._draw()

    def release_buffers(self):
        for _buffer in self._buffers:
            if _buffer:
                _buffer.queue()
        self._buffers.clear()

    def _draw(self):
        raise NotImplementedError

    def on_resize(self, event):
        self.apply_magnification()

    def apply_magnification(self):
        raise NotImplementedError

    def on_mouse_wheel(self, event):
        raise NotImplementedError

    def on_mouse_press(self, event):
        self._is_dragging = True
        self._origin = event.pos

    def on_mouse_release(self, event):
        self._is_dragging = False

    def on_mouse_move(self, event):
        raise NotImplementedError

    def pause_drawing(self, pause=True):
        self._pause_drawing = pause

    def toggle_drawing(self):
        self._pause_drawing = False if self._pause_drawing else True

    def is_pausing(self):
        return True if self._pause_drawing else False

    def resume_drawing(self):
        self._pause_drawing = False

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color

    @property
    def ia(self):
        return self._ia

    @ia.setter
    def ia(self, value):
        self._ia = value

    def _prepare_texture(self, buffer):
        raise NotImplementedError


class Canvas2D(CanvasBase):
    _visible_payloads = [
        PAYLOADTYPE_INFO_IDS.PAYLOAD_TYPE_IMAGE,
        PAYLOADTYPE_INFO_IDS.PAYLOAD_TYPE_CHUNK_DATA,
        PAYLOADTYPE_INFO_IDS.PAYLOAD_TYPE_MULTI_PART,
    ]

    def __init__(
            self, *,
            image_acquirer=None,
            width=640, height=480,
            background_color='gray',
            vsync=True, display_rate=30.
    ):
        #
        super().__init__(
            image_acquirer=image_acquirer,
            width=width, height=height,
            display_rate=display_rate,
            background_color=background_color,
            vsync=vsync
        )

        #
        self._vertex_shader = """
            // Uniforms
            uniform mat4 u_model;
            uniform mat4 u_view;
            uniform mat4 u_projection;

            // Attributes
            attribute vec2 a_position;
            attribute vec2 a_texcoord;

            // Varyings
            varying vec2 v_texcoord;

            // Main
            void main (void)
            {
                v_texcoord = a_texcoord;
                gl_Position = u_projection * u_view * u_model * vec4(a_position, 0.0, 1.0);
            }
        """

        self._fragment_shader = """
            varying vec2 v_texcoord;
            uniform sampler2D texture;
            void main()
            {
                gl_FragColor = texture2D(texture, v_texcoord);
            }
        """

        #
        self._program = None
        self._data = None
        self._coordinate = None
        self._translate = 0.
        self._latest_translate = self._translate
        self._magnification = 1.

        # Apply shaders.
        self._program = Program(
            self._vertex_shader, self._fragment_shader, count=4
        )

        #
        self._data = np.zeros(
            4, dtype=[
                ('a_position', np.float32, 2),
                ('a_texcoord', np.float32, 2)
            ]
        )

        #
        self._data['a_texcoord'] = np.array(
            [[0., 1.], [1., 1.], [0., 0.], [1., 0.]]
        )

        #
        self._program['u_model'] = np.eye(4, dtype=np.float32)
        self._program['u_view'] = np.eye(4, dtype=np.float32)

        #
        self._coordinate = [0, 0]


        #
        self._program['texture'] = np.zeros(
            (self._height, self._width), dtype='uint8'
        )
        self._temperature = np.zeros(
            (self._height, self._width), dtype=np.float32
        )

        #
        self.apply_magnification()

    def _prepare_texture(self, buffer, static_arr):

        update = True
        if buffer.payload_type not in self._visible_payloads:
            update = False

        # Set the image as the texture of our canvas.
        if buffer:
            #
            payload = buffer.payload
            component = payload.components[0]
            width = component.width
            height = component.height

            # Update the canvas size if needed.
            self.set_canvas_size(width, height)

            #
            exponent = 0
            data_format = None

            #
            data_format_value = component.data_format_value
            if is_custom(data_format_value):
                update = False
            else:
                data_format = component.data_format
                bpp = get_bits_per_pixel(data_format)
                if bpp is not None:
                    exponent = bpp - 8
                else:
                    update = False

            if update:
                # Reshape the image so that it can be drawn on the
                # VisPy canvas:
                if data_format in mono_location_formats or \
                        data_format in bayer_location_formats:
                    # Reshape the 1D NumPy array into a 2D so that VisPy
                    # can display it as a mono image:
                    content = component.data.reshape(height, width)
                else:
                    # The image requires you to reshape it to draw it on the
                    # canvas:
                    if data_format in rgb_formats or \
                            data_format in rgba_formats or \
                            data_format in bgr_formats or \
                            data_format in bgra_formats:
                        # Reshape the 1D NumPy array into a 2D so that VisPy
                        # can display it as an RGB image:
                        content = component.data.reshape(
                            height, width,
                            int(component.num_components_per_pixel)
                        )
                        #
                        if data_format in bgr_formats:
                            # Swap every R and B so that VisPy can display
                            # it as an RGB image:
                            content = content[:, :, ::-1]
                    else:
                        return

                # Convert each data to an 8bit.
                if exponent > 0:
                    # The following code may affect to the rendering
                    # performance:
                    # content = (content / (2 ** exponent))
                    # ken edit:
                    # content = 2*12*((content / (2 ** exponent)) - 114 * np.ones((height, width)))


                    # ken: probably add vignette removal function here. divide by value/min
                    def remove_vignette(value,arr):

                        # mask = value - raw_min * np.ones((height, width)))

                        # arr = np.loadtxt("./../../data/sample-vignette-may3.csv", delimiter = ",", dtype = np.uint16)

                        # # Figure out how 'wide' each range is
                        # leftSpan = np.divide(value,(np.divide(arr,np.min(arr))))
                        # rightSpan = rightMax - rightMin
                        #
                        # # Convert the left range into a 0-1 range (float)
                        # valueScaled = (value - raw_min * np.ones((height, width))) / float(leftSpan)

                        # Convert the 0-1 range into a value in the right range.
                        return np.divide(value,(np.divide(arr,np.min(arr))))

                    content = remove_vignette(content, static_arr)
                    content = remove_vignette(content, self._static_arr3)

                    def ADUtoTemp(array):
                        room_temp = 23.0 # default temperature
                        # got push test feb 23 , 2024
                        # determine what pixel value corresponds to default temperature.
                        # between the room temperature min max of [26395.9,26908.99] after noise removal, at focused distance for peltier cell.
                        # so there is a range depending on the reflectiveness of the material!
                        # it will probably be better to use ADU (analog digital unit) from a non-reflective material.
                        # this is analogous to measuring temperature at a shady, dark space.
                        # For reference, at focused distance, the foam gives a range of [26452.0,26815.9] after noise removal, so a value f
                        # from here should be used.
                        # Noe that these four values correspond to [40.2%, 41.1%] and [40.3%,40.9%]
                        # just pick 26600 for now, it's around the mid-point
                        room_temp_ADU = 26600.0

                        # the following is based on data from "ice-cup-and-boiling-water-kettle-apr29-calibrated-data.png"
                        # picked min and max data for freezing and boiling temperature respectively.
                        # sample_temp = 56.3
                        # sample_temp_ADU = 29958
                        # calculation based on simple linear model: pix = 95.24*temp + 24666.67
                        boil_temp = 100.0
                        boil_temp_ADU = 34190

                        ice_temp = 1.0
                        ice_temp_ADU = 24796

                        # for each pixel, scale the ADU value into temperature values using the following formulat:
                        # temperature = 0.0105*ADU -259


                        return  0.0105*array - 259.0*np.ones((height, width)) + 2.3*np.ones((height, width))

                    self._temperature = ADUtoTemp(content)

                    # for viewing on the debugger
                    test = self._temperature

                    def translate(value, leftMin, leftMax, rightMin, rightMax):
                        # Figure out how 'wide' each range is
                        leftSpan = leftMax - leftMin
                        rightSpan = rightMax - rightMin

                        # Convert the left range into a 0-1 range (float)
                        valueScaled = (value - leftMin * np.ones((height, width))) / float(leftSpan)

                        # Convert the 0-1 range into a value in the right range.
                        return rightMin * np.ones((height, width)) + (valueScaled * rightSpan)



                    content = translate(content, np.min(content), np.max(content), 0.0, 255.0)

                    # Then cast each array element to an uint8:
                    content = content.astype(np.uint8)

                    # Ken edit for editing display image.
                    # new_content = 6 * (content - 100 * np.ones((height, width)))
                    # new_content_formatted = new_content.astype(np.uint8)
                    # print('test\n')

                    # section for checking temperature value within the debugger.





                # self._program['texture'] = new_content_formatted
                self._program['texture'] = content





    def _draw(self):
        self._program.draw('triangle_strip')

    def apply_magnification(self):
        #
        canvas_w, canvas_h = self.physical_size
        gloo.set_viewport(0, 0, canvas_w, canvas_h)

        #
        ratio = self._magnification
        w, h = self._width, self._height

        self._program['u_projection'] = ortho(
            self._coordinate[0],
            canvas_w * ratio + self._coordinate[0],
            self._coordinate[1],
            canvas_h * ratio + self._coordinate[1],
            -1, 1
        )

        x, y = int((canvas_w * ratio - w) / 2), int((canvas_h * ratio - h) / 2)  # centering x & y

        #
        self._data['a_position'] = np.array(
            [[x, y], [x + w, y], [x, y + h], [x + w, y + h]]
        )

        #
        self._program.bind(gloo.VertexBuffer(self._data))

    def on_mouse_wheel(self, event):
        self._translate += event.delta[1]
        power = 7. if is_running_on_macos() else 5.  # 2 ** exponent
        stride = 4. if is_running_on_macos() else 7.
        translate = self._translate
        translate = min(power * stride, translate)
        translate = max(-power * stride, translate)
        self._translate = translate
        self._magnification = 2 ** -(self._translate / stride)
        if self._latest_translate != self._translate:
            self.apply_magnification()
            self._latest_translate = self._translate

    def on_mouse_move(self, event):
        if self._is_dragging:
            adjustment = 2. if is_running_on_macos() else 1.
            ratio = self._magnification * adjustment
            delta = event.pos - self._origin
            self._origin = event.pos
            self._coordinate[0] -= (delta[0] * ratio)
            self._coordinate[1] += (delta[1] * ratio)
            self.apply_magnification()

