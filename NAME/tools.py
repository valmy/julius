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
import stat

import gettext
from gettext import gettext as _

import NAMEconfig
import commands
import configurationhandler
import version

__project_path = None

class project_path_not_found(Exception):
    pass

class data_path_not_found(Exception):
    def __init__(self, path):
        self.path = path
    def __str__(self):
        return repr(self.path)

def usage():
    print _("""Usage:
    NAME [OPTIONS] command ...

Options:
    --EXAMPLE, -e <data>       Example option
    --verbose                  Verbose mode
    -h, --help                 Show help information

Commands:
    xxxx <arg1> <arg2> to do ...

Examples:
    NAME xxxx foo bar""")


def get_NAME_data_path():
    """Retrieve NAME data path

    This path is by default <NAME_lib_path>/../data/ in trunk
    and /usr/share/NAME in an installed version but this path
    is specified at installation time.
    """

    # get pathname absolute or relative
    if NAMEconfig.__NAME_data_directory__.startswith('/'):
        pathname = NAMEconfig.__NAME_data_directory__
    else:
        pathname = os.path.dirname(__file__) + '/' + NAMEconfig.__NAME_data_directory__
    abs_data_path = os.path.abspath(pathname)

    if os.path.exists(abs_data_path):
        return abs_data_path
    else:
        raise data_path_not_found(abs_data_path)

def process_command_line(argv):
    """Entry point for command line processing
    use sys.argv by default if no args to parse

    :return: options
    """

    opt_command = []
    opt_example = None
    i = 0

    while i < len(argv):
        arg = argv[i]

        if arg.startswith('-'):
            if arg == '--example' or arg == '-e':
                if i + 1 < len(argv):
                    opt_example = argv[i + 1]
                    i += 1
                else:
                    print _("ERROR: %s needs one argument: %s" % ('--example', '<argument name>'))
                    sys.exit(1)
            elif arg == '--verbose':
                oldenv = ""
                if os.environ.has_key('NAME'):
                    oldenv = os.environ['NAME']
                os.environ['NAME'] = "verbose:" + oldenv
            elif arg == '--version':
                version.show_version()
                sys.exit(0)
            elif arg == '--help' or arg == '-h':
                usage()
                sys.exit(0)
            elif arg == '--':
                # turn off option detection, give everything to templates (even -f, --version)
                opt_command.extend(argv[i:])
                break
            else:
                opt_command.append(arg)
        else:
            opt_command.append(arg)
        i += 1

    if len(opt_command) == 0:
        print _("ERROR: No command provided in command line")
        usage()
        sys.exit(1)

    return (opt_command, opt_example)


def get_completion_in_context(argv, context_path=None):
    """seek for available completion (command, example…)

    : return tuples with list of available commands and origin (default or example)
    """

    if context_path is None:
        context_path = os.getcwd()
    else:
        context_path = os.path.abspath(context_path)

    available_completion = []

    # get available templates after option if needed
    if argv[-2] in ("-e", "--example"):
        available_completion.extend(['example_argument'])

    else:
        # treat commands and try to get the template from the project directory if we are in a project (if not already provided by the -t option)
        (opt_command, opt_example) = process_command_line(argv[3:])
        if not opt_example and configurationhandler.loadConfig(can_stop=False, config_file_path=context_path) == 0:
            try:
                opt_example = configurationhandler.project_config['example']
            except KeyError:
                pass
        # if no command yet, check for available command
        if len(opt_command) == 1:
            available_completion.extend([command.name for command in _get_commands_in_context(opt_example, context_path)])
        else:
            # ask for the command what she needs (it automatically handle the case of command followed by template and command followed by command)
            for command in commands.get_commands_by_criteria(name=opt_command[0]): # as 1: is '' or the begining of a word
                available_completion.extend(command.shell_completion(opt_example, opt_command[1:]))

    # dash option completion.  Some commands have dash args, but we also have them.  So we take what command thought
    # should be the completions and add our own.  We also strip anything that doesn't start with a dash, since many
    # completion functions are naive and just give all possible matches, even if they don't match.
    if argv[-1].startswith("-"):
        available_completion.extend(["-h", "--help", "-e", "--example", "--verbose", "--version"])
        available_completion = [arg for arg in available_completion if arg.startswith('-')]

    # remove duplicates and sort
    completion = list(set(available_completion))
    completion.sort()
    return (completion)


def _get_commands_in_context(opt_template, context_path=None):
    """seek for available commands in current context (internally called)"""

    command_completion = []
    # list available command in template suiting context (even command "followed by template" native of that template)
    if opt_template: 
        command_completion.extend([command for command in commands.get_commands_by_criteria(template=opt_template) if command.is_right_context(context_path, verbose=False)])

    # add commands followed by a template if we don't already have a template provided (native command followed by template has already been handled before)
    else:
        command_completion.extend([command for command in commands.get_commands_by_criteria(followed_by_template=True) if command.is_right_context(context_path, verbose=False)])

    # add builtin commands
    command_completion.extend([command for command in commands.get_commands_by_criteria(template="builtins") if command.is_right_context(context_path, verbose=False)])

    return command_completion

def get_commands_in_context(context_path=None):
    """seek for available commands in current context (extern call)"""
    opt_template = None
    if configurationhandler.loadConfig(can_stop=False, config_file_path=context_path) == 0:
        try:
            opt_template = configurationhandler.project_config['template']
        except KeyError:
            pass
    return(_get_commands_in_context(opt_template, context_path))

def check_for_followed_by_args(cmd, command_args):
    if not cmd.followed_by_command:
        return command_args # nothing to check

    command = None

    if cmd.followed_by_command:
        # If no arguments, there is something obviously wrong
        if len(command_args) == 0:
            usage_error(_("No command provided to %s command.") % cmd.name, cmd=cmd)

        command = commands.get_command(command_args[0]) # did user provid a valid builtin command?
        if command:
            command_args.insert(0, 'builtins')
        elif len(command_args) == 1:
            usage_error(_("%s is not a standard command.") % (command_args[0]), cmd=cmd)

        if len(command_args) > 1:
            if not command:
                usage_error(_("No %s command found.") % command_args[0], cmd=cmd)
        if not command:
            usage_error(_("No command provided to %s command.") % cmd.name, cmd=cmd)

    return command_args

def usage_error(msg=None, cmd=None, **kwargs):

    def print_command_candidates():
        cmds = []
        cmds.extend(commands.get_command_names_by_criteria())
        cmds.sort()
        print _("Candidate commands are: %s") % ", ".join(cmds)

    if msg:
        print _("ERROR: %s") % msg
    if cmd:
        cmd.usage()
    elif cmd:
        if cmd.followed_by_command:
            print_command_candidates()
    else:
        print_command_candidates()
    sys.exit(4)
