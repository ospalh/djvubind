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
Common and simple functions that are used throughout everything else.
"""


import multiprocessing
import os
import random
import shlex
import string
import subprocess
import sys


roman_numeral_map = (('m',  1000), ('cm', 900), ('d',  500),
                     ('cd', 400), ('c',  100), ('xc', 90),
                     ('l',  50), ('xl', 40), ('x',  10),
                     ('ix', 9), ('v',  5), ('iv', 4), ('i',  1))
html_codes = (['&', '&amp;'],['<', '&lt;'],['>', '&gt;'],['"', '&quot;'])


class ChangeDirectory(object):
    """
    Context manager that makes a temporary change the working directory.
    """

    def __init__(self, directory):
        self._dir = directory
        self._cwd = os.getcwd()
        self._pwd = self._cwd

    @property
    def current(self):
        return self._cwd

    @property
    def previous(self):
        return self._pwd

    @property
    def relative(self):
        c = self._cwd.split(os.path.sep)
        p = self._pwd.split(os.path.sep)
        l = min(len(c), len(p))
        i = 0
        while i < l and c[i] == p[i]:
            i += 1
        out = os.path.join(*(['.'] + (['..'] * (len(c) - i)) + p[i:]))
        return os.path.normpath(out)

    def __enter__(self):
        self._pwd = self._cwd
        os.chdir(self._dir)
        self._cwd = os.getcwd()
        return self

    def __exit__(self, *args):
        os.chdir(self._pwd)
        self._cwd = self._pwd


def arabic_to_roman(number):
    """
    convert arabic integer to roman numeral
    """

    roman = ''
    for numeral, integer in roman_numeral_map:
        while number >= integer:
            roman = roman + numeral
            number = number - integer
    return roman

def color(text, color_name):
    """
    Change the text color by adding ANSI escape sequences.
    """

    # Don't bother on the windows platform.
    if sys.platform.startswith('win'):
        return text

    colors = {}
    colors['pink'] = '\033[95m'
    colors['blue'] = '\033[94m'
    colors['green'] = '\033[92m'
    colors['yellow'] = '\033[93m'
    colors['red'] = '\033[91m'
    end = '\033[0m'

    if color_name in colors.keys():
        text = colors[color_name] + text + end

    return text

def counter(start=0, end=None, incriment=1, roman=False):
    """
    Basic generator that increases the return with each call.  The return is a string.
    """

    current = start - incriment

    while (end is None) or (current < end):
        current = current + incriment
        if roman:
            yield arabic_to_roman(current)
        else:
            yield str(current)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """
    Creates a random string of ascii numbers and digits. Useful for making
    identifies for temporary files.
    """

    return ''.join(random.choice(chars) for _ in range(size))

def replace_html_codes(text):
    """
    Replaces html ampersand codes (e.g. &gt;) with their actual character (e.g. >)
    """

    for code in html_codes:
        text = text.replace(code[1], code[0])

    return text

def split_cmd(start, files, end=''):
    """
    Rumor has it that Windows has a character limit of a little more than 32,000 for commands.[1]
    Linux seems to vary based on kernel settings and whatnot, but tends to be more in the millions.[2]
    Supposing the images are named 'page_0001.tif', we can hit the windows limit very quickly.  For the
    sake of being safe, we will split things up at the 32,000 mark.

    [1] http://stackoverflow.com/questions/2381241/what-is-the-subprocess-popen-max-length-of-the-args-parameter
    [2] http://www.linuxjournal.com/article/6060
    """
    #print(cmd)
    # Ah, this function is rather silly. Keep it anyway. RAS 2019-05-04
    print("splitting “{}”, “{}”, “{}”".format(start, files, end))
    cmds = []
    start = start + ' '
    end = ' ' + end
    buffer = start
    while len(files) > 0:
        if len(buffer) + len(files[0]) + len(end) + 3 < 32000:
            buffer = buffer + ' "' + files.pop(0) + '"'
        else:
            buffer = buffer + end.rstrip()
            cmds.append(buffer)
            buffer = start
    buffer = buffer + end.rstrip()
    cmds.append(buffer)
    return cmds

def simple_exec(cmd):
    """
    Execute a simple command.  Any output disregarded and exit status is
    returned.
    """
    # print("executing “{}”".format(cmd))
    return subprocess.call(shlex.split(cmd))


def execute(cmd):
    """
    Execute a command line process.  Includes the option of capturing output,
    and checks for successful execution.
    """
    # print("executing “{}”".format(cmd))
    return subprocess.check_output(shlex.split(cmd))
    # N.B.: The call may throw a CalledProcessError. Old code was to
    # explicitly check the return code and then do sys.exit. Following
    # the principle of never cathing an exception we can”t handle we
    # just let the program blow up on its own. Maybe we should catch,
    # print cmd and raise == crash.

    # Also, when we called this with catpure=False we explicitly
    # (why?) returned None. If you’re not interested in the output,
    # just don’t look at it.

def list_files(directory='.', contains=None, extension=None):
    """Find all files in a given directory that match criteria."""

    contents = []
    for path in os.listdir(directory):
        path = os.path.join(directory, path)
        if (contains is not None) and (contains not in path):
            continue
        if (extension is not None) and (not path.endswith(extension)):
            continue
        contents.append(path)
    contents.sort()

    return contents

def is_executable(command):
    """
    Checks if a given command is available.  Handy for dependency checks on external commands.
    """

    if get_executable_path(command) is not None:
        return True
    else:
        return False


def get_executable_path(command):
    """
    Checks if a given command is available and returns the path to the executable (if available).
    """

    # Add extension if on the windows platform.
    if sys.platform.startswith('win'):
        pathext = os.environ['PATHEXT']
    else:
        pathext = ''

    for path in os.environ['PATH'].split(os.pathsep):
        if os.path.isdir(path):
            for ext in pathext.split(os.pathsep):
                name = os.path.join(path, command + ext)
                if (os.access(name, os.X_OK)) and (not os.path.isdir(name)):
                    return name

    return None

def parse_config(filename):
    """
    Returns a dictionary of config/value pairs from a simple config file without
    sections or the other complexities of the builtin ConfigParser.
    """

    options = {}

    with open(filename) as handle:
        for line in handle:

            line = line.strip()

            # Remove comments.  Note that in-line comments are not handled and
            # will probaly screw something up.
            if line.startswith('#'):
                line = ''

            # Store option/value pairs.
            if '=' in line:
                option, value = line.split('=', 1)

                option = option.strip()
                value = value.strip()

                options[option] = value

    return options

def cpu_count():
    """
    Returns the number of CPU cores (both virtual an pyhsical) in the system.
    """

    try:
        cpus = multiprocessing.cpu_count()
    except NotImplementedError:
        cpus = 1

    return cpus
