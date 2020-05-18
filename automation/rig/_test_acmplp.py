'''
Created on May 17, 2020

@author: Onkar.Raut
'''
import os
import re
import glob
import time
import pylink
import platform
import unittest
import automation.rig.boards



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
                
        pass


    def tearDown(self):
#         os.chdir(self.working_directory)
        if self.jlink.opened() == True:
            self.jlink.close()
        pass


    def testEKRA2A1(self):
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
        
        test_io_info = [(r"1", r""""""),]
        
        ''' Assume a hex file name based on the the unit test module name and test case.'''
        fpath, fname = os.path.split(__file__)
        search_patterns = []
        search_patterns.append(r"(_test_(.*).py)")
        
        for sp in search_patterns:
            search_pattern = re.compile(sp)
            match = re.search(search_pattern, fname)
            if match:
                self.pyfile = match.group(1)
                self.module_name = match.group(2)
                break
        
        self.board_name = r"ek_ra2a1"
        self.hexfile = "_".join([self.module_name, self.board_name, "ep"])
        self.hexfile = self.hexfile + r".hex"
        
        fpath = os.path.join(fpath,"**",self.hexfile)
        files = glob.glob(fpath,recursive=True)
        
        self.assertGreater(len(files), 0, "Hex File %s Not found." % self.hexfile)
#         self.assertEqual(len(files), 1, "Multiple Hex File %s found." % self.hexfile)
        
        self.assertIn(automation.rig.boards.names[self.board_name], automation.rig.boards.serials.keys(), 
                      "Board does not exist. Serial number for board cannot be calculated")
        self.serial_number = automation.rig.boards.serials[automation.rig.boards.names[self.board_name]]
        jlinklog=self.id()+".log"
        lib=pylink.library.Library(self.jlinkDLL)
        log=jlinklog
        self.jlink = pylink.JLink(lib=lib)
        
        self.emuList = self.jlink.connected_emulators(host=pylink.enums.JLinkHost.USB)
        
        found = False
        
        for emu in self.emuList:
            if emu.SerialNumber == self.serial_number:
                found = True
                break
        
        ''' Test if emulator is connected '''
        self.assertTrue(found, 
                      "Expected Emulator SN:%(sn)s not connected to the rig" % {"sn":self.serial_number})
        
        ''' Connect Emulator '''
        self.jlink.open(self.serial_number)
        self.assertTrue(self.jlink.opened(), "Jlink could not be opened")
        self.assertTrue(self.jlink.connected(), "Jlink not connected")
        
        ''' Connect to a Target CPU '''
        target_cpu = automation.rig.boards.mcus[automation.rig.boards.names[self.board_name]]       
        self.jlink.connect(target_cpu,speed=4000)
        
        self.assertTrue(self.jlink.target_connected(), "Jlink not connected")
        self.jlink.enable_reset_pulls_reset()
        self.jlink.enable_reset_pulls_trst()
        self.jlink.enable_reset_inits_registers()

        """ Disable dialog boxes """
#         self.jlink.disable_dialog_boxes()
        
        """ Program the board """
        bytes_flashed = self.jlink.flash_file(path=files[0], addr=0, on_progress=None, power_on=False)
        
        if self.jlink.halted() == False:
            self.jlink.halt()
        
        self.jlink.set_reset_pin_low()
        self.jlink.set_trst_pin_low()
        time.sleep(0.5)
        self.jlink.set_reset_pin_high()
        self.jlink.set_trst_pin_high()
        self.assertTrue(self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD),"Could not set JLink Target Interface to SWD")
        
        
#         self.jlink.reset(ms=750, halt=False)
             
        self.rtt_status = self.jlink.rtt_get_status()
        
#         self.assertEqual(self.rtt_status.IsRunning, 1, "RTT is not running")
#         self.assertGreater(self.rtt_status.NumDownBuffers, 0, "NumDownbuffers set to 0")
#         self.assertGreater(self.rtt_status.NumUpBuffers, 0, "NumUpbuffers set to 0")

        """ Start the RTT """
        if self.rtt_status.IsRunning != 1:
            self.jlink.rtt_start()
            self.rtt_status = self.jlink.rtt_get_status()
        
        if self.rtt_status.NumBytesRead == 0:
            self.jlink.set_reset_pin_low()
            self.jlink.set_trst_pin_low()
            time.sleep(0.5)
            self.jlink.set_reset_pin_high()
            self.jlink.set_trst_pin_high()
            self.rtt_status = self.jlink.rtt_get_status()
            num_bytes = self.rtt_status.NumBytesRead
            initial_output = self.jlink.rtt_read(0, num_bytes)
        
        
        
        
       
       
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testInitial']
    unittest.main()