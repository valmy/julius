#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright 2012 T. Budiman
#
# This file is part of NAME
#
#This program is free software: you can redistribute it and/or modify it 
#under the terms of the GNU General Public License version 3, as published 
#by the Free Software Foundation.

#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the GNU General Public License for more details.

#You should have received a copy of the GNU General Public License along 
#with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import gettext
from gettext import gettext as _

import NAMEconfig, tools

gettext.textdomain('NAME')

def show_version():
    """ print version information """

    try:
        NAME_data_path = tools.get_NAME_data_path()
    except tools.data_path_not_found, invalid_data_path:
        NAME_data_path = (_("No NAME data path found in %s.") % invalid_data_path)

    print _("""NAME %s
  Python interpreter: %s %s
  Python standard library: %s
  
  NAME used library: %s
  NAME data path: %s

Copyright 2012 T. Budiman

NAME comes with ABSOLUTELY NO WARRANTY. NAME is free software, and
you may use, modify and redistribute it under the terms of the GNU
General Public License version 3 or later.""") % (
    NAMEconfig.__version__, sys.executable, ".".join([str(x) for x in sys.version_info[0:3]]),
    os.path.dirname(os.__file__), os.path.dirname(__file__), NAME_data_path)
