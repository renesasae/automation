'''
Created on May 2, 2020

@author: Onkar.Raut
'''
import os
import re
import logging
import subprocess


class JLink(object):
    '''
    classdocs
    '''
    def getEmuList(self):
        ''' Returns a list of emulators found'''
        jlinkexe = [self.commander, r"-AutoConnect", r"0", r"-ExitOnError", r"1", r"-USB", r"0"]
        commands = ["ShowEmuList",
                    "exit"]
        cmdIter = iter(commands)
        
        process = subprocess.Popen(jlinkexe, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        process.wait(timeout=5)
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
                
        if process.returncode == 0:
            debugger_count = 0;
            
        return
    
    def Program(self,CommandFile=None,SerialNumber=None):
        if CommandFile == None :
            logging.critical("Missing needed CommandFile")
            raise ValueError("Missing needed CommandFile")
        if SerialNumber == None:
            logging.critical("Missing needed SerialNumber")
            raise ValueError("Missing needed SerialNumber")
        
        if os.path.exists(CommandFile) == False:
            logging.error("CommandFile does not exist on file system check path: %s", CommandFile)
            raise FileNotFoundError("CommandFile does not exist on file system check path: %s", CommandFile)
        
        CommandFile = os.path.normpath(CommandFile)
        __fpath__, __fcmd__ = os.path.split(CommandFile)
        
        jlinkexe = [self.commander, r"-CommandFile", CommandFile, r"-SelectEmuBySN", SerialNumber]
        
#         proc = subprocess.run(jlinkexe,cwd=__fpath__,shell=True)
        proc = subprocess.run(jlinkexe,cwd=__fpath__,timeout=30,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
        
        if proc.returncode == 0:
#         if proc.returncode == 0 and r"Script processing completed." in proc.stdout:
            return True
        
        return False
    
    def Ready(self):
        return False if self.commander == None else True

    def __init__(self, jlinkpath):
        '''
        Constructor
        '''
        """
        Check if any JLink Debuggers are attached via USB.
        """
        
        
        """
        Check if J-Link Software and Documentation Package is installed.
        """
        if os.path.exists(jlinkpath) == False or jlinkpath == None:
            logging.critical("J-Link Executable file path incorrect or not provided")
            raise FileNotFoundError
        
        if os.path.isfile(jlinkpath) == False or os.access(jlinkpath, os.X_OK) == False:
            logging.critical("JLink path provided is not an executable")
            raise FileNotFoundError
        
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
        
        process = subprocess.Popen([jlinkpath, r"-AutoConnect", r"0", r"-ExitOnError", r"1", "-USB"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        
        if process != None: 
            process.wait(timeout=10)
            process_output = process.stdout.readline()
            for jlink_search_pattern in jlink_search_patterns:
                search_pattern = re.compile(jlink_search_pattern)
    #             process_output = process_output.decode("utf-8")
                match = re.search(search_pattern, process_output)
                if match:
                    __rev_major__ = match.group(2)
                    __rev_minor__ = match.group(3)
                    self.rev_major = int(__rev_major__)
                    self.rev_minor = int(__rev_minor__)
                    self.commander = os.path.normpath(jlinkpath)
                    break
            process.terminate()
        
            jlinkfiles = [f for f in os.listdir(self.__fpath__) if os.path.isfile(os.path.join(self.__fpath__, f))]
            
            ''' Fill out the files needed'''
            for f in jlinkfiles:
                if "jlinkarm" in f.lower():
                    self.jlinkarmdll= f
                if "jlinkrttviewer" in f.lower():
                    self.rttviewer = f
            
        if self.commander == None:
            raise FileNotFoundError
        
        return
        