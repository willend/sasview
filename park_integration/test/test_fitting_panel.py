"""
    Unit tests for fitting module 
"""
import unittest
from sans.guitools.plottables import Theory1D
from sans.guitools.plottables import Data1D
from sans.fit.ScipyFitting import Parameter
import math
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='test_log.txt',
                    filemode='w')
class testFitModule(unittest.TestCase):
    def test0(self):
        """ test fitting for two set of data  and one model B constraint"""
        from sans.fit.Loader import Load
        load= Load()
        #Load the first set of data
        load.set_filename("testdata1.txt")
        load.set_values()
        data1 = Data1D(x=[], y=[],dx=None, dy=None)
        load.load_data(data1)
        
        #Load the second set of data
        load.set_filename("testdata2.txt")
        load.set_values()
        data2 = Data1D(x=[], y=[],dx=None, dy=None)
        load.load_data(data2)
        
        #Importing the Fit module
        from sans.fit.Fitting import Fit
        fitter= Fit('park')
        # Receives the type of model for the fitting
        from sans.guitools.LineModel import LineModel
        model1  = LineModel()
        model2  = LineModel()
        
        #Do the fit
        
        fitter.set_model(model1,"M1",1, {'A':1,'B':1})
        fitter.set_data(data1,1)
       
        fitter.set_model(model2,"M2",2, {'A':'M1.A','B':'M1.B'})
        fitter.set_data(data2,2)
    
        
        chisqr1, out1, cov1,result= fitter.fit()
        self.assert_(chisqr1)
        print "chisqr1",chisqr1
        print "out1", out1
        print " cov1", cov1
        
    def test01(self):
        """ test fitting for two set of data  and one model B constraint"""
        from sans.fit.Loader import Load
        load= Load()
        #Load the first set of data
        load.set_filename("testdata1.txt")
        load.set_values()
        data1 = Data1D(x=[], y=[],dx=None, dy=None)
        load.load_data(data1)
        
        #Load the second set of data
        load.set_filename("testdata2.txt")
        load.set_values()
        data2 = Data1D(x=[], y=[],dx=None, dy=None)
        load.load_data(data2)
        
        #Importing the Fit module
        from sans.fit.Fitting import Fit
        fitter= Fit('park')
        # Receives the type of model for the fitting
        from sans.guitools.LineModel import LineModel
        model1  = LineModel()
        model2  = LineModel()
        
        #Do the fit
        
        fitter.set_model(model1,"M1",1, {'A':1,'B':1})
        fitter.set_data(data1,1)
       
        fitter.set_model(model2,"M2",2, {'A':'M1.A','B':'M1.B'})
        fitter.set_data(data2,2)
    
        
        chisqr1, out1, cov1= fitter.fit()
        print "chisqr1",chisqr1
        print "out1", out1
        print " cov1", cov1
       
      
    
    
    def test1(self):
        """ test fitting for two set of data  and one model 1 constraint"""
        from sans.fit.Loader import Load
        load= Load()
        #Load the first set of data
        load.set_filename("testdata_line.txt")
        load.set_values()
        data1 = Data1D(x=[], y=[],dx=None, dy=None)
        load.load_data(data1)
        
        #Load the second set of data
        load.set_filename("testdata_line1.txt")
        load.set_values()
        data2 = Data1D(x=[], y=[],dx=None, dy=None)
        load.load_data(data2)
        
        #Importing the Fit module
        from sans.fit.Fitting import Fit
        fitter= Fit('park')
        # Receives the type of model for the fitting
        from sans.guitools.LineModel import LineModel
        model1  = LineModel()
        model2  = LineModel()
        
        #Do the fit
        
        fitter.set_model(model1,"M1",1, {'A':1,'B':1})
        fitter.set_data(data1,1)
       
        fitter.set_model(model2,"M2",2, {'A':'M1.A','B':1})
        fitter.set_data(data2,2)
    
        
        chisqr1, out1, cov1= fitter.fit()
        print "chisqr1",chisqr1
        print "out1", out1
        print " cov1", cov1
       
      
    
    def test2(self):
        """ test fitting for two set of data  and one model no constraint"""
        from sans.fit.Loader import Load
        load= Load()
        #Load the first set of data
        load.set_filename("testdata_line.txt")
        load.set_values()
        data1 = Data1D(x=[], y=[],dx=None, dy=None)
        load.load_data(data1)
        
        #Load the second set of data
        load.set_filename("testdata_line1.txt")
        load.set_values()
        data2 = Data1D(x=[], y=[],dx=None, dy=None)
        load.load_data(data2)
        
        #Importing the Fit module
        from sans.fit.Fitting import Fit
        fitter= Fit('scipy')
        # Receives the type of model for the fitting
        from sans.guitools.LineModel import LineModel
        model1  = LineModel()
        model2  = LineModel()
        
        #Do the fit
        
        fitter.set_model(model1,"M1",1, {'A':1,'B':1})
        fitter.set_data(data1,1)
       
        fitter.set_model(model2,"M2",2, {'A':1,'B':1})
        fitter.set_data(data2,2)
    
        
        chisqr1, out1, cov1= fitter.fit()
        print "chisqr1",chisqr1
        print "out1", out1
        print " cov1", cov1
     
        
        fitter= Fit('park')
        # Receives the type of model for the fitting
        from sans.guitools.LineModel import LineModel
        model1  = LineModel()
        model2  = LineModel()
        
        #Do the fit
        
        fitter.set_model(model1,"M1",1, {'A':1,'B':1})
        fitter.set_data(data1,1)
       
        fitter.set_model(model2,"M2",2, {'A':1,'B':1})
        fitter.set_data(data2,2)
    
        
        chisqr2, out2, cov2,result= fitter.fit()
        print "chisqr2",chisqr2
        print "out2", out2
        print " cov2", cov2
        
        
       
    
      