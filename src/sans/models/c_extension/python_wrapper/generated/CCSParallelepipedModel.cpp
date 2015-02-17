/**
	This software was developed by the University of Tennessee as part of the
	Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
	project funded by the US National Science Foundation.

	If you use DANSE applications to do scientific research that leads to
	publication, we ask that you acknowledge the use of the software with the
	following sentence:

	"This work benefited from DANSE software developed under NSF award DMR-0520547."

	copyright 2008, University of Tennessee
 */

/** CCSParallelepipedModel
 *
 * C extension 
 *
 * WARNING: THIS FILE WAS GENERATED BY WRAPPERGENERATOR.PY
 *          DO NOT MODIFY THIS FILE, MODIFY src\sans\models\include\csparallelepiped.h
 *          AND RE-RUN THE GENERATOR SCRIPT
 *
 */
#define NO_IMPORT_ARRAY
#define PY_ARRAY_UNIQUE_SYMBOL PyArray_API_sans
 
extern "C" {
#include <Python.h>
#include <arrayobject.h>
#include "structmember.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

}

#include "csparallelepiped.h"
#include "dispersion_visitor.hh"

/// Error object for raised exceptions
static PyObject * CCSParallelepipedModelError = NULL;


// Class definition
typedef struct {
    PyObject_HEAD
    /// Parameters
    PyObject * params;
    /// Dispersion parameters
    PyObject * dispersion;
    /// Underlying model object
    CSParallelepipedModel * model;
    /// Log for unit testing
    PyObject * log;
} CCSParallelepipedModel;


static void
CCSParallelepipedModel_dealloc(CCSParallelepipedModel* self)
{
    Py_DECREF(self->params);
    Py_DECREF(self->dispersion);
    Py_DECREF(self->log);
    delete self->model;
    self->ob_type->tp_free((PyObject*)self);
    

}

static PyObject *
CCSParallelepipedModel_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    CCSParallelepipedModel *self;
    
    self = (CCSParallelepipedModel *)type->tp_alloc(type, 0);
   
    return (PyObject *)self;
}

static int
CCSParallelepipedModel_init(CCSParallelepipedModel *self, PyObject *args, PyObject *kwds)
{
    if (self != NULL) {
    	
    	// Create parameters
        self->params = PyDict_New();
        self->dispersion = PyDict_New();

	self->model = new CSParallelepipedModel();

        // Initialize parameter dictionary
        PyDict_SetItemString(self->params,"sld_rimB",Py_BuildValue("d",0.000004000000));
        PyDict_SetItemString(self->params,"sld_rimC",Py_BuildValue("d",0.000002000000));
        PyDict_SetItemString(self->params,"scale",Py_BuildValue("d",1.000000000000));
        PyDict_SetItemString(self->params,"background",Py_BuildValue("d",0.060000000000));
        PyDict_SetItemString(self->params,"parallel_psi",Py_BuildValue("d",0.000000000000));
        PyDict_SetItemString(self->params,"midB",Py_BuildValue("d",75.000000000000));
        PyDict_SetItemString(self->params,"parallel_theta",Py_BuildValue("d",0.000000000000));
        PyDict_SetItemString(self->params,"parallel_phi",Py_BuildValue("d",0.000000000000));
        PyDict_SetItemString(self->params,"sld_pcore",Py_BuildValue("d",0.000001000000));
        PyDict_SetItemString(self->params,"sld_rimA",Py_BuildValue("d",0.000002000000));
        PyDict_SetItemString(self->params,"shortA",Py_BuildValue("d",35.000000000000));
        PyDict_SetItemString(self->params,"rimB",Py_BuildValue("d",10.000000000000));
        PyDict_SetItemString(self->params,"rimC",Py_BuildValue("d",10.000000000000));
        PyDict_SetItemString(self->params,"longC",Py_BuildValue("d",400.000000000000));
        PyDict_SetItemString(self->params,"sld_solv",Py_BuildValue("d",0.000006000000));
        PyDict_SetItemString(self->params,"rimA",Py_BuildValue("d",10.000000000000));
        // Initialize dispersion / averaging parameter dict
        DispersionVisitor* visitor = new DispersionVisitor();
        PyObject * disp_dict;
        disp_dict = PyDict_New();
        self->model->shortA.dispersion->accept_as_source(visitor, self->model->shortA.dispersion, disp_dict);
        PyDict_SetItemString(self->dispersion, "shortA", disp_dict);
        disp_dict = PyDict_New();
        self->model->midB.dispersion->accept_as_source(visitor, self->model->midB.dispersion, disp_dict);
        PyDict_SetItemString(self->dispersion, "midB", disp_dict);
        disp_dict = PyDict_New();
        self->model->longC.dispersion->accept_as_source(visitor, self->model->longC.dispersion, disp_dict);
        PyDict_SetItemString(self->dispersion, "longC", disp_dict);
        disp_dict = PyDict_New();
        self->model->parallel_phi.dispersion->accept_as_source(visitor, self->model->parallel_phi.dispersion, disp_dict);
        PyDict_SetItemString(self->dispersion, "parallel_phi", disp_dict);
        disp_dict = PyDict_New();
        self->model->parallel_psi.dispersion->accept_as_source(visitor, self->model->parallel_psi.dispersion, disp_dict);
        PyDict_SetItemString(self->dispersion, "parallel_psi", disp_dict);
        disp_dict = PyDict_New();
        self->model->parallel_theta.dispersion->accept_as_source(visitor, self->model->parallel_theta.dispersion, disp_dict);
        PyDict_SetItemString(self->dispersion, "parallel_theta", disp_dict);


         
        // Create empty log
        self->log = PyDict_New();
        
        

    }
    return 0;
}

static char name_params[] = "params";
static char def_params[] = "Parameters";
static char name_dispersion[] = "dispersion";
static char def_dispersion[] = "Dispersion parameters";
static char name_log[] = "log";
static char def_log[] = "Log";

static PyMemberDef CCSParallelepipedModel_members[] = {
    {name_params, T_OBJECT, offsetof(CCSParallelepipedModel, params), 0, def_params},
	{name_dispersion, T_OBJECT, offsetof(CCSParallelepipedModel, dispersion), 0, def_dispersion},     
    {name_log, T_OBJECT, offsetof(CCSParallelepipedModel, log), 0, def_log},
    {NULL}  /* Sentinel */
};

/** Read double from PyObject
    @param p PyObject
    @return double
*/
double CCSParallelepipedModel_readDouble(PyObject *p) {
    if (PyFloat_Check(p)==1) {
        return (double)(((PyFloatObject *)(p))->ob_fval);
    } else if (PyInt_Check(p)==1) {
        return (double)(((PyIntObject *)(p))->ob_ival);
    } else if (PyLong_Check(p)==1) {
        return (double)PyLong_AsLong(p);
    } else {
        return 0.0;
    }
}
/**
 * Function to call to evaluate model
 * @param args: input numpy array q[] 
 * @return: numpy array object 
 */
 
static PyObject *evaluateOneDim(CSParallelepipedModel* model, PyArrayObject *q){
    PyArrayObject *result;
   
    // Check validity of array q , q must be of dimension 1, an array of double
    if (q->nd != 1 || q->descr->type_num != PyArray_DOUBLE)
    {
        //const char * message= "Invalid array: q->nd=%d,type_num=%d\n",q->nd,q->descr->type_num;
        //PyErr_SetString(PyExc_ValueError , message);
        return NULL;
    }
    result = (PyArrayObject *)PyArray_FromDims(q->nd, (int *)(q->dimensions), PyArray_DOUBLE);
	if (result == NULL) {
        const char * message= "Could not create result ";
        PyErr_SetString(PyExc_RuntimeError , message);
		return NULL;
	}
#pragma omp parallel for
	 for (int i = 0; i < q->dimensions[0]; i++){
      double q_value  = *(double *)(q->data + i*q->strides[0]);
      double *result_value = (double *)(result->data + i*result->strides[0]);
      *result_value =(*model)(q_value);
	}
    return PyArray_Return(result); 
 }

 /**
 * Function to call to evaluate model
 * @param args: input numpy array  [x[],y[]]
 * @return: numpy array object 
 */
 static PyObject * evaluateTwoDimXY( CSParallelepipedModel* model, 
                              PyArrayObject *x, PyArrayObject *y)
 {
    PyArrayObject *result;
    int x_len, y_len, dims[1];
    //check validity of input vectors
    if (x->nd != 1 || x->descr->type_num != PyArray_DOUBLE
        || y->nd != 1 || y->descr->type_num != PyArray_DOUBLE
        || y->dimensions[0] != x->dimensions[0]){
        const char * message= "evaluateTwoDimXY  expect 2 numpy arrays";
        PyErr_SetString(PyExc_ValueError , message); 
        return NULL;
    }
   
	if (PyArray_Check(x) && PyArray_Check(y)) {
		
	    x_len = dims[0]= x->dimensions[0];
        y_len = dims[0]= y->dimensions[0];
	    
	    // Make a new double matrix of same dims
        result=(PyArrayObject *) PyArray_FromDims(1,dims,NPY_DOUBLE);
        if (result == NULL){
	    const char * message= "Could not create result ";
        PyErr_SetString(PyExc_RuntimeError , message);
	    return NULL;
	    }
       
        /* Do the calculation. */
#pragma omp parallel for
        for (int i=0; i< x_len; i++) {
            double x_value = *(double *)(x->data + i*x->strides[0]);
  		    double y_value = *(double *)(y->data + i*y->strides[0]);
  			double *result_value = (double *)(result->data +
  			      i*result->strides[0]);
  			*result_value = (*model)(x_value, y_value);
        }           
        return PyArray_Return(result); 
        
        }else{
		    PyErr_SetString(CCSParallelepipedModelError, 
                   "CCSParallelepipedModel.evaluateTwoDimXY couldn't run.");
	        return NULL;
		}      	
}
/**
 *  evalDistribution function evaluate a model function with input vector
 *  @param args: input q as vector or [qx, qy] where qx, qy are vectors
 *
 */ 
static PyObject * evalDistribution(CCSParallelepipedModel *self, PyObject *args){
	PyObject *qx, *qy;
	PyArrayObject * pars;
	int npars ,mpars;
	
	// Get parameters
	
	    // Reader parameter dictionary
    self->model->sld_rimB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimB") );
    self->model->sld_rimC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimC") );
    self->model->scale = PyFloat_AsDouble( PyDict_GetItemString(self->params, "scale") );
    self->model->background = PyFloat_AsDouble( PyDict_GetItemString(self->params, "background") );
    self->model->parallel_psi = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_psi") );
    self->model->midB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "midB") );
    self->model->parallel_theta = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_theta") );
    self->model->parallel_phi = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_phi") );
    self->model->sld_pcore = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_pcore") );
    self->model->sld_rimA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimA") );
    self->model->shortA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "shortA") );
    self->model->rimB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimB") );
    self->model->rimC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimC") );
    self->model->longC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "longC") );
    self->model->sld_solv = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_solv") );
    self->model->rimA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimA") );
    // Read in dispersion parameters
    PyObject* disp_dict;
    DispersionVisitor* visitor = new DispersionVisitor();
    disp_dict = PyDict_GetItemString(self->dispersion, "shortA");
    self->model->shortA.dispersion->accept_as_destination(visitor, self->model->shortA.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "midB");
    self->model->midB.dispersion->accept_as_destination(visitor, self->model->midB.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "longC");
    self->model->longC.dispersion->accept_as_destination(visitor, self->model->longC.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_phi");
    self->model->parallel_phi.dispersion->accept_as_destination(visitor, self->model->parallel_phi.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_psi");
    self->model->parallel_psi.dispersion->accept_as_destination(visitor, self->model->parallel_psi.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_theta");
    self->model->parallel_theta.dispersion->accept_as_destination(visitor, self->model->parallel_theta.dispersion, disp_dict);

	
	// Get input and determine whether we have to supply a 1D or 2D return value.
	if ( !PyArg_ParseTuple(args,"O",&pars) ) {
	    PyErr_SetString(CCSParallelepipedModelError, 
	    	"CCSParallelepipedModel.evalDistribution expects a q value.");
		return NULL;
	}
    // Check params
	
    if(PyArray_Check(pars)==1) {
		
	    // Length of list should 1 or 2
	    npars = pars->nd; 
	    if(npars==1) {
	        // input is a numpy array
	        if (PyArray_Check(pars)) {
		        return evaluateOneDim(self->model, (PyArrayObject*)pars); 
		    }
		}else{
		    PyErr_SetString(CCSParallelepipedModelError, 
                   "CCSParallelepipedModel.evalDistribution expect numpy array of one dimension.");
	        return NULL;
		}
    }else if( PyList_Check(pars)==1) {
    	// Length of list should be 2 for I(qx,qy)
	    mpars = PyList_GET_SIZE(pars); 
	    if(mpars!=2) {
	    	PyErr_SetString(CCSParallelepipedModelError, 
	    		"CCSParallelepipedModel.evalDistribution expects a list of dimension 2.");
	    	return NULL;
	    }
	     qx = PyList_GET_ITEM(pars,0);
	     qy = PyList_GET_ITEM(pars,1);
	     if (PyArray_Check(qx) && PyArray_Check(qy)) {
	         return evaluateTwoDimXY(self->model, (PyArrayObject*)qx,
		           (PyArrayObject*)qy);
		 }else{
		    PyErr_SetString(CCSParallelepipedModelError, 
                   "CCSParallelepipedModel.evalDistribution expect 2 numpy arrays in list.");
	        return NULL;
	     }
	}
	PyErr_SetString(CCSParallelepipedModelError, 
                   "CCSParallelepipedModel.evalDistribution couln't be run.");
	return NULL;
	
}

/**
 * Function to call to evaluate model
 * @param args: input q or [q,phi]
 * @return: function value
 */
static PyObject * run(CCSParallelepipedModel *self, PyObject *args) {
	double q_value, phi_value;
	PyObject* pars;
	int npars;
	
	// Get parameters
	
	    // Reader parameter dictionary
    self->model->sld_rimB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimB") );
    self->model->sld_rimC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimC") );
    self->model->scale = PyFloat_AsDouble( PyDict_GetItemString(self->params, "scale") );
    self->model->background = PyFloat_AsDouble( PyDict_GetItemString(self->params, "background") );
    self->model->parallel_psi = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_psi") );
    self->model->midB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "midB") );
    self->model->parallel_theta = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_theta") );
    self->model->parallel_phi = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_phi") );
    self->model->sld_pcore = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_pcore") );
    self->model->sld_rimA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimA") );
    self->model->shortA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "shortA") );
    self->model->rimB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimB") );
    self->model->rimC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimC") );
    self->model->longC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "longC") );
    self->model->sld_solv = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_solv") );
    self->model->rimA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimA") );
    // Read in dispersion parameters
    PyObject* disp_dict;
    DispersionVisitor* visitor = new DispersionVisitor();
    disp_dict = PyDict_GetItemString(self->dispersion, "shortA");
    self->model->shortA.dispersion->accept_as_destination(visitor, self->model->shortA.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "midB");
    self->model->midB.dispersion->accept_as_destination(visitor, self->model->midB.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "longC");
    self->model->longC.dispersion->accept_as_destination(visitor, self->model->longC.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_phi");
    self->model->parallel_phi.dispersion->accept_as_destination(visitor, self->model->parallel_phi.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_psi");
    self->model->parallel_psi.dispersion->accept_as_destination(visitor, self->model->parallel_psi.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_theta");
    self->model->parallel_theta.dispersion->accept_as_destination(visitor, self->model->parallel_theta.dispersion, disp_dict);

	
	// Get input and determine whether we have to supply a 1D or 2D return value.
	if ( !PyArg_ParseTuple(args,"O",&pars) ) {
	    PyErr_SetString(CCSParallelepipedModelError, 
	    	"CCSParallelepipedModel.run expects a q value.");
		return NULL;
	}
	  
	// Check params
	if( PyList_Check(pars)==1) {
		
		// Length of list should be 2 for I(q,phi)
	    npars = PyList_GET_SIZE(pars); 
	    if(npars!=2) {
	    	PyErr_SetString(CCSParallelepipedModelError, 
	    		"CCSParallelepipedModel.run expects a double or a list of dimension 2.");
	    	return NULL;
	    }
	    // We have a vector q, get the q and phi values at which
	    // to evaluate I(q,phi)
	    q_value = CCSParallelepipedModel_readDouble(PyList_GET_ITEM(pars,0));
	    phi_value = CCSParallelepipedModel_readDouble(PyList_GET_ITEM(pars,1));
	    // Skip zero
	    if (q_value==0) {
	    	return Py_BuildValue("d",0.0);
	    }
		return Py_BuildValue("d",(*(self->model)).evaluate_rphi(q_value,phi_value));

	} else {

		// We have a scalar q, we will evaluate I(q)
		q_value = CCSParallelepipedModel_readDouble(pars);		
		
		return Py_BuildValue("d",(*(self->model))(q_value));
	}	
}
/**
 * Function to call to calculate_ER
 * @return: effective radius value 
 */
static PyObject * calculate_ER(CCSParallelepipedModel *self) {

	// Get parameters
	
	    // Reader parameter dictionary
    self->model->sld_rimB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimB") );
    self->model->sld_rimC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimC") );
    self->model->scale = PyFloat_AsDouble( PyDict_GetItemString(self->params, "scale") );
    self->model->background = PyFloat_AsDouble( PyDict_GetItemString(self->params, "background") );
    self->model->parallel_psi = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_psi") );
    self->model->midB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "midB") );
    self->model->parallel_theta = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_theta") );
    self->model->parallel_phi = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_phi") );
    self->model->sld_pcore = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_pcore") );
    self->model->sld_rimA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimA") );
    self->model->shortA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "shortA") );
    self->model->rimB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimB") );
    self->model->rimC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimC") );
    self->model->longC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "longC") );
    self->model->sld_solv = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_solv") );
    self->model->rimA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimA") );
    // Read in dispersion parameters
    PyObject* disp_dict;
    DispersionVisitor* visitor = new DispersionVisitor();
    disp_dict = PyDict_GetItemString(self->dispersion, "shortA");
    self->model->shortA.dispersion->accept_as_destination(visitor, self->model->shortA.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "midB");
    self->model->midB.dispersion->accept_as_destination(visitor, self->model->midB.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "longC");
    self->model->longC.dispersion->accept_as_destination(visitor, self->model->longC.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_phi");
    self->model->parallel_phi.dispersion->accept_as_destination(visitor, self->model->parallel_phi.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_psi");
    self->model->parallel_psi.dispersion->accept_as_destination(visitor, self->model->parallel_psi.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_theta");
    self->model->parallel_theta.dispersion->accept_as_destination(visitor, self->model->parallel_theta.dispersion, disp_dict);

		
	return Py_BuildValue("d",(*(self->model)).calculate_ER());

}
/**
 * Function to call to cal the ratio shell volume/ total volume
 * @return: the ratio shell volume/ total volume 
 */
static PyObject * calculate_VR(CCSParallelepipedModel *self) {

	// Get parameters
	
	    // Reader parameter dictionary
    self->model->sld_rimB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimB") );
    self->model->sld_rimC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimC") );
    self->model->scale = PyFloat_AsDouble( PyDict_GetItemString(self->params, "scale") );
    self->model->background = PyFloat_AsDouble( PyDict_GetItemString(self->params, "background") );
    self->model->parallel_psi = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_psi") );
    self->model->midB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "midB") );
    self->model->parallel_theta = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_theta") );
    self->model->parallel_phi = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_phi") );
    self->model->sld_pcore = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_pcore") );
    self->model->sld_rimA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimA") );
    self->model->shortA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "shortA") );
    self->model->rimB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimB") );
    self->model->rimC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimC") );
    self->model->longC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "longC") );
    self->model->sld_solv = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_solv") );
    self->model->rimA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimA") );
    // Read in dispersion parameters
    PyObject* disp_dict;
    DispersionVisitor* visitor = new DispersionVisitor();
    disp_dict = PyDict_GetItemString(self->dispersion, "shortA");
    self->model->shortA.dispersion->accept_as_destination(visitor, self->model->shortA.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "midB");
    self->model->midB.dispersion->accept_as_destination(visitor, self->model->midB.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "longC");
    self->model->longC.dispersion->accept_as_destination(visitor, self->model->longC.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_phi");
    self->model->parallel_phi.dispersion->accept_as_destination(visitor, self->model->parallel_phi.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_psi");
    self->model->parallel_psi.dispersion->accept_as_destination(visitor, self->model->parallel_psi.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_theta");
    self->model->parallel_theta.dispersion->accept_as_destination(visitor, self->model->parallel_theta.dispersion, disp_dict);

		
	return Py_BuildValue("d",(*(self->model)).calculate_VR());

}
/**
 * Function to call to evaluate model in cartesian coordinates
 * @param args: input q or [qx, qy]]
 * @return: function value
 */
static PyObject * runXY(CCSParallelepipedModel *self, PyObject *args) {
	double qx_value, qy_value;
	PyObject* pars;
	int npars;
	
	// Get parameters
	
	    // Reader parameter dictionary
    self->model->sld_rimB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimB") );
    self->model->sld_rimC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimC") );
    self->model->scale = PyFloat_AsDouble( PyDict_GetItemString(self->params, "scale") );
    self->model->background = PyFloat_AsDouble( PyDict_GetItemString(self->params, "background") );
    self->model->parallel_psi = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_psi") );
    self->model->midB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "midB") );
    self->model->parallel_theta = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_theta") );
    self->model->parallel_phi = PyFloat_AsDouble( PyDict_GetItemString(self->params, "parallel_phi") );
    self->model->sld_pcore = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_pcore") );
    self->model->sld_rimA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_rimA") );
    self->model->shortA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "shortA") );
    self->model->rimB = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimB") );
    self->model->rimC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimC") );
    self->model->longC = PyFloat_AsDouble( PyDict_GetItemString(self->params, "longC") );
    self->model->sld_solv = PyFloat_AsDouble( PyDict_GetItemString(self->params, "sld_solv") );
    self->model->rimA = PyFloat_AsDouble( PyDict_GetItemString(self->params, "rimA") );
    // Read in dispersion parameters
    PyObject* disp_dict;
    DispersionVisitor* visitor = new DispersionVisitor();
    disp_dict = PyDict_GetItemString(self->dispersion, "shortA");
    self->model->shortA.dispersion->accept_as_destination(visitor, self->model->shortA.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "midB");
    self->model->midB.dispersion->accept_as_destination(visitor, self->model->midB.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "longC");
    self->model->longC.dispersion->accept_as_destination(visitor, self->model->longC.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_phi");
    self->model->parallel_phi.dispersion->accept_as_destination(visitor, self->model->parallel_phi.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_psi");
    self->model->parallel_psi.dispersion->accept_as_destination(visitor, self->model->parallel_psi.dispersion, disp_dict);
    disp_dict = PyDict_GetItemString(self->dispersion, "parallel_theta");
    self->model->parallel_theta.dispersion->accept_as_destination(visitor, self->model->parallel_theta.dispersion, disp_dict);

	
	// Get input and determine whether we have to supply a 1D or 2D return value.
	if ( !PyArg_ParseTuple(args,"O",&pars) ) {
	    PyErr_SetString(CCSParallelepipedModelError, 
	    	"CCSParallelepipedModel.run expects a q value.");
		return NULL;
	}
	  
	// Check params
	if( PyList_Check(pars)==1) {
		
		// Length of list should be 2 for I(qx, qy))
	    npars = PyList_GET_SIZE(pars); 
	    if(npars!=2) {
	    	PyErr_SetString(CCSParallelepipedModelError, 
	    		"CCSParallelepipedModel.run expects a double or a list of dimension 2.");
	    	return NULL;
	    }
	    // We have a vector q, get the qx and qy values at which
	    // to evaluate I(qx,qy)
	    qx_value = CCSParallelepipedModel_readDouble(PyList_GET_ITEM(pars,0));
	    qy_value = CCSParallelepipedModel_readDouble(PyList_GET_ITEM(pars,1));
	    return Py_BuildValue("d",(*(self->model))(qx_value,qy_value));

	} else {

		// We have a scalar q, we will evaluate I(q)
		qx_value = CCSParallelepipedModel_readDouble(pars);		
		
		return Py_BuildValue("d",(*(self->model))(qx_value));
	}	
}

static PyObject * reset(CCSParallelepipedModel *self, PyObject *args) {
    

    return Py_BuildValue("d",0.0);
}

static PyObject * set_dispersion(CCSParallelepipedModel *self, PyObject *args) {
	PyObject * disp;
	const char * par_name;

	if ( !PyArg_ParseTuple(args,"sO", &par_name, &disp) ) {
	    PyErr_SetString(CCSParallelepipedModelError,
	    	"CCSParallelepipedModel.set_dispersion expects a DispersionModel object.");
		return NULL;
	}
	void *temp = PyCObject_AsVoidPtr(disp);
	DispersionModel * dispersion = static_cast<DispersionModel *>(temp);


	// Ugliness necessary to go from python to C
	    // TODO: refactor this
    if (!strcmp(par_name, "shortA")) {
        self->model->shortA.dispersion = dispersion;
    } else    if (!strcmp(par_name, "midB")) {
        self->model->midB.dispersion = dispersion;
    } else    if (!strcmp(par_name, "longC")) {
        self->model->longC.dispersion = dispersion;
    } else    if (!strcmp(par_name, "parallel_phi")) {
        self->model->parallel_phi.dispersion = dispersion;
    } else    if (!strcmp(par_name, "parallel_psi")) {
        self->model->parallel_psi.dispersion = dispersion;
    } else    if (!strcmp(par_name, "parallel_theta")) {
        self->model->parallel_theta.dispersion = dispersion;
    } else {
	    PyErr_SetString(CCSParallelepipedModelError,
	    	"CCSParallelepipedModel.set_dispersion expects a valid parameter name.");
		return NULL;
	}

	DispersionVisitor* visitor = new DispersionVisitor();
	PyObject * disp_dict = PyDict_New();
	dispersion->accept_as_source(visitor, dispersion, disp_dict);
	PyDict_SetItemString(self->dispersion, par_name, disp_dict);
    return Py_BuildValue("i",1);
}


static PyMethodDef CCSParallelepipedModel_methods[] = {
    {"run",      (PyCFunction)run     , METH_VARARGS,
      "Evaluate the model at a given Q or Q, phi"},
    {"runXY",      (PyCFunction)runXY     , METH_VARARGS,
      "Evaluate the model at a given Q or Qx, Qy"},
    {"calculate_ER",      (PyCFunction)calculate_ER     , METH_VARARGS,
      "Evaluate the model at a given Q or Q, phi"},
    {"calculate_VR",      (PyCFunction)calculate_VR     , METH_VARARGS,
      "Evaluate VR"},    
    {"evalDistribution",  (PyCFunction)evalDistribution , METH_VARARGS,
      "Evaluate the model at a given Q or Qx, Qy vector "},
    {"reset",    (PyCFunction)reset   , METH_VARARGS,
      "Reset pair correlation"},
    {"set_dispersion",      (PyCFunction)set_dispersion     , METH_VARARGS,
      "Set the dispersion model for a given parameter"},
   {NULL}
};

static PyTypeObject CCSParallelepipedModelType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "CCSParallelepipedModel",             /*tp_name*/
    sizeof(CCSParallelepipedModel),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)CCSParallelepipedModel_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "CCSParallelepipedModel objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    CCSParallelepipedModel_methods,             /* tp_methods */
    CCSParallelepipedModel_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CCSParallelepipedModel_init,      /* tp_init */
    0,                         /* tp_alloc */
    CCSParallelepipedModel_new,                 /* tp_new */
};


//static PyMethodDef module_methods[] = {
//    {NULL} 
//};

/**
 * Function used to add the model class to a module
 * @param module: module to add the class to
 */ 
void addCCSParallelepipedModel(PyObject *module) {
	PyObject *d;
	
    if (PyType_Ready(&CCSParallelepipedModelType) < 0)
        return;

    Py_INCREF(&CCSParallelepipedModelType);
    PyModule_AddObject(module, "CCSParallelepipedModel", (PyObject *)&CCSParallelepipedModelType);
    
    d = PyModule_GetDict(module);
    static char error_name[] = "CCSParallelepipedModel.error";
    CCSParallelepipedModelError = PyErr_NewException(error_name, NULL, NULL);
    PyDict_SetItemString(d, "CCSParallelepipedModelError", CCSParallelepipedModelError);
}
