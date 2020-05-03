'''
Created on May 2, 2020

@author: Onkar.Raut
'''
import os
import re
import subprocess
import logging
from plistlib import InvalidFileException

class JLink(object):
    '''
    classdocs
    '''
    def getEmuList(self):
        ''' Returns a list of emulators found'''
        jlinkexe = [self.commander,"-ExitOnError 1", "-AutoConnect 0"]
        commands = ["ShowEmuList",
                    "exit"]
        cmdIter = iter(commands)
        
        process = subprocess.Popen(jlinkexe, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        process_output = []
        while process.poll() == None:
            outline = process.stdout.readline()
            process_output.append(outline.decode("utf-8"))
            logging.debug(outline.decode("utf-8"))
            if b"J-Link>" == outline:
                try:
                    process.stdin.write(next(cmdIter))
                except StopIteration:
                    if(commands[-1] != "exit"):
                        process.stdin.write("exit")
                        process.terminate()
                    break;
            
        return

    def __init__(self, jlinkpath):
        '''
        Constructor
        '''
        if os.path.exists(jlinkpath) == False or jlinkpath == None:
            logging.critical("J-Link Executable file path incorrect or not provided")
        
        if os.path.isfile(jlinkpath) == False or os.access(jlinkpath, os.X_OK) == False:
            logging.critical("JLink path provided is not an executable")
        
        self.__fpath__, self.__fjlink__ = os.path.split(jlinkpath)
        
        if "jlink" not in self.__fjlink__.lower():
            logging.critical("File provided may not be JLink.")
            raise FileNotFoundError
        
        self.rev_major = None
        self.rev_minor = None
        self.emulators = set()
        self.commander = None
        
        jlink_search_patterns = []
        jlink_search_patterns.append(r"(SEGGER J-Link Commander V(\d{1,2})\.(\d{1,2}).*)")
        
        process = subprocess.Popen([jlinkpath, "-AutoConnect 0", "-ExitOnError 1"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        init_input_to_jlink = b"exit"
        
        process_output = process.stdout.readline()
        for jlink_search_pattern in jlink_search_patterns:
            search_pattern = re.compile(jlink_search_pattern)
            process_output = process_output.decode("utf-8")
            match = re.search(search_pattern, process_output)
            if match:
                __rev_major__ = match.group(2)
                __rev_minor__ = match.group(3)
                self.rev_major = int(__rev_major__)
                self.rev_minor = int(__rev_minor__)
                self.commander = jlinkpath
                break

        
        while process.poll() == None:
            process_output = process.stdout.readline()
            logging.debug(process_output.decode("utf-8"))
            if b"J-Link>" == process_output:
                process.stdin.write(init_input_to_jlink)
            
            
        jlink_search_patterns = []
        jlink_search_patterns.append(r"(SEGGER J-Link Commander V(\d{1,2})\.(\d{1,2}).*)")
        
        jlinkfiles = [f for f in os.listdir(self.__fpath__) if os.path.isfile(os.path.join(self.__fpath__, f))]
        
        ''' Fill out the files needed'''
        for f in jlinkfiles:
            if "jlinkarm" in f.lower():
                self.jlinkarmdll= f
            if "jlinkrttviewer" in f.lower():
                self.rttviewer = f
            
            
        __fjlinkrttviewer__ = None
        
        if self.commander == None:
            raise FileNotFoundError
        
        return
        