'''
Created on May 10, 2020

@author: Onkar.Raut
'''
import os
import csv
import glob
import logging

class Find(object):
    board_name_dict = {
            'ek_ra2a1':"EK-RA2A1",
            'ek_ra2l1':"EK-RA2L1",
            'ek_ra2e1':"EK-RA2E1" ,
            'ek_ra4m1':"EK-RA4M1" ,
            'ek_ra4m2':"EK-RA4M2" ,
            'ek_ra4m3':"EK-RA4M3" ,
            'ek_ra6m1':"EK-RA6M1" ,
            'ek_ra6m2':"EK-RA6M2" ,
            'ek_ra6m3':"EK-RA6M3" ,
            'ek_ra6m3g':"EK-RA6M3G",
            'ek_ra6t1':"EK-RA6T1" ,
            'ek_ra6m4':"EK-RA6M4" ,
            'ek_ra2l1':"EK-RA2L1" ,
            }
    board_mcu_dict = {
            'ek_ra2a1':"R7FA2A1AB",
            'ek_ra2l1':"ND",
            'ek_ra2e1':"ND" ,
            'ek_ra4m1':"R7FA4M1AB" ,
            'ek_ra4m2':"ND" ,
            'ek_ra4m3':"ND" ,
            'ek_ra6m1':"R7FA6M1AD" ,
            'ek_ra6m2':"R7FA6M2AF" ,
            'ek_ra6m3':"R7FA6M3AH" ,
            'ek_ra6m3g':"R7FA6M3AH",
            'ek_ra6t1':"ND" ,
            'ek_ra6m4':"ND" ,
            'ek_ra2l1':"ND" ,
            }
    def hex(self, root):
        '''
        Find Hex Files which can be programmed.
        '''
        fpath = os.path.join(root,"**","*.hex")
        files = glob.glob(fpath,recursive=True)
        
        logging.info("Files found.")
        for file in files:
            logging.info(file)
        self.files = files
        return
        
        
    def generate(self, hex_file_list = None):
        """
        device %(device)
        speed 4000
        if swd
        loadfile "(%filename)"
        rx 100
        st
        exit
        """
        
        jlink_search_patterns = []
        jlink_search_patterns.append(r"")
        
        
        for hexfile in hex_file_list:
            fpath, fname = os.path.split(hexfile)
            
            
            

        return
    
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
                self.boards_serials = {}
                logging.info("%s is a file containing board names and scripts" % csvFile)
                for row in rcsv:
                    logging.info("%s,%s" % (row['board_name'],row['serial_number']))
                    self.boards_serials[row['board_name']] = row['serial_number']
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
                    self.serials_scripts.append({r"serial_number":srl['serial_number'], r"script_path" :scr['script_path']})
                    break
        if len(self.serials_scripts) != len (self.boards_scripts):
            logging.error("Missing serial numbers in script files")
            return False
        
#         self.serials_scripts = {}
#         
#         for scr in self.boards_scripts:
#             for srl in self.boards_serials:
#                 if scr['board_name'] == srl['board_name']:
#                     if srl['serial_number'] not in self.serials_scripts.keys():
#                         self.serials_scripts[srl['serial_number']] = [scr['script_path']]
#                     else:
#                         self.serials_scripts[srl['serial_number']].append(scr['script_path'])
#                     break
        
        return True
    
    def write(self):
        with open(r"schedule.csv", 'w', newline='') as csvfile:
            fieldnames = [r"serial_number", r"script_path"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.serials_scripts:
                writer.writerow(row)
        return
        
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