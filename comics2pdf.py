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


def handle_rar(file_to_exctract, tmp_dir):
    try:
        os.mkdir(tmp_dir)
    except:
        print("Temporary folder already exists")
    print("Extracting pictures in the CBR file...")
    patoolib.extract_archive(file_to_exctract, outdir=tmp_dir)
    newfile = file_to_exctract.replace(file_to_exctract[-4:], ".pdf")
    print("Creating the PDF file...")
    to_pdf(newfile, tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print('\x1b[1;32m' + "\"" + newfile[:-4] + "\" successfully converted!" + '\x1b[0m')


def handle_zip(file_to_exctract, tmp_dir):
    zip_ref = zipfile.ZipFile(file_to_exctract, 'r')
    print("Extracting pictures in the CBZ file...")
    zip_ref.extractall(tmp_dir)
    zip_ref.close()
    newfile = file_to_exctract.replace(file_to_exctract[-4:], ".pdf")
    print("Creating the PDF file...")
    to_pdf(newfile, tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print('\x1b[1;32m' + "\"" + newfile[:-4] + "\" successfully converted!" + '\x1b[0m')


def get_files(f, dir):
    files = os.listdir(dir)
    for file in files:
        path = dir + separator() + file
        if os.path.isdir(path):
            get_files(f, path)
        else:
            f.append(path)


def to_pdf(filename, newdir):
    image_list = []
    get_files(image_list,  newdir)
    im_list = list()
    is_first_picture = True
    im = None
    index = 0
    list_len = len(image_list)

    for image in sorted(image_list):
        index += 1
        sys.stdout.flush()
        sys.stdout.write("Conversion: {0:.0f}%\r".format(index / list_len * 100))
        img = Image.open(image)
        try:
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(image, dpi=(96, 96))
        except:
            print("Error")

        if (is_first_picture):
            im = img
            is_first_picture = False
        else:
            im_list.append(img)
    print("Saving the PDF file...")
    im.save(filename, "PDF", resolution=100.0, save_all=True, append_images=im_list)
    shutil.rmtree(newdir, ignore_errors=True)


def launch_convert(file):
    tmp_dir = tmp_directory + separator() + "c2p" + separator()
    if (file[-4:] == '.cbz' or file[-4:] == '.zip'):
        handle_zip(file, tmp_dir)
    elif (file[-4:] == '.cbr' or file[-4:] == '.rar'):
        handle_rar(file, tmp_dir)


def opendir(directory):
    for file in sorted(os.listdir(directory)):
        launch_convert(directory + separator() + file)
    if False:
        print("WARNING: some items were skipped")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '-d' and os.path.isdir(sys.argv[2]):
            opendir(sys.argv[2])
        elif sys.argv[1] == '-f' and os.path.isfile(sys.argv[2]):
            launch_convert(sys.argv[2])
        else:
            print("Bad argument. Please use:\n\t-d [path/to/folder] to all \
            files in folder\n\t-f [path/to/file] to convert a single file")
    else:
        print("Please specifie arguments.\n\t-d [path/to/folder] to all \
        files in folder\n\t-f [path/to/file] to convert a single file")

if __name__ == "__main__":
    main()