#!/usr/bin/env python3
# Converts .cbr and .cbz files to .pdf
# Author: PaulMonnery
# Forked from:  MComas1
# License:  You can do what you want with it.
# Mainly based on a script by Bransorem (https://github.com/bransorem/comic2pdf)

import os
import sys
import zipfile
import patoolib
from PIL import Image
import PIL.ExifTags
import shutil
import tempfile
import platform

tmp_directory = tempfile.gettempdir()
current_os = platform.system()

def separator():
    if current_os == 'Windows':
        return ('\\')
    else:
        return ('/')


def handle_rar(filein):
    tmp_dir = tmp_directory + separator() + "c2p" + separator()
    os.mkdir(tmp_dir)
    print("Extracting pictures in the CBR file...")
    patoolib.extract_archive(filein, outdir=tmp_dir)
    newfile = filein.replace(filein[-4:], ".pdf")
    print("Creating the PDF file...")
    to_pdf(newfile, tmp_dir, 7)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print('\x1b[1;32m' + "\"" + newfile[:-4] + "\" successfully converted!" + '\x1b[0m')


def handle_zip(filein):
    tmp_dir = tmp_directory + separator() + "c2p" + separator()
    zip_ref = zipfile.ZipFile(filein, 'r')
    print("Extracting pictures in the CBZ file...")
    zip_ref.extractall(tmp_dir)
    zip_ref.close()
    newfile = filein.replace(filein[-4:], ".pdf")
    print("Creating the PDF file...")
    to_pdf(newfile, tmp_dir, 0)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print('\x1b[1;32m' + "\"" + newfile[:-4] + "\" successfully converted!" + '\x1b[0m')


def to_pdf(filename, newdir, ii):
    ffiles = os.listdir(newdir)
    if (len(ffiles) == 1):
        to_pdf(filename, newdir + ffiles[0] + separator(), ii)
    else:
        im_list = list()
        firstP = True
        im = None
        index = 0
        list_len = len(ffiles)
        for image in sorted(ffiles):
            index += 1
            sys.stdout.flush()
            sys.stdout.write("Conversion: {0:.0f}%\r".format(
                index / list_len * 100))
            if (image.endswith(".jpg") or image.endswith(".JPG")
            or image.endswith(".jpeg") or image.endswith(".JPEG")):
                im1 = Image.open(newdir + image)
                try:
                    im1.save(newdir + image, dpi=(96, 96))
                except:
                    print("Error")

                if (firstP):
                    im = im1
                    firstP = False
                else:
                    im_list.append(im1)
            else:
                continue
        print("Saving the PDF file...")
        im.save(filename, "PDF", resolution=100.0, save_all=True, append_images=im_list)
        shutil.rmtree(newdir, ignore_errors=True)


def launch_convert(file):
    if (file[-4:] == '.cbz' or file[-4:] == '.zip'):
        handle_zip(file)
    elif (file[-4:] == '.cbr' or file[-4:] == '.rar'):
        handle_rar(file)


def opendir(directory):
    for file in sorted(os.listdir(directory)):
        launch_convert(directory + separator() + file)
    if False:
        print("WARNING: some items were skipped")


def start():
    if len(sys.argv) > 1:
        if sys.argv[1] == '-d' and os.path.isdir(sys.argv[2]):
            opendir(sys.argv[2])
        elif sys.argv[1] == '-f' and os.path.isfile(sys.argv[2]):
            launch_convert(sys.argv[2])
        else:
            print("Bad argument. Please use:\n\t-d [path/to/folder] to all files in folder\n\t-f [path/to/file] to convert a single file")
    else:
        print("Please specifie arguments.\n\t-d [path/to/folder] to all files in folder\n\t-f [path/to/file] to convert a single file")

start()