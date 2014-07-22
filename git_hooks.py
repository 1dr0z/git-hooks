from __future__ import print_function
from cStringIO import StringIO
from datetime import datetime
import os, sys

#---------------------------------
# Public Helpers
#---------------------------------

def run_hooks(hooks):
    for hook in hooks:
        status, message = hook()
        if not status:
            print('Error:', message)

            if hook.get_stderr():
                print(hook.get_stderr())

            if hook.get_stdout():
                print(hook.get_stdout())

            sys.exit(1)
        elif message:
            print(hook.get_stdout())

class CapturedOutput:

    """Capture stdout and stderr for a command block"""

    def __init__(self):
        self._output = (StringIO(), StringIO())
        self._sysout = sys.stdout
        self._syserr = sys.stderr

    def __enter__(self):
        sys.stdout, sys.stderr = self._output
        return self._output

    def __exit__(self, type, value, trace):
        sys.stdout = self._sysout
        sys.stderr = self._syserr

class DirectoryImporter:

    """Import files from a specified directory even if it is not in the system path.

    Temporarily modifies the system path to add the directory at the beginning
    Provides an importer function that will import files relative to the directory"""

    directory = None

    def __init__(self, directory):
        if not os.path.isdir(directory):
            raise IOError('directory {0} not found'.format(directory))
        self.directory = directory

    def _importer(self, relpath):
        """Import a module relative to the directory path"""
        module = os.path.splitext(relpath)[0]
        module = module.replace(os.pathsep, '.')
        return __import__(module)

    def __enter__(self):
        if self.directory:
            sys.path.insert(0, self.directory)
        return self._importer

    def __exit__(self, type, value, trace):
        if self.directory:
            del sys.path[0]

def git_hook(function):
    """Decorator function used to create a git hook"""
    return Hook(function)

def is_hook(object):
    """Determine wether an object is a git hook"""
    return isinstance(object, Hook)

__all__ = ['run_hooks', 'CapturedOutput', 'DirectoryImporter', 'git_hook', 'is_hook']

#---------------------------------
# Internal Machinery
#---------------------------------

class Status:

    """A really simple status object"""

    def __init__(self):
        self.status  = True
        self.message = None

    def passes(self, message=None):
        """Set a passing status with optional message"""

        self.status  = True
        self.message = message

    def fails(self, message):
        """Set a failing status, message is required"""
        self.status  = False
        self.message = message

    def log(self, message):
        """Output a formated log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        print('{0}: {1}'.format(timestamp, message))

class Hook:

    """Simple object that serves as a wrapper for given function

    The following things are True:
        function stdout and stderr will be captured instead of output
        function will be called with a status object to either pass or fail
        when the function throws an exception it will be set to a failed status"""

    def __init__(self, function):
        self._status = Status()
        self._hook   = function
        self._stdout = None
        self._stderr = None

    def __call__(self):
        with CapturedOutput() as output:
            try:
                self._hook(self._status)
            except BaseException as detail:
                self._status.fails('{}'.format(detail))

            # store the captured output for this hook
            self._stdout = output[0].getvalue().strip() or None
            self._stderr = output[1].getvalue().strip() or None

        return self._status.status, self._status.message

    def get_stdout(self):
        return self._stdout

    def get_stderr(self):
        return self._stderr