
from harvesters.core import Harvester

import numpy as np

import matplotlib

from harvesters.util.pfnc import mono_location_formats, \
    rgb_formats, bgr_formats, \
    rgba_formats, bgra_formats


print('running TLSimu...')

h = Harvester()

# ATTENTION! Please use the CTI file in the original location!

# Why? Visit https://github.com/genicam/harvesters/wiki/FAQ and
# read "I pointed out a CTI file but Harvester says the image doesn't
# exist (Part 2)."s

# h.add_file('C:\\Users\\Aimlab\\AppData\\Roaming\\Python\\Python39\\site-packages\\genicam\\TLSimu.cti')

# print('C:\\Users\\Aimlab\\AppData\\Roaming\\Python\\Python39\\site-packages\\genicam\\TLSimu.cti')
#
# h.add_file('C:\\Users\\Aimlab\\AppData\\Roaming\\Python\\Python39\\site-packages\\genicam\\TLSimu.cti')


print('C:\\ProgramData\\Anaconda3\\envs\\pycharmHarvesterPython3_7\\Lib\\site-packages\\genicam\\TLSimu.cti')

h.add_file('C:\\ProgramData\\Anaconda3\\envs\\pycharmHarvesterPython3_7\\Lib\\site-packages\\genicam\\TLSimu.cti')

# print('C:\\Program Files\\MATRIX VISION\\mvIMPACT Acquire\\bin\\x64\\mvGenTLProducer.cti')

# h.add_file('C:\\Program Files\\MATRIX VISION\\mvIMPACT Acquire\\bin\\x64\\mvGenTLProducer.cti')

h.update()



# print('C:\\Windows\\System32\\mvGenTLConsumer.dll')

# h.add_file('C:\\Windows\\System32\\mvGenTLConsumer.dll')

# h.add_file('bar.cti')

# print(h.files)

print(len(h.device_info_list))

print(h.device_info_list[0])
# print(h.device_info_list[1])
print(h.device_info_list[2])
# print(h.device_info_list[3])
ia = h.create(0)

# works
# ia = h.create({'serial_number': 'SN_InterfaceA_0'})

# requires size modification to work.
# ia = h.create({'serial_number': 'SN_InterfaceA_1'})

# works
# ia = h.create({'serial_number': 'SN_InterfaceB_0'})

# requires size modification to work.
# ia = h.create({'serial_number': 'SN_InterfaceB_1'})


ia.remote_device.node_map.Width.value = 8

ia.remote_device.node_map.Height.value = 8

ia.remote_device.node_map.PixelFormat.value = 'Mono8'

ia.start()

with ia.fetch() as buffer:
    
    # Let's create an alias of the 2D image component:
    component = buffer.payload.components[0]
    
    # Note that the number of components can be vary. If your
    # target remote device transmits a multi-part information, then
    # you'd get two or more components in the payload. However, now
    # we're working with a remote device that transmits only a 2D image.
    # So we manipulate only index 0 of the list object, components.
    
    # Let's see the acquired data in 1D:
    # ken. nice! it's already in numpy format!
    _1d = component.data
    print('1D: {0}'.format(_1d))
    
    # Reshape the NumPy array into a 2D array:
    _2d = component.data.reshape(
        component.height, component.width
    )
    print('2D: {0}'.format(_2d))
    
    # Here are some trivial calculations:
    print(
        'AVE: {0}, MIN: {1}, MAX: {2}'.format(
            np.average(_2d), _2d.min(), _2d.max()
        )
    )
    payload = buffer.payload
    component = payload.components[0]
    width = component.width
    height = component.height
    data_format = component.data_format
    
    # pixel_location = component.represent_pixel_location()
    rgb_2d = np.zeros(shape=(height, width, 3), dtype='uint8')

    # Reshape the image so that it can be drawn on the VisPy canvas:
    if data_format in mono_location_formats:
        content = component.data.reshape(height, width)
    else:
        # The image requires you to reshape it to draw it on the
        # canvas:
        if data_format in rgb_formats or \
                data_format in rgba_formats or \
                data_format in bgr_formats or \
                data_format in bgra_formats:
            #
            content = component.data.reshape(
                height, width,
                int(component.num_components_per_pixel)  # Set of R, G, B, and Alpha
            )
            #
            if data_format in bgr_formats:
                # Swap every R and B:
                content = content[:, :, ::-1]
        # else:
        #     return
        
        
    


ia.stop()

ia.destroy()


# h.remove_file('C:\\Program Files\\MATRIX VISION\\mvIMPACT Acquire\\bin\\x64\\mvGenTLProducer.cti')

h.reset() # without this, the camera will not be detected for future runs, under which case spyder needs to be restarted.


