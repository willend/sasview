#!/usr/bin/env python
"""
	This software was developed by the University of Tennessee as part of the
	Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
	project funded by the US National Science Foundation.

	If you use DANSE applications to do scientific research that leads to
	publication, we ask that you acknowledge the use of the software with the
	following sentence:

	"This work benefited from DANSE software developed under NSF award DMR-0520547."

	copyright 2008, University of Tennessee
"""

""" Provide functionality for a C extension model

	WARNING: THIS FILE WAS GENERATED BY WRAPPERGENERATOR.PY
 	         DO NOT MODIFY THIS FILE, MODIFY ../c_extensions/elliptical_cylinder.h
 	         AND RE-RUN THE GENERATOR SCRIPT

"""

from sans.models.BaseComponent import BaseComponent
from sans_extension.c_models import CEllipticalCylinderModel
import copy    
    
class EllipticalCylinderModel(CEllipticalCylinderModel, BaseComponent):
    """ Class that evaluates a EllipticalCylinderModel model. 
    	This file was auto-generated from ../c_extensions/elliptical_cylinder.h.
    	Refer to that file and the structure it contains
    	for details of the model.
    	List of default parameters:
         scale           = 1.0 
         r_minor         = 20.0 A
         r_ratio         = 1.5 A
         length          = 400.0 A
         contrast        = 3e-006 A-2
         background      = 0.0 cm-1
         cyl_theta       = 1.57 rad
         cyl_phi         = 0.0 rad
         cyl_psi         = 0.0 rad

    """
        
    def __init__(self):
        """ Initialization """
        
        # Initialize BaseComponent first, then sphere
        BaseComponent.__init__(self)
        CEllipticalCylinderModel.__init__(self)
        
        ## Name of the model
        self.name = "EllipticalCylinderModel"

		## Parameter details [units, min, max]
        self.details = {}
        self.details['scale'] = ['', None, None]
        self.details['r_minor'] = ['A', None, None]
        self.details['r_ratio'] = ['A', None, None]
        self.details['length'] = ['A', None, None]
        self.details['contrast'] = ['A-2', None, None]
        self.details['background'] = ['cm-1', None, None]
        self.details['cyl_theta'] = ['rad', None, None]
        self.details['cyl_phi'] = ['rad', None, None]
        self.details['cyl_psi'] = ['rad', None, None]

   
    def clone(self):
        """ Return a identical copy of self """
        obj = EllipticalCylinderModel()
        obj.params = copy.deepcopy(self.params)
        return obj   
   
    def run(self, x = 0.0):
        """ Evaluate the model
            @param x: input q, or [q,phi]
            @return: scattering function P(q)
        """
        
        return CEllipticalCylinderModel.run(self, x)
   
    def runXY(self, x = 0.0):
        """ Evaluate the model in cartesian coordinates
            @param x: input q, or [qx, qy]
            @return: scattering function P(q)
        """
        
        return CEllipticalCylinderModel.runXY(self, x)
        
    def set_dispersion(self, parameter, dispersion):
        """
            Set the dispersion object for a model parameter
            @param parameter: name of the parameter [string]
            @dispersion: dispersion object of type DispersionModel
        """
        return CEllipticalCylinderModel.set_dispersion(self, parameter, dispersion.cdisp)
        
   
# End of file
