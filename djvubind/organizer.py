#! /usr/bin/env python3

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
"""
Data structures to organize collect and abstract information.
"""

import os
import sys

from . import utils

class Book:
    """
    Contains all information regarding the djvu ebook that will be produced.
    """

    def __init__(self):
        self.pages = []
        self.suppliments = {'cover_front':None,
                            'cover_back':None,
                            'metadata':None,
                            'bookmarks':None}
        self.dpi = None

    def get_dpi(self):
        """
        Sets the book's dpi based on the dpi of the individual pages.  Pretty much
        only used by minidjvu.
        """

        for page in self.pages:
            if (self.dpi is not None) and (page.dpi != self.dpi):
                print("msg: [organizer.Book.analyze()] {0}".format(page.path))
                print("     Page dpi is different from the previous page.", file=sys.stderr)
                print("     If you encounter problems with minidjvu, this is probably why.", file=sys.stderr)
            self.dpi = page.dpi

        return None

    def insert_page(self, path):
        """
        Add an image to the book.
        """

        self.pages.append(Page(path))
        return None

    def save_report(self):
        """
        Saves a diagnostic report of the book in csv format.
        """

        with open('book.csv', 'w', encoding='utf8') as handle:
            handle.write('Path, Bitonal, DPI, Title, OCR\n')
            for page in self.pages:
                entry = [page.path, str(page.bitonal), str(page.dpi), str(page.title), str(len(page.text))]
                entry = ", ".join(entry)
                handle.write(entry)
                handle.write('\n')

        return None

class Page:
    """
    Contains information relevant to a single page/image.
    """

    def __init__(self, path):
        self.path = os.path.abspath(path)

        self.bitonal = None
        self.dpi = 0
        self.text = ''
        self.title = None

    def get_dpi(self):
        """
        Find the resolution of the image.
        """
        resolution = utils.execute('identify -ping -format %x "{0}"'.format(
            self.path), capture=True).decode('ascii').split(' ')
        if resolution[1] == 'PixelsPerInch':
            self.dpi = int(resolution[0])
        elif resolution[1] == 'PixelsPerCentimeter':
            self.dpi = round(float(resolution[0]) * 2.54)
        else:
            raise ValueError(
                'Unknown image resolution unit "{0}"'.format(resolution[0]))

    def is_bitonal(self):
        """
        Check if the image is bitonal.
        """

        if utils.execute('identify -ping "{0}"'.format(self.path), capture=True).decode('utf8').find('1-bit') == -1:
            self.bitonal = False
        else:
            if int(utils.execute('identify -ping -format %z "{0}"'.format(
                    self.path), capture=True).decode('utf8')) != 1:
                print("msg: {0}: Bitonal image but with a depth greater than 1.  Modifying image depth.".format(os.path.split(self.path)[1]))
                utils.execute('mogrify -colorspace gray -depth 1 "{0}"'.format(self.path))
            self.bitonal = True

        if (self.path[-4:].lower() == '.pgm') and (self.bitonal is True):
            msg = utils.color("wrn: {0}: Bitonal image but using a PGM format instead of PBM. Tesseract might get mad!".format(os.path.split(self.path)[1]), 'red')
            print(msg, file=sys.stderr)
        return None
