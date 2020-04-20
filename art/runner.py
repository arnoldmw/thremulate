"""
ART Attack Runner
Version: 1.0
Author: Olivier Lemelin

Modified by: Arnold Mwesigwa, amwesigwa16@gmail.com
Changes made:
1. Returns commands to execute when the AtomicRunner class is instantiated.
2. Removed the code for running interactively.
3. Removed print statements since we are using only the AtomicRunner class.

Script that was built in order to automate the execution of ART.
"""

#      Thremulate executes Network Adversary Post Compromise Activities.
#      Copyright (C) 2020  Mwesigwa Arnold
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import os.path
import fnmatch
import platform
import re
import subprocess
import sys
import hashlib
import json

import yaml
import unidecode

TECHNIQUE_DIRECTORY_PATTERN = 'T*'
ATOMICS_DIR_RELATIVE_PATH = os.path.join(".", "atomics")
HASH_DB_RELATIVE_PATH = "techniques_hash.db"
COMMAND_TIMEOUT = 20

# launcher = ''
# command = ''
# built_command = ''

agent_launcher = ''
agent_command = ''
agent_commands = []


##########################################
# Filesystem & Helpers
##########################################


def get_platform():
    """Gets the current platform."""

    # We need to handle the platform a bit differently in certain cases.
    # Otherwise, we simply return the value that's given here.
    plat = platform.system().lower()

    if plat == "darwin":
        # 'macos' is the term that is being used within the .yaml files.
        plat = "macos"

    return plat


def get_self_path():
    """Gets the full path to this script's directory."""
    return os.path.dirname(os.path.abspath(__file__))


def get_yaml_file_from_dir(path_to_dir):
    """Returns path of the first file that matches "*.yaml" in a directory."""

    for entry in os.listdir(path_to_dir):
        if fnmatch.fnmatch(entry, '*.yaml'):
            # Found the file!
            return os.path.join(path_to_dir, entry)

    print("No YAML file describing the technique in {}!".format(path_to_dir))
    return None


def load_technique(path_to_dir):
    """Loads the YAML content of a technique from its directory. (T*)"""

    # Get path to YAML file.
    file_entry = get_yaml_file_from_dir(path_to_dir)

    # Load and parses its content.
    with open(file_entry, 'r', encoding="utf-8") as f:
        return yaml.load(unidecode.unidecode(f.read()))


def load_techniques():
    """Loads multiple techniques from the 'atomics' directory."""

    # Get path to atomics directory.
    atomics_path = os.path.join(get_self_path(),
                                ATOMICS_DIR_RELATIVE_PATH)
    normalized_atomics_path = os.path.normpath(atomics_path)

    # Create a dict to accept the techniques that will be loaded.
    techniques = {}

    # For each tech directory in the main directory.
    for atomic_entry in os.listdir(normalized_atomics_path):

        # Make sure that it matches the current pattern.

        if fnmatch.fnmatch(atomic_entry, TECHNIQUE_DIRECTORY_PATTERN):
            # ## PRINTS TECHNIQUES LOADED
            # print("Loading Technique {}...".format(atomic_entry))

            # Get path to tech dir.
            path_to_dir = os.path.join(normalized_atomics_path, atomic_entry)

            # Load, parse and add to dict.
            tech = load_technique(path_to_dir)
            techniques[atomic_entry] = tech

            # Add path to technique's directory.
            techniques[atomic_entry]["path"] = path_to_dir

    return techniques


##########################################
# Executors
##########################################

def is_valid_executor(exe, self_platform):
    """Validates that the executor can be run on the current platform."""
    if self_platform not in exe["supported_platforms"]:
        return False

    # The "manual" executors need to be run by hand, normally.
    # This script should not be running them.
    if exe["executor"]["name"] == "manual":
        return False

    return True


def get_valid_executors(tech):
    """From a loaded technique, get all executors appropriate for the current platform."""
    return list(filter(lambda x: is_valid_executor(x, get_platform()), tech['atomic_tests']))


def get_executors(tech):
    """From a loaded technique, get all executors."""
    return tech['atomic_tests']


def get_default_parameters(args):
    """Build a default parameters dictionary from the content of the YAML file."""
    return {name: values["default"] for name, values in args.items()}


def set_parameters(executor_input_arguments, given_arguments):
    """Sets the default parameters if no value was given."""

    # Default parameters as decribed in the executor.
    default_parameters = get_default_parameters(executor_input_arguments)

    # Merging default parameters with the given parameters, giving precedence
    # to the given params.
    final_parameters = {**default_parameters, **given_arguments}

    # Convert to right type
    for name, value in final_parameters.items():
        final_parameters[name] = convert_to_right_type(value, executor_input_arguments[name]["type"])

    return final_parameters


def apply_executor(executor, path, parameters):
    """Non-interactively run a given executor."""

    args = executor["input_arguments"] if "input_arguments" in executor else {}
    final_parameters = set_parameters(args, parameters)

    launcher = convert_launcher(executor["executor"]["name"])
    command = executor["executor"]["command"]
    built_command = build_command(launcher, command, final_parameters)

    global agent_launcher
    global agent_command
    global agent_commands

    agent_launcher = launcher
    agent_command = built_command
    agent_commands.append(agent_command)

    # begin execution with the above parameters.
    # ##############################################################################################################
    # execute_command(launcher, built_command, path)


#
# def get_command(agent_launcher, agent_command):
#     return [agent_launcher, agent_command]


##########################################
# Commands
##########################################

class ManualExecutorException(Exception):
    """Custom Exception that we trigger triggered when we encounter manual executors."""
    pass


def convert_launcher(launcher):
    """Takes the YAML launcher, and outputs an appropriate executable
    to run the command."""

    plat = get_platform()

    # Regular command prompt.
    if launcher == "command_prompt":  # pylint: disable=no-else-return
        if plat == "windows":  # pylint: disable=no-else-return
            # This is actually a 64bit CMD.EXE.  Do not change this to a 32bits CMD.EXE
            return "C:\\Windows\\System32\\cmd.exe /C"

        elif plat == "linux":
            # Good ol' Bourne Shell.
            return "/bin/sh"

        elif plat == "macos":
            # I assume /bin/sh is available on OSX.
            return "/bin/sh"

        else:
            # We hit a non-Linux, non-Windows OS.  Use sh.
            print("Warning: Unsupported platform {}! Using /bin/sh.".format(plat))
            return "/bin/sh"

    elif launcher == "powershell":
        return "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"

    elif launcher == "sh":
        return "/bin/sh"

    elif launcher == "manual":
        # We cannot process manual execution with this script.  Raise an exception.
        raise ManualExecutorException()

    else:
        # This launcher is not known.  Returning it directly.
        # print("Warning: Launcher '{}' has no specific case! Returning as is.")
        return launcher


def build_command(launcher, command, parameters):
    """Builds the command line that will eventually be run."""

    # Using a closure! We use the replace to match found objects
    # and replace them with the corresponding passed parameter.
    def replacer(matchobj):
        if matchobj.group(1) in parameters:
            val = parameters[matchobj.group(1)]
        else:
            print("Warning: no match found while building the replacement string.")
            val = None

        return val

    # Fix string interpolation (from ruby to Python!) -- ${}
    command = re.sub(r"\$\{(.+?)\}", replacer, command)

    # Fix string interpolation (from ruby to Python!) -- #{}
    command = re.sub(r"\#\{(.+?)\}", replacer, command)

    return command


def convert_to_right_type(value, t):
    """We need to convert the entered argument to the right type, based on the YAML
    file's indications."""

    # Make sure that type is easy to parse.
    t = t.lower()

    if t == "string":
        # Can't really validate this otherwise.
        pass

    elif t == "path":
        # Validating this type doesn't seem to make sense most of the time...
        pass
        # value = os.path.normcase(os.path.normpath(value))
        # # Make sure that the path exists, or that the base directory does (creating a new file, for example)
        # if not os.path.exists(value) and not os.path.exists(os.path.dirname(value)):
        #    raise Exception("Path {} does not exist!".format(value))

    elif t == "url":
        # We'll assume the URL is well-formatted.  That's the user's problem. :)
        pass

    # else:
    #     raise Exception("Value type {} does not exist!".format(t))

    return value


def execute_command(launcher, command, cwd):
    """Executes a command with the given launcher."""

    # We execute one line at a time.
    for comm in command.split("\n"):

        # We skip empty lines.  This is due to the split just above.
        if comm == "":
            continue

        # # We actually run the command itself.
        p = subprocess.Popen(launcher, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, env=os.environ, cwd=cwd)

        # Attempt to fetch the results of the command.  The command, by default, has a few seconds to do its
        # work.  We kill it if it takes too long.
        try:
            outs, errs = p.communicate(bytes(comm, "utf-8") + b"\n", timeout=COMMAND_TIMEOUT)

            def clean_output(s):
                # Remove Windows CLI garbage
                s = re.sub(r"Microsoft\ Windows\ \[version .+\]\r?\nCopyright.*(\r?\n)+[A-Z]\:.+?\>", "", s)
                return re.sub(r"(\r?\n)*[A-Z]\:.+?\>", "", s)

            # Output the appropriate outputs if they exist.
            if outs:
                print("Output: {}".format(clean_output(outs.decode("utf-8", "ignore"))), flush=True)
            else:
                print("(No output)")
            if errs:
                print("Errors: {}".format(clean_output(errs.decode("utf-8", "ignore"))), flush=True)

        # We kill the process if it takes too long to operate.
        except subprocess.TimeoutExpired as e:

            # Display output if it exists.
            if e.output:
                print(e.output)
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            print("Command timed out!")

            # Kill the command.
            p.kill()

            # Next command.
            continue


#########################################
# Hash database
#########################################

def load_hash_db():
    """Loads the hash database from a file, or create the empty file if it did not already exist."""
    hash_db_path = os.path.join(get_self_path(), HASH_DB_RELATIVE_PATH)
    try:
        with open(hash_db_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Could not decode the JSON Hash DB!  Please fix the syntax of the file.")
        sys.exit(3)
    except IOError:
        print("File did not exist.  Created a new empty Hash DB.")
        empty_db = {}
        write_hash_db(hash_db_path, empty_db)
        return empty_db


def write_hash_db(hash_db_path, db):
    """Writes the hash DB dictionary to a file."""
    with open(hash_db_path, 'w') as f:
        json.dump(db, f, sort_keys=True, indent=4, separators=(',', ': '))


def check_hash_db(hash_db_path, executor_data, technique_name, executor_position):
    """Checks the hash DB for a hash, and verifies that it corresponds to the current executor data's
    hash.  Adds the hash to the current database if it does not already exist."""
    hash_db = load_hash_db()
    executor_position = str(executor_position)

    # Tries to load the technique section.
    if technique_name not in hash_db:
        # print("Technique section '{}' did not exist.  Creating.".format(technique_name))
        # Create section
        hash_db[technique_name] = {}

    new_hash = hashlib.sha256(json.dumps(executor_data).encode()).hexdigest()

    # Tries to load the executor hash.
    if executor_position not in hash_db[technique_name]:
        # print("Hash was not in DB.  Adding.")
        # Create the hash, since it does not exist.  Return OK.
        hash_db[technique_name][executor_position] = new_hash

        # Write DB to file.
        write_hash_db(hash_db_path, hash_db)
        return True

    old_hash = hash_db[technique_name][executor_position]

    # If a previous hash already exists, compare both hashes.
    return old_hash == new_hash


def clear_hash(hash_db_path, technique_to_clear, position_to_clear=-1):
    """Clears a hash from the DB, then saves the DB to a file."""
    hash_db = load_hash_db()

    if position_to_clear == -1:
        # We clear out the whole technique.
        del hash_db[technique_to_clear]
    else:
        # We clear the position.
        del hash_db[technique_to_clear][str(position_to_clear)]

    # print("Hash cleared.")

    write_hash_db(hash_db_path, hash_db)


#########################################
# Atomic Runner and Main
#########################################


class AtomicRunner:
    """Class that allows the execution, interactive or not, of the various techniques that are part of ART."""

    def __init__(self):
        """Constructor.  Ensures that the techniques are loaded before we can run them."""
        # Loads techniques.
        self.techniques = load_techniques()
        self.command = agent_command
        self.launcher = agent_launcher
        self.platform = ''

    def execute(self, technique_name, position=0, parameters=None):
        """Runs a technique non-interactively."""

        parameters = parameters or {}

        # print("================================================")
        # print("Executing {}/{}\n".format(technique_name, position))

        # Gets the tech.
        tech = self.techniques[technique_name]

        # Gets Executors.
        executors = get_executors(tech)

        try:
            # Get executor at given position.
            executor = executors[position]
        except IndexError:
            print("Out of bounds: this executor is not part of that technique's list!")
            return False

        # Make sure that it is compatible.
        if not is_valid_executor(executor, self.platform):
            # if not is_valid_executor(executor, get_platform()):
            print("Warning: This executor is not compatible with the current platform!")
            return False

        # Check that hash matches previous executor hash or that this is a new hash.
        if not check_hash_db(HASH_DB_RELATIVE_PATH, executor, technique_name, position):
            print("Warning: new executor fingerprint does not match the old one! Skipping this execution.")
            print("To re-enable this test, review this specific executor, test your payload, and clear out this"
                  " executor's hash from the database.")
            print("Run this: python runner.py clearhash {} {}.".format(technique_name, position))
            return False

        # Launch execution.
        try:
            apply_executor(executor, tech["path"], parameters)
        except ManualExecutorException:
            # print("Cannot launch a technique with a manual executor. Aborting.")
            return False

        self.launcher = agent_launcher
        self.command = agent_command
        return True


def clear(args):
    """Clears a stale hash from the Hash DB."""
    clear_hash(HASH_DB_RELATIVE_PATH, args.technique, args.position)
