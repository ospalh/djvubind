#! /usr/bin/env python

#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc.

import os
import shutil

import Djvubind.ocr
import Djvubind.utils

class Book:
    def __init__(self):
        self.pages = []
        self.cover = {}
        self.cover["front"] = None
        self.cover["back"] = None
        self.metadata = None
        self.bookmarks = None

    def insert_page(self, path):
        self.pages.append(Page(path))
        return None

class Page:
    def __init__(self, path):
        self.path = os.path.abspath(path)

        self.bitonal = self.is_bitonal()
        self.dpi = self.get_dpi()
        self.text = self.ocr()

    def get_dpi(self):
        dpi = Djvubind.utils.execute("identify -format '%x' {0} | awk '{{print $1}}'".format(self.path), capture=True)
        return int(dpi)

    def is_bitonal(self):
        if (Djvubind.utils.execute('identify -format %z "{0}"'.format(self.path), capture=True) != b'1\n'):
            return False
        else:
            return True

    def ocr(self):
        if self.path.split('.')[-1] in ['jpg', 'jpeg']:
            Djvubind.utils.execute('convert "{0}" "{0}.tif"'.format(self.path))
            text = Djvubind.ocr.get_text(self.path+'.tif')
            os.remove(self.path+'.tif')
        elif self.path.split('.')[-1] == 'tiff':
            shutil.copy2(self.path, self.path+'.tif')
            text = Djvubind.ocr.get_text(self.path+'.tif')
            os.remove(self.path+'.tif')
        elif self.path.split('.')[-1] == 'tif':
            text = Djvubind.ocr.get_text(self.path)
        else:
            text =  ''

        return text
