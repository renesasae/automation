'''
Created on May 17, 2020

@author: Onkar.Raut
TODO: 
    1. Catergorize assertion failures as 'setup failure' or 'ep failure'
    2. More messages to each test case for enabling issues in future.
    3. Consider moving test_io_info to a text file.
    4. Consider how we can standardize this file.
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
    
    expected_common = r"""
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
""".replace('\n',"\r\n")
   
    test_io_info = [(b"1", r'Enter the DAC Value(0 - 4095) to Compare:'),
                    (b"0", r'Comparator Output is HIGH and Setting On-board LED HIGH'),
                    (b"1", r'Enter the DAC Value(0 - 4095) to Compare:'),
                    (b"2150", r'Comparator Output is HIGH and Setting On-board LED HIGH'),] 
    def setUp(self):
        # Reads EP version and FSP version from a file        
        jlinkDLLpath=None
        if platform.system()=='Windows':
            jlinkDLLpath=pylink.jlink.library.Library()
            jlinkDLLpath=r"C:\Program Files (x86)\SEGGER\JLink_V670\JLinkARM.dll"
        if platform.system()=='Linux':
            jlinkDLLpath=r"/usr/local/lib/libjlinkarm.so"    
        
        if os.path.exists(jlinkDLLpath)==True:
            jlinkDLLpath = os.path.normpath(jlinkDLLpath)
        
        self.jlinkDLL = jlinkDLLpath
        self.working_directory = os.getcwd()
        
        """ Get the board name based on the test name """
        sp = r"(test_(.*))"
        search_pattern = re.compile(sp)
        match = re.search(search_pattern, self._testMethodName)
        self.assertIsNotNone(match, "***SETUP FAILURE***:Invalid Test name")
        self.board_name = match.group(2)
#         os.chdir(os.path.dirname(os.path.realpath(__file__)))

        fpath, fname = os.path.split(__file__)
        sp = r"(_test_(.*).py)"
        
        search_pattern = re.compile(sp)
        match = re.search(search_pattern, fname)
        self.assertIsNotNone(match, "***SETUP FAILURE***:Invalid python unittest filename")
        self.module_name = match.group(2)
        self.hexfile = "_".join([self.module_name, self.board_name, "ep"])
        self.hexfile = self.hexfile + r".hex"
        
        """ Search recursively in curent working directory for matching files """
        fpath = os.path.join(fpath,"**",self.hexfile)
        self.files = glob.glob(fpath,recursive=True)
        self.assertGreater(len(self.files), 0, "***SETUP FAILURE***:Hex File %s Not found." % self.hexfile)
        
        self.assertIn(automation.rig.boards.names[self.board_name], automation.rig.boards.serials.keys(), 
                      "***SETUP FAILURE***: Board does not exist. Serial number for board cannot be calculated")
        self.serial_number = automation.rig.boards.serials[automation.rig.boards.names[self.board_name]]
        
        jlinklog=self.id()+".log"
        
        
        lib=pylink.library.Library()
        
        if None == lib.dll():
            if None == lib.load_default():
                lib=pylink.library.Library(self.jlinkDLL)
        
        log=jlinklog
        self.jlink = pylink.JLink(lib=lib)
        
        self.emuList = self.jlink.connected_emulators(host=pylink.enums.JLinkHost.USB)
        
        found = False
        
        for emu in self.emuList:
            if emu.SerialNumber == self.serial_number:
                found = True
                break
        
        if found == False:
            self.skipTest("***SETUP FAILURE***:Expected Emulator SN:%(sn)s not connected to the rig" % {"sn":self.serial_number})
        
        ''' Test if emulator is connected '''
        self.assertTrue(found, 
                      "***SETUP FAILURE***:Expected Emulator SN:%(sn)s not connected to the rig" % {"sn":self.serial_number})
        pass

    def tearDown(self):
#         os.chdir(self.working_directory)
        if self.jlink.opened() == True:
            self.jlink.close()
        pass


    def test_ek_ra2a1(self):
        """ Test ACMPLP Implementation on the EK-RA2A1"""
        for file in self.files:
            ''' Connect Emulator '''
            self.jlink.open(self.serial_number)
            self.assertTrue(self.jlink.opened(), "***SETUP FAILURE***:Jlink could not be opened")
            self.assertTrue(self.jlink.connected(), "***SETUP FAILURE***:Jlink not connected")
            
            ''' Connect to a Target CPU '''
            self.target_cpu = automation.rig.boards.mcus[automation.rig.boards.names[self.board_name]]       
            self.jlink.connect(self.target_cpu,speed=4000)
            
            self.assertTrue(self.jlink.target_connected(), "***SETUP FAILURE***:Jlink not connected")
            self.jlink.enable_reset_pulls_reset()
            self.jlink.enable_reset_pulls_trst()
            self.jlink.enable_reset_inits_registers()
    
            """ Disable dialog boxes """
            self.jlink.disable_dialog_boxes()
            
            """ Program the board """
            bytes_flashed = self.jlink.flash_file(path=file, addr=0, power_on=False)
            
            """ Close the emulator """
            if self.jlink.opened() == True:
                self.jlink.close()
            
            """ Open again """
            self.jlink.open(self.serial_number)
            self.assertTrue(self.jlink.opened(), "***SETUP FAILURE***:Jlink could not be opened")
            
            self.assertTrue(self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD),"***SETUP FAILURE***:Could not set JLink Target Interface to SWD")
            
            if self.jlink.target_connected()==False:
                self.jlink.connect(self.target_cpu,speed=4000)
            
            self.assertTrue(self.jlink.connected(), "***SETUP FAILURE***:Jlink not connected")
            self.assertTrue(self.jlink.target_connected(), "***SETUP FAILURE***:Jlink Target CPU not connected")
            
            """ Request RTT block to be located at 0x20002000 """
            self.jlink.rtt_start(0x20002000)
            
            """ Located RTT control block @ 0x200004F4 """
            """ Located RTT control block @ 0x20000000"""
            rtt_status = self.jlink.rtt_get_status()
            
            self.assertEqual(1, rtt_status.IsRunning, "***SETUP FAILURE***:Segger RTT interface not started")
            
            """ Assuming board is in an unknown state and no output is periodically produced."""
    #         if rtt_status.NumBytesTransferred == 0:
            """ Bring device to reset state """
            self.jlink.set_reset_pin_low()
            time.sleep(0.5)
            self.jlink.set_reset_pin_high()
            time.sleep(0.1)
            rtt_status = self.jlink.rtt_get_status()
            
            self.assertGreater(rtt_status.NumDownBuffers, 0, "***SETUP FAILURE***:NumDownbuffers set to 0")
            self.assertGreater(rtt_status.NumUpBuffers, 0, "***SETUP FAILURE***:NumUpbuffers set to 0")
            
            self.assertGreater(rtt_status.NumBytesTransferred, 0, "***COMPARE FAILURE***:Did not receive initialization bytes")
            
            """ Verify Initial bytes received """
            rtt_output = self.jlink.rtt_read(0, rtt_status.NumBytesTransferred)
            rtt_output_as_str = bytearray(rtt_output)
            rtt_output_as_str = rtt_output_as_str.decode("utf-8")
            self.assertIn(self.expected_common, rtt_output_as_str, "***COMPARE FAILURE***:Expected output not found in RTT output")
            
            """ Recursive test """
            bytes_rcvd = 0
            for io in self.test_io_info:
                bytes_rcvd = rtt_status.NumBytesTransferred
                if len(io[0]) > 0:
                    self.jlink.rtt_write(0, io[0])
                time.sleep(0.1)
                rtt_status = self.jlink.rtt_get_status()
                bytes_to_read = rtt_status.NumBytesTransferred - bytes_rcvd
                rtt_output = self.jlink.rtt_read(0, bytes_to_read)
                rtt_output_as_str = bytearray(rtt_output)
                rtt_output_as_str = rtt_output_as_str.decode("utf-8")
                self.assertIn(io[1], rtt_output_as_str, "***COMPARE FAILURE***:Expected output not found in rtt")
            
            """ Close the emulator """
            if self.jlink.opened() == True:
                self.jlink.close()
        pass
    
    def test_ek_ra4m1(self):
        """ Test ACMPLP Implementation on the EK-RA2A1"""
        for file in self.files:
            ''' Connect Emulator '''
            self.jlink.open(self.serial_number)
            self.assertTrue(self.jlink.opened(), "***SETUP FAILURE***:Jlink could not be opened")
            self.assertTrue(self.jlink.connected(), "***SETUP FAILURE***:Jlink not connected")
            
            ''' Connect to a Target CPU '''
            self.target_cpu = automation.rig.boards.mcus[automation.rig.boards.names[self.board_name]]       
            self.jlink.connect(self.target_cpu,speed=4000)
            
            self.assertTrue(self.jlink.target_connected(), "***SETUP FAILURE***:Jlink not connected")
            self.jlink.enable_reset_pulls_reset()
            self.jlink.enable_reset_pulls_trst()
            self.jlink.enable_reset_inits_registers()
    
            """ Disable dialog boxes """
            self.jlink.disable_dialog_boxes()
            
            """ Program the board """
            bytes_flashed = self.jlink.flash_file(path=file, addr=0, power_on=False)
            
            """ Close the emulator """
            if self.jlink.opened() == True:
                self.jlink.close()
            
            """ Open again """
            self.jlink.open(self.serial_number)
            self.assertTrue(self.jlink.opened(), "***SETUP FAILURE***:Jlink could not be opened")
            
            self.assertTrue(self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD),"***SETUP FAILURE***:Could not set JLink Target Interface to SWD")
            
            if self.jlink.target_connected()==False:
                self.jlink.connect(self.target_cpu,speed=4000)
            
            self.assertTrue(self.jlink.connected(), "***SETUP FAILURE***:Jlink not connected")
            self.assertTrue(self.jlink.target_connected(), "***SETUP FAILURE***:Jlink Target CPU not connected")
            
            """ Request RTT block to be located at 0x20002000 """
            self.jlink.rtt_start(0x20002000)
            
            """ Located RTT control block @ 0x200004F4 """
            """ Located RTT control block @ 0x20000000"""
            rtt_status = self.jlink.rtt_get_status()
            
            self.assertEqual(1, rtt_status.IsRunning, "***SETUP FAILURE***:Segger RTT interface not started")
            
            """ Assuming board is in an unknown state and no output is periodically produced."""
    #         if rtt_status.NumBytesTransferred == 0:
            """ Bring device to reset state """
            self.jlink.set_reset_pin_low()
            time.sleep(0.5)
            self.jlink.set_reset_pin_high()
            time.sleep(0.1)
            rtt_status = self.jlink.rtt_get_status()
            
            self.assertGreater(rtt_status.NumDownBuffers, 0, "***SETUP FAILURE***:NumDownbuffers set to 0")
            self.assertGreater(rtt_status.NumUpBuffers, 0, "***SETUP FAILURE***:NumUpbuffers set to 0")
            
            self.assertGreater(rtt_status.NumBytesTransferred, 0, "***COMPARE FAILURE***:Did not receive initialization bytes")
            
            """ Verify Initial bytes received """
            rtt_output = self.jlink.rtt_read(0, rtt_status.NumBytesTransferred)
            rtt_output_as_str = bytearray(rtt_output)
            rtt_output_as_str = rtt_output_as_str.decode("utf-8")
            self.assertIn(self.expected_common, rtt_output_as_str, "***COMPARE FAILURE***:Expected output not found in RTT output")
            
            """ Recursive test """
            bytes_rcvd = 0
            for io in self.test_io_info:
                bytes_rcvd = rtt_status.NumBytesTransferred
                if len(io[0]) > 0:
                    self.jlink.rtt_write(0, io[0])
                time.sleep(0.1)
                rtt_status = self.jlink.rtt_get_status()
                bytes_to_read = rtt_status.NumBytesTransferred - bytes_rcvd
                rtt_output = self.jlink.rtt_read(0, bytes_to_read)
                rtt_output_as_str = bytearray(rtt_output)
                rtt_output_as_str = rtt_output_as_str.decode("utf-8")
                self.assertIn(io[1], rtt_output_as_str, "***COMPARE FAILURE***:Expected output not found in rtt")
            
            """ Close the emulator """
            if self.jlink.opened() == True:
                self.jlink.close()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testInitial']
    unittest.main()