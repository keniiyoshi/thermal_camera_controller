"""
Created on Sun Dec  4 13:46:25 2022

@author: ken iiyoshi, Aimlab


Some more sample edits.

How to run (March 24, 2023):
    The program won't work if you try to compile through the IPython console. Run it from Anaconda's CMD.exe Prompt.
    Once it runs, open the mvGenTLProducer.cti file in the C:\Program Files\MATRIX VISION\mvIMPACT Acquire\bin\x64 folder.

site packages that I have edited in order to eliminate warnings and erros:
 C:\ProgramData\Anaconda3\envs\pycharmHarvesterPython3_7\Lib\site-packages\harvesters\core.py
 C:\ProgramData\Anaconda3\envs\pycharmHarvesterPython3_7\Lib\site-packages\harvesters_gui\frontend\pyqt5.py
 C:\ProgramData\Anaconda3\envs\pycharmHarvesterPython3_7\Lib\site-packages\harvesters_gui\_private\frontend\canvas.py
 C:\ProgramData\Anaconda3\envs\pycharmHarvesterPython3_7\Lib\site-packages\vispy\ext\six.py
 C:\ProgramData\Anaconda3\envs\pycharmHarvesterPython3_7\Lib\site-packages\vispy\gloo\program.py
 C:\ProgramData\Anaconda3\envs\pycharmHarvesterPython3_7\Lib\site-packages\vispy\gloo\glir.py
"""


import sys
from PyQt5.QtWidgets import QApplication
from harvesters_gui.frontend.pyqt5 import Harvester

if __name__ == '__main__':
    print("sys.argv = ",sys.argv)
    app = QApplication(sys.argv)
    h = Harvester()
    h.show()
    sys.exit(app.exec_()) # app.exec_()= 0 if it successfully finishes (by closing the harvester GUI)
