#! /usr/bin/env python3

from distutils.core import setup

setup (name='djvubind',
      version='0.3.1',
      description='Creates djvu files with positional ocr, metadata, and bookmarks.',
      author='Adam Zajac',
      author_email='strider1551@gmail.com',
      url='https://code.google.com/p/djvubind/',
      license='GPL-3',
      py_modules=['djvubindlib/__init__', 'djvubindlib/ocr', 'djvubindlib/organizer', 'djvubindlib/utils'],
      data_files=[('share/man/man1', ['docs/djvubind.1.gz']),
                  ('bin', ['djvubind'])]
)
