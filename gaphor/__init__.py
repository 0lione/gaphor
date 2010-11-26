#!/usr/bin/env python

"""This is Gaphor, a Python+GTK based UML modelling tool.

This module allows Gaphor to be launched from the command line.
The main() function sets up the command-line options and arguments and
passes them to the main Application instance."""

__all__ = [ 'main', 'GaphorError' ]

from optparse import OptionParser
import pygtk

from gaphor.application import Application

pygtk.require('2.0')

class GaphorError(Exception):
    """Generic Gaphor exception."""
    
    def __init__(self, args=None):
        """Constructor.  Initialize base exception and store passed
        arguments."""

        super(GaphorError, self).__init__()
        self.args = args

def launch():
    """Start the main application by initiating and running Application.
    
    The file_manager service is used here to load a Gaphor model if one was
    specified on the command line.  Otherwise, a new model is created and
    the Gaphor GUI is started."""

    file_manager = Application.get_service('file_manager')

    if len(Application.args) == 1:
        file_manager.load(Application.args[0])
    else:
        file_manager.action_new()

    Application.run()
    
def main():
    """Start Gaphor from the command line.  This function creates an option
    parser for retrieving arguments and options from the command line.  This
    includes a Gaphor model to load.
    
    The application is then initialized, passing along the option parser.  This
    provides and plugins and services with access to the command line options
    and may add their own."""

    parser = OptionParser()

    parser.add_option('-p',\
                      '--profile',\
                      action='store_true',\
                      help='Run in profile')

    parser.add_option('-l',\
                      '--logging',\
                      default='DEBUG',\
                      help='Logging level')
                      
    Application.init(opt_parser=parser)
   
    if Application.options.profile:

        import cProfile
        import pstats

        cProfile.run('import gaphor; gaphor.launch()',\
                     'gaphor.prof')
        
        profile_stats = pstats.Stats('gaphor.prof')
        profile_stats.strip_dirs().sort_stats('time').print_stats(50)

    else:
	
        launch()

# TODO: Remove this.  
import __builtin__

__builtin__.__dict__['log'] = misc.logger.Logger()

