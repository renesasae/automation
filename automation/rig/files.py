'''
Created on May 10, 2020

@author: Onkar.Raut
'''
import os
import csv
import glob
import logging

class Find(object):
    def hex(self, root):
        '''
        Find JLink Script files
        '''    
        fpath = os.path.join(root,"**","*.hex")
        files = glob.glob(fpath,recursive=True)
        logging.info("Files found.")
        for file in files:
            logging.info(file)
        self.files = files
    
    def scripts(self, root):
        '''
        Find JLink Script files
        '''    
        fpath = os.path.join(root,"**","program.jlink")
        files = glob.glob(fpath,recursive=True)
        if len(files) > 0:
            logging.info("Files found.")
        else:
            logging.info("No files found.")
        for file in files:
            logging.info(file)
        self.files = files
        
    def readcsv(self,csvFile):
        ''''
        Read J-Link Script files
        '''
        
        with open(csvFile) as fcsv:
            rcsv = csv.DictReader(fcsv, delimiter=',')
            if rcsv.fieldnames[0] == 'board_name' and rcsv.fieldnames[1] == 'script_path':
                self.boards_scripts = []
                self.root, _ = os.path.split(csvFile)
                logging.info("%s is a file containing board names and Jlink script names" % csvFile)
                for row in rcsv:
                    logging.info("%s,%s" % (row['board_name'],row['script_path']))
                    self.boards_scripts.append(row)
            elif rcsv.fieldnames[0] == 'board_name' and rcsv.fieldnames[1] == 'serial_number':
                self.boards_serials = []
                logging.info("%s is a file containing board names and scripts" % csvFile)
                for row in rcsv:
                    logging.info("%s,%s" % (row['board_name'],row['serial_number']))
                    self.boards_serials.append(row)
            else:
                return False
            
        return True
                
    def prepare(self):
        if self.boards_scripts == None or self.boards_serials == None:
            return False
        
        self.serials_scripts = []
        
        for scr in self.boards_scripts:
            for srl in self.boards_serials:
                if scr['board_name'] == srl['board_name']:
                    self.serials_scripts.append((srl['serial_number'],scr['script_path']))
                    break
        if len(self.serials_scripts) != len (self.boards_scripts):
            logging.error("Missing serial numbers in script files")
            return False
        
        self.serials_scripts = {}
        
        for scr in self.boards_scripts:
            for srl in self.boards_serials:
                if scr['board_name'] == srl['board_name']:
                    if srl['serial_number'] not in self.serials_scripts.keys():
                        self.serials_scripts[srl['serial_number']] = [scr['script_path']]
                    else:
                        self.serials_scripts[srl['serial_number']].append(scr['script_path'])
                    break
        
        return True
        
        
    def __init__(self, root=None):
        '''
        Constructor
        '''
#         TODO: Check if root is a string and a path
        self.files = None
        self.boards_scripts = None
        self.boards_serials = None
        if root != None:
            if os.path.isdir(root):
                self.scripts(root)