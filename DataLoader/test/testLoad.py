"""
    Unit tests for DataLoader module 
    log file "test_log.txt" contains all errors when running loader
    It is create in the folder where test is runned
"""
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='test_log.txt',
                    filemode='w')



import unittest
import math
import DataLoader
from DataLoader.loader import  Loader
 
import os.path

class designtest(unittest.TestCase):
    
    def setUp(self):
        self.loader = Loader()
        
        
    def test_singleton(self):
        """
            Testing whether Loader is truly a singleton
        """
        # Set a new data member
        self.loader._test_data_member = 1.45
        
        # Create a 'new' Loader
        b = Loader()
        
        # Test that the new loader has the new data member
        self.assertEqual(b._test_data_member, self.loader._test_data_member)

class testLoader(unittest.TestCase):
    logging.debug("Inside testLoad module")
    
    """ test fitting """
    def setUp(self):
        """
            Set up the initial conditions before _each_ test
            so that they all start from the same well-defined state. 
        """
        #Creating a loader
        self.L=Loader()
        
     
    def testLoad0(self):
        """test reading empty file"""
        self.assertEqual(self.L.load('empty.txt'),None)
        
    def testLoad1(self):
        """test reading 2 columns"""
        
        #Testing loading a txt file of 2 columns, the only reader should be read1 
        output=self.L.load('test_2_columns.txt') 
        x=[2.83954,0.204082,0.408163,0.612245,0.816327,1.02041,1.22449,1.42857,1.63265]
        y=[0.6,3.44938, 5.82026,5.27591,5.2781,5.22531,7.47487,7.85852,10.2278]
        dx=[]
        dy=[]
        self.assertEqual(len(output.x),len(x))
        self.assertEqual(len(output.y),len(y))
        
        for i in range(len(x)):
            self.assertEqual(output.x[i],x[i])
            self.assertEqual(output.y[i],y[i])
       
    
    def testLoad2(self):
        """Testing loading a txt file of 3 columns"""
        output= self.L.load('test_3_columns.txt') 
        x=[0,0.204082,0.408163,0.612245,0.816327,1.02041,1.22449]    
        y=[2.83954,3.44938,5.82026,5.27591,5.2781,5.22531,7.47487]
        dx=[]
        dy=[0.6,0.676531,0.753061,0.829592,0.906122,0.982653,1.05918]
        self.assertEqual(len(output.x),len(x))
        self.assertEqual(len(output.y),len(y))
        self.assertEqual(len(output.dy),len(dy))
        for i in range(len(x)):
            self.assertEqual(output.x[i],x[i])
            self.assertEqual(output.y[i],y[i])
            self.assertEqual(output.dy[i],dy[i])
       
    
    def testload3(self):
        """ Testing loading Igor data"""
        #tested good file.asc
        output= self.L.load('MAR07232_rest.ASC') 
        self.assertEqual(output.xmin,-0.018558945804750416)
        self.assertEqual(output.xmax, 0.016234058202440633,)
        self.assertEqual(output.ymin,-0.01684257151702391)
        self.assertEqual(output.ymax,0.017950440578015116)
       
        #tested corrupted file.asc
        try:self.L.load('AR07232_rest.ASC')
        except ValueError,msg:
           #logging.log(10,str(msg))
           logging.error(str(msg))
    def testload4(self):
        """ Testing loading danse file"""
        #tested good file.sans
        output=self.L.load('MP_New.sans')
        
        self.assertEqual(output.wavelength,7.5)
        
        #tested corrupted file.sans
        try: self.L.load('P_New.sans')
        except ValueError,msg:
           #logging.log(40,str(msg))
           logging.error(str(msg))
        #else: raise ValueError,"No error raised for missing extension"
        
    def testload5(self):
        """ Testing loading image file"""
        output=self.L.load('angles_flat.png')
        self.assertEqual(output.xbins ,200)
        
    def testload6(self):
        """test file with unknown extension"""
        try:self.L.load('hello.missing')
        except RuntimeError,msg:
           self.assertEqual( str(msg),"Unknown file type '.missing'")
        else: raise ValueError,"No error raised for missing extension"
        
        #self.L.lookup('hello.missing')
        try: self.L.lookup('hello.missing')
        except RuntimeError,msg:
           self.assertEqual( str(msg),"Unknown file type '.missing'")
        else: raise ValueError,"No error raised for missing extension"
        
    def testload7(self):
        """ test file containing an image but as extension .txt"""
        self.assertEqual(self.L.load('angles_flat.txt'),None)

if __name__ == '__main__':
    unittest.main()
   