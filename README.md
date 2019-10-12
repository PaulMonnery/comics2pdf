# comics2pdf
A script that converts comic files (cbr, cbz) to pdf, in python3. Works on Linux

## Getting Started

You can use it on a file or a directory, just specifie the input method via a flag:
```
python3 comic2pdf.py -d [path/to/directory]
```
Converts all files from the given directory
```
python3 comic2pdf.py -f [path/to/file]
```
Converts the given file

### Prerequisites

Script in Python 3.6 (probably won't work with Python 2.x versions). Requires the "zipfile36", "patool" and "pillow" (aka PIL) modules in order to work correctly. To install them run the following commands:

```
pip3 install zipfile36 patool pillow
```

### Installing

Install the required modules in a virtualenv to run it in while keeping the script in a specific folder, or install the module for your user and run:
```
chmod 755 comic2pdf.py
sudo mv comic2pdf.py /usr/bin/c2p
```

## Authors and Acknowledgments

* **MComas1**

Based on a python script by **bransorem** (https://github.com/bransorem/comic2pdf).
