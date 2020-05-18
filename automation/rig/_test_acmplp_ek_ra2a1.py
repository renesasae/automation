'''
Created on May 17, 2020

@author: Onkar.Raut
'''
import os
import re
import automation.rig.files
import pylink
import platform
import unittest


class Test(unittest.TestCase):
    jlink = None
    jlinkDLL = None
    working_directory = None
    emuList = None
    hexfile = None
    board_name = None
    module_name = None
    serial_number = None
    def setUp(self):
        # Reads EP version and FSP version from a file        
        jlinkDLLpath=None
        if platform.system()=='Windows':
            jlinkDLLpath=r"C:\Program Files (x86)\SEGGER\JLink_V670\JLinkARM.dll"
        if platform.system()=='Linux':
            jlinkDLLpath=r"/usr/local/lib/libjlinkarm.so"    
        
        if os.path.exists(jlinkDLLpath)==True:
            jlinkDLLpath = os.path.normpath(jlinkDLLpath)
        
        self.jlinkDLL = jlinkDLLpath
        self.working_directory = os.getcwd()
#         os.chdir(os.path.dirname(os.path.realpath(__file__)))
        lib = pylink.library.Library(self.jlinkDLL)
        self.jlink = pylink.JLink(lib)
        self.emuList = self.jlink.connected_emulators(host=pylink.enums.JLinkHost.USB)
        
        ''' Assume a hex file name based on the the unit test name.'''
        fpath, fname = os.path.split(__file__)
        search_patterns = []
        search_patterns.append(r"(_test_(.*)_(ek_.*).py)")
        
        for sp in search_patterns:
            search_pattern = re.compile(sp)
            match = re.search(search_pattern, fname)
            if match:
                self.pyfile = match.group(1)
                self.module_name = match.group(2)
                self.board_name = match.group(3)
                self.hexfile = "_".join([self.module_name, self.board_name, "ep"])
                self.hexfile = self.hexfile + r".hex"
        self.assertTrue(os.path.exists(os.path.join(fpath,self.hexfile)))
        
        ''' Select the right emulator based on the board name'''
        flist = automation.rig.files.Find()
        flist.readcsv(r"C:\Users\onkar.raut\Documents\2020H1\LiClipse\testing\automation\board_programs.csv")
        flist.readcsv(r"C:\Users\onkar.raut\Documents\2020H1\LiClipse\testing\automation\serial_number_definitions.csv")
        
        self.assertIn(self.board_name, flist.board_name_dict.keys(), "Board does not exist. Serial number for board cannot be calculated")
        
        self.serial_number = flist.boards_serials[flist.board_name_dict[self.board_name]]
        
        self.serial_number = int(self.serial_number)
        
        ''' Test if emulator is connected '''
        self.assertIn(self.serial_number, self.emuList, "Expected Emulator SN:%(sn)s not connected to the rig" % {"sn":self.serial_number})

        ''' Connect Emulator '''
        self.jlink.open(self.serial_number)
        
        
        ''' Download firmware file '''
        
        pass


    def tearDown(self):
#         os.chdir(self.working_directory)
        pass


    def testRA2A1(self):
        expected = """
******************************************************************
*   Renesas FSP Example Project for r_acmplp Module              *
*   Example Project Version 1.0                                  *
*   Flex Software Pack Version  1.0.0                            *
******************************************************************

Refer to readme.txt file for more details on Example Project and 
FSP User's Manual for more information about r_acmplp driver

The project initializes ACMPLP module in Normal mode.
In Normal mode, user can enter DAC value(input to ACMPLP) within permitted range(0-4095).
When DAC input value is greater than set reference voltage(another input to ACMPLP),
Comparator output status is HIGH and on-board LED is turned ON.
If the output status (when DAC input less than ref voltage) is LOW,then the LED is turned OFF.

 Menu Options
 1. Enter 1 for ACMPLP Normal Mode
 2. Enter 2 for Exit
        """
        lib = pylink.library.Library(self.jlinkDLL)
        
        ''' Assume a hex file name based on the the unit test name.'''
        fpath, fname = os.path.split(__file__)
        search_patterns = []
        search_patterns.append(r"(_test_(.*)_(ek_.*).py)")
        
        
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testInitial']
    unittest.main()