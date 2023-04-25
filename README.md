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
7. Using the command prompt, navigate to the project directory, and run `pip install -e lib/harvesters_gui_for_crystals` and  `pip install -e lib/harvesters_for_crystals`.
8. You should now be able to run the harvester.py program from PyCharm!
9. to connect to a camera, you need to input a cti file. For the Gobi camera, mvGenTLProducer.cti from MATRIX VISION is used. TLSimi.cti can be used to digitally simulate a camera, if no physical camera is available. [More on this](https://github.com/genicam/harvesters/wiki). It is probably more convenient to install this under the project directory as opposed to program files.

### Developing the program
1. if you only edit the main files in the root directly, you can run without the libraries. if you edit the library building, you would need to build by installing it through the command prompt. i.e   `pip install lib/harvesters_for_crystals-master;  pip install lib/harvesters_gui_for_crystals-master`. The code is built in the libs subfolders within the corresponding directories, and the installs are in the pycharm anaconda environment site-packages folder.
 
2. periodically commit and push the project to github!