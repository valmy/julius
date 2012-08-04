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

import configurationhandler
import commands as commands_module
import NAMEconfig
import tools

import gettext
from gettext import gettext as _

help_commands = _("List all commands")
def commands(project_dir, command_args, shell_completion=False):
    """List all commands"""

    # We have nothing for this
    if shell_completion:
        return("")

    all_commands = commands_module.get_all_commands()
    for command in all_commands:
        print "%s" % command
            
    return(0)

help_getstarted = _("Give some getstarted advice")
def getstarted(current_dir, command_args, shell_completion=False):
    """Give some getstarted advice"""

    # We have nothing for this
    if shell_completion:
        return("")

    print _('''-------------------------------
    Welcome to NAME!
-------------------------------

You can ... by executing 'NAME xxx <yyy> <zzz>'.

Example with ...:
1. create an ...:
$ NAME xxxx foo bar
$ cd foo
$ NAME tutorial

2. You can also try:
$ xxxx edit
$ xxxx design
$ xxxx run
Use bash completion to get every available command

3. How to play with a package and release it:

Optional (but recommended): build your package locally:
$ NAME package

BE WARNED: the two following commands will connect to Launchpad. Make sure that you have a Launchpad account and a PPA! You can find out more about setting up a Launchpad account and Launchpad features at https://launchpad.net/
$ NAME release or $ NAME share

Have Fun!''')
    return 0

help_help = _("Get help from commands")
usage_help = _("Usage: NAME help <command>")
def help(current_dir, command_args, shell_completion=False):
    """Get help from commands"""

    # We have nothing for this
    if shell_completion:
        return("")

    # main NAME script has already made sure input is sane

    command_name = command_args[1]
    command = commands_module.get_command(command_name)

    # Also print usage if we can
    if command.usage():
        print # blank line before getting to help
    return command.help(current_dir, command_args)

# here, special builtin commands properties
followed_by_command = ['help']
