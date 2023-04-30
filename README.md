# thermal_camera_controller

Date: April 23, 2023.
Author: ken iiyoshi

The Thermal Camera Controller aims to calibrate the Gobi640 camera for dynamic thermomemechanical crystals characterizations, as use the camera for data recording and analysis, as well as controlling any heating setup for the crystals.

This markup aims to guide users on how to set up the environment for using this program.

While it is more convenient to interface the Gobi camera during the development for debugging, using the simulation camera should be sufficient for GUI development.

## Instructions
### Environment setup

1. Install Anaconda Navigator
2. Install Pycharm. Free education license provided for NYU students.
3. Create an anaconda environment under pycharm using Python 3.7
4. Setup the python command prompt for Pycharm. [This link](https://stackoverflow.com/questions/48924787/pycharm-terminal-doesnt-activate-conda-environment) might be helpful.
5. Download this project from gitHub and open it on PyCharm.
6. Connect the project to the original github project.
7. Using the command prompt, navigate to the project directory, and run `pip install -e lib/harvesters_gui_for_crystals-master` and  `pip install -e lib/harvesters_for_crystals-master`.
8. You should now be able to run the harvester.py program from PyCharm!
9. to connect to a camera, you need to input a cti file. For the Gobi camera, mvGenTLProducer.cti from MATRIX VISION is used. TLSimi.cti can be used to digitally simulate a camera, if no physical camera is available. [More on this](https://github.com/genicam/harvesters/wiki). It is probably more convenient to install this under the project directory as opposed to program files.

### Developing the program
1. if you only edit the main files in the root directly, you can run without the libraries. if you edit the library building, you would need to build by installing it through the command prompt. i.e   `pip install lib/harvesters_for_crystals-master;  pip install lib/harvesters_gui_for_crystals-master`. The code is built in the libs subfolders within the corresponding directories, and the installs are in the pycharm anaconda environment site-packages folder.
2. Since the code is run through the code installed in the site-package any breakpoints for debugging should be set in there. It's the exact copy of the code from the main repository.
3. periodically commit and push the project to github!

### Running the program

The main file is harvester.py,which is for interfacing with the gobi camera. xxx-harvester-TLSimu.py can be used for camera simulation. Some other files in the libraries, such as pyqt5.py, can be run directly for debugging purposes. You can ignore main.py for now.