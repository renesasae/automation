#!/usr/local/bin/python2.7
# encoding: utf-8
'''
automation.rig.debuggers -- shortdesc

automation.rig.debuggers is a Utility to enumerate all boards connected to a computer and output related information to a CSV

It defines classes_and_methods

@author:     Onkar Raut

@copyright:  2020 electrotantra.tech. All rights reserved.

@license:    license

@contact:    rautonkar@gmail.com
@deffield    updated: Updated
'''

import sys
import os
from automation.rig import files
from automation.rig.jlink import JLink

import logging
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2020-05-02'
__updated__ = '2020-05-02'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
        logging.error(msg)
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Onkar Raut on %s.
  Copyright 2020 electrotantra. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument("-i", "--include", dest="include", help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="RE" )
        parser.add_argument("-j", "--jlink", dest="jlink", help="Path to location where JLink Commander (Jlink.exe) is installed. [default: %(default)s]", metavar="PATH" )
        parser.add_argument("-e", "--exclude", dest="exclude", help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="RE" )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')
        parser.add_argument('-l', '--log', dest='logfile', help='Specify where logger information should be output.')
        
        # Process arguments
        args = parser.parse_args()

        paths = args.paths
        verbose = args.verbose
        recurse = args.recurse
        inpat = args.include
        expat = args.exclude
        loglevel = logging.NOTSET
        jlink = os.path.normpath(os.path.normcase(args.jlink))
        

        if verbose > 0:
            if verbose == 1:
                loglevel = logging.CRITICAL
            elif verbose == 2:
                loglevel = logging.ERROR
            elif verbose == 3:
                loglevel = logging.WARNING
            elif verbose == 4:
                loglevel = logging.INFO
            elif verbose == 5:
                loglevel = logging.DEBUG
            else:
                loglevel = logging.NOTSET
        
        if args.logfile is not None:
            logging.basicConfig(filename=args.logfile, level=loglevel, format='%(asctime)s - %(levelname)s - %(message)s')
        else:
            logging.basicConfig(level=loglevel, format='%(module)s: %(asctime)s - %(levelname)s - %(message)s')
                
        if os.path.exists(jlink) == False or jlink == None:
            raise CLIError("J-Link Executable file path incorrect or not provided")
        
        if os.path.isfile(jlink) == False or os.access(jlink, os.X_OK) == False:
            raise CLIError("JLink path provided is not an executable")
        
        jlink = JLink(jlink)
        
        scriptFiles = files.Find()
        scriptFiles.readcsv(r"C:\Users\onkar.raut\Documents\2020H1\LiClipse\testing\automation\board_programs.csv")
        scriptFiles.readcsv(r"C:\Users\onkar.raut\Documents\2020H1\LiClipse\testing\automation\serial_number_definitions.csv")
        scriptFiles.prepare()
        
        jlink.Program(r"C:\Users\onkar.raut\Documents\2020H1\reviews\ep_ra2a1\freertos_ek_ra2a1_ep\freertos_ek_ra2a1_ep Program.jlink","831004110")
        jlink.Program(r"C:\Users\onkar.raut\Documents\2020H1\reviews\ep_ra2a1\quickstart_ek_ra2a1_ep\quickstart_ek_ra2a1_ep Program.jlink","831004110")
        
       
            
        if inpat and expat and inpat == expat:
            raise CLIError("include and exclude pattern are equal! Nothing will be processed.")

        for inpath in paths:
            ### do something with inpath ###
            print(inpath)
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0

    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
#         sys.argv.append("-h")
        sys.argv.append("-vvvv")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'automation.rig.debuggers_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())