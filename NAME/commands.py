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
import subprocess
import sys

import builtincommands
import tools

import gettext
from gettext import gettext as _

gettext.textdomain('NAME')

# A dictionary with keys 'builtins'. Values
# are another dictionary mapping command names to their command objects. This
# is used as a cache of all commands.
__commands = {}

def get_all_commands():
    """Load all commands

    First load builtins commands. Push right parameters
    depending if hooks are available, or if the command execution is special
    You can note that create command is automatically overloaded atm.
    """

    global __commands
    if len(__commands) > 0:
        return __commands

    # add builtin commands (avoiding gettext and hooks)
    __commands = {}
    for elem in dir(builtincommands):
        command = getattr(builtincommands, elem)
        if (callable(command)
            and not command.__name__.startswith(('pre_', 'post_', 'help_', 'usage_', 'gettext'))):
            command_name = command.__name__
            # here, special case for some commands
            followed_by_command = False

            if command_name in builtincommands.followed_by_command:
                followed_by_command = True

            hooks = {'pre': None, 'post': None}
            for event in ('pre', 'post'):
                event_hook = getattr(builtincommands,
                                     event + '_' + command_name, None)
                if event_hook:
                    hooks[event] = event_hook

            __commands[command_name] = Command(
                command_name, command,
                followed_by_command, hooks['pre'], hooks['post'])

    return __commands


def get_commands_by_criteria(**criterias):
    """Get a list of all commands corresponding to criterias

    Criterias correponds to Command object properties.
    """

    # all criterias are None by default, which means, don't care about the
    # value.
    matched_commands = []
    all_commands = get_all_commands()

    for candidate_command_name in all_commands:
        candidate_command = all_commands[candidate_command_name]
        command_ok = True

        # check all criterias
        for elem in criterias:
            if (getattr(candidate_command, elem) != criterias[elem]):
                command_ok = False
                continue # no need to check other criterias
        if command_ok:
            matched_commands.append(candidate_command)

    return matched_commands


def get_command_names_by_criteria(**criteria):
    """Get a list of all command names corresponding to criteria.

    'criteria' correponds to Command object properties.
    """
    return [command.name for command in get_commands_by_criteria(**criteria)]


def get_command(command_name, **kwargs):
    try:
        command = get_commands_by_criteria(name=command_name, **kwargs)[0]
    except IndexError:
        return None
    return command

class Command:

    def _errmsg(self, function_name, return_code):
       '''Quit immediately and print error if return_code != 4'''
       if return_code != 4:
            print _("ERROR: %s command failed") % function_name
            print _("Aborting")

    def __init__(self, command_name, command,
                 followed_by_command=False,
                 prehook=None, posthook=None):
        self.command = command
        self.prehook = prehook
        self.posthook = posthook
        self.followed_by_command = followed_by_command
        self.name = command_name

    def shell_completion(self, args):
        """Smart completion of a command

        This command try to calls the
        corresponding command argument.
        """

        completion = []

        if (len(args) == 1 or len(args) == 2):
            if self.followed_by_command: # builtin command completion
                completion.extend(get_command_names_by_criteria())

        # give to the command the opportunity of giving some shell-completion
        # features
        if len(completion) == 0:
            if callable(self.command): # Internal function
                completion.extend(
                    self.command("", args, True))
            else: # External command
                instance = subprocess.Popen(
                    [self.command, "shell-completion"] + args,
                    stdout=subprocess.PIPE)
                command_return_completion, err = instance.communicate()
                if instance.returncode != 0:
                    print err
                    sys.exit(1)
                completion.extend(command_return_completion.strip().split(' ')) # pylint: disable=E1103

        return completion

    def usage(self):
        """Print usage of the current command"""

        return_code = False
        if callable(self.command): # intern function
            name = 'usage_'+self.name
            if hasattr(builtincommands, name):
                print getattr(builtincommands, name)
                return_code = True
        else: # launch command with "_usage" parameter
            process = subprocess.Popen([self.command, "_usage"], stdout=subprocess.PIPE)
            output = process.communicate()[0].strip()
            if output:
                print output
                return_code = True

        return return_code

    def help(self, dest_path, command_args):
        """Print help of the current command"""

        return_code = 0
        if callable(self.command): # intern function
            name = 'help_'+self.name
            if hasattr(builtincommands, name):
                print getattr(builtincommands, name)
            else:
                print self.command.__doc__ # untranslatable fallback
        else: # launch command with "help" parameter
            process = subprocess.Popen([self.command, "help"] + command_args,
                                       cwd=dest_path, stdout=subprocess.PIPE)
            output = process.communicate()[0].strip()
            if output:
                print output
            return_code = process.returncode

        return return_code

    def launch(self, current_dir, command_args):
        """Launch command and hooks for it

        This command will perform the right action (insider function or script
        execution) after having checked the context.
        """

        if self.prehook:
            return_code = self.prehook(current_dir, command_args)
            if return_code != 0:
                self._errmsg(self.prehook.__name__, return_code)
                return return_code

        if callable(self.command): # Internal function
            return_code = self.command(current_dir, command_args)
        else: # External command
            return_code = subprocess.call(
                [self.command] + command_args, cwd=current_dir)
        if return_code != 0:
            self._errmsg(self.name, return_code)
            return return_code

        if self.posthook:
            return_code = self.posthook(current_dir, command_args)
            if return_code != 0:
                self._errmsg(self.posthook.__name__, return_code)
                return return_code

        return 0
