# comics2pdf
A script and GUI that converts comic files (cbr, cbz) to pdf, in python3 for Linux

![alt text](screenshot_GUI.png "GUI screenshot")


## Getting Started

You can use the script on a file or a directory, just specify the input method via a flag:
```bash
./comics2pdf.py -d [path/to/directory] #Converts all files from the given directory
./comics2pdf.py -f [path/to/file]      #Converts the given file
./comics2pdf_gui.py                    #Launch the program's GUI
```


### Prerequisites

Script in Python 3.6 (probably won't work with Python 2.x versions). Requires the "zipfile36", "patool" and "pillow" (aka PIL) modules in order to work correctly. To install them run the following commands:

```
pip3 install zipfile36 patool pillow
```

PyQt5 is needed to run the GUI

```
pip3 install PyQt5
```

### Installing

Install the required modules in a virtualenv to run it in while keeping the script in a specific folder, or install the module for your user and run:
```
chmod 755 comics2pdf.py
chmod 755 comics2pdf_gui.py
sudo mv comics2pdf.py /usr/bin/c2p
sudo mv comics2pdf_gui.py /usr/bin/c2p_gui
```

## Authors and Acknowledgments

* **MComas1**

Based on a python script by **bransorem** (https://github.com/bransorem/comic2pdf).
