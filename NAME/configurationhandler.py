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

import tools

project_config = {} # retrieved from project/.NAME

def loadConfig(can_stop=True, config_file_path=None):
    """ load configuration from path/.NAME or pwd/.NAME file"""

    # retrieve .NAME file
    global project_config
    project_config = {} # reset project_config
    try:
        if config_file_path is None:
            root_conf_dir = os.path.expanduser('~')
        else:
            root_conf_dir = os.path.abspath(config_file_path)
        NAME_file_path = root_conf_dir  + '/.NAME'
        config = project_config
    except tools.project_path_not_found:
        if can_stop:
            print _("ERROR: Can't load configuration in user home path or the specified path.")
            sys.exit(1)
        else:
            return(1)

    if os.path.isfile(NAME_file_path):
        try:
            fileconfig = file(NAME_file_path, 'rb')
            for line in fileconfig: 
                fields = line.split('#')[0] # Suppress commentary after the value in configuration file and in full line
                fields = fields.split('=', 1) # Separate variable from value
                # normally, we have two fields in "fields"
                if len(fields) == 2:
                    config[fields[0].strip()] = fields[1].strip() 
            fileconfig.close()
        except (OSError, IOError), e:
            print _("ERROR: Can't load configuration in %s: %s" % (NAME_file_path, e))
            sys.exit(1)
    return(0)


def saveConfig(config_file_path=None):
    """ save the configuration file from config dictionary in project or global NAME file

    path is optional (needed by the create command, for instance).
    getcwd() is taken by default.    
    
    keep commentaries and layout from original file """

    # retrieve .NAME file
    try:
        if config_file_path is None:
            root_conf_dir = os.path.expanduser('~')
        else:
            root_conf_dir = os.path.abspath(config_file_path)
        NAME_file_path = root_conf_dir + '/.NAME'
    # if no .NAME, create it using config_file_path or cwd
    except tools.project_path_not_found:
        if config_file_path:
            NAME_file_path = os.path.abspath(config_file_path) + '/.NAME'
        else:
            NAME_file_path = os.getcwd() + "/.NAME"
    config = project_config
    
    try:
        filedest = file(NAME_file_path + '.new', 'w')
        try:
            fileconfig = file(NAME_file_path, 'rb')
            remaingconfigtosave = config.copy()
            for line in fileconfig:
                fields = line.split('#')[0] # Suppress commentary after the value in configuration file and in full line
                fieldsafter = line.split('#')[1:]
                fields = fields.split('=', 1) # Separate variable from value
                # normally, we have two fields in "fields" and it should be used by config tabular
                if len(fields) == 2:
                    if fields[0].strip() in remaingconfigtosave:
                        line = fields[0].strip() + " = " + str(remaingconfigtosave.pop(fields[0].strip()))
                        if len(fieldsafter) > 0:
                            line = line + " #" + "#".join(fieldsafter) # fieldsafter already contains \n
                        else:
                            line = line + "\n"
                    else: # old config value, no more on the dictionary. So, remove it:
                        line = ""
                filedest.write(line) # commentaries or empty lines, anything other things which is not useful will be printed unchanged
            # write remaining data if some (new data not in the old config file).
            filedest.write("".join(elem + " = " + str(remaingconfigtosave[elem]) + '\n' for elem in remaingconfigtosave)) #\n here for last element (and not be added, when no iteration to do)
#            print "\n".join(elem + " = " + remaingconfigtosave[elem] for elem in remaingconfigtosave)
            fileconfig.close()
        except (OSError, IOError), e:      
            # write config file from scratch (no previous file found)
            filedest.write("\n".join(elem + " = " + str(config[elem]) for elem in config) + "\n")
        finally:
            filedest.close()
            os.rename(filedest.name, NAME_file_path)
    except IOError, e:
        sys.stderr.write(_("ERROR: Can't save configuration in %s\n" % NAME_file_path))
        return(1)
    return 0
