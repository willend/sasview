
import math
import wx
#from copy import deepcopy
from BaseInteractor import _BaseInteractor
from sans.guicomm.events import NewPlotEvent
from sans.guicomm.events import StatusEvent
from sans.guicomm.events import SlicerParameterEvent
from sans.guicomm.events import EVT_SLICER_PARS
from sans.guiframe.dataFitting import Data1D


class SectorInteractor(_BaseInteractor):
    """
    Draw a sector slicer.Allow to performQ averaging on data 2D
    """
    def __init__(self, base, axes, color='black', zorder=3):
        
        _BaseInteractor.__init__(self, base, axes, color=color)
        ## Class initialization
        self.markers = []
        self.axes = axes   
        ## connect the plot to event 
        self.connect = self.base.connect
        
        ## compute qmax limit to reset the graph     
        x = math.pow(max(self.base.data2D.xmax, 
                         math.fabs(self.base.data2D.xmin)), 2)
        y = math.pow(max(self.base.data2D.ymax, 
                         math.fabs(self.base.data2D.ymin)), 2)
        self.qmax = math.sqrt(x + y)
        ## Number of points on the plot
        self.nbins = 20
        ## Angle of the middle line
        self.theta2 = math.pi/3
        ## Absolute value of the Angle between the middle line and any side line
        self.phi = math.pi/12
        ## Middle line
        self.main_line = LineInteractor(self, self.base.subplot, color='blue', 
                                        zorder=zorder, r=self.qmax,
                                           theta= self.theta2)
        self.main_line.qmax = self.qmax
        ## Right Side line
        self.right_line = SideInteractor(self, self.base.subplot, color='black',
                                          zorder=zorder, r=self.qmax,
                                          phi=-1*self.phi, theta2=self.theta2)
        self.right_line.qmax = self.qmax
        ## Left Side line 
        self.left_line = SideInteractor(self, self.base.subplot, color='black',
                                        zorder=zorder, r=self.qmax,
                                           phi=self.phi, theta2=self.theta2)
        self.left_line.qmax = self.qmax
        ## draw the sector               
        self.update()
        self._post_data()
        ## Bind to slice parameter events
        self.base.Bind(EVT_SLICER_PARS, self._onEVT_SLICER_PARS)

    def _onEVT_SLICER_PARS(self, event):
        """
        receive an event containing parameters values to reset the slicer
        
        :param event: event of type SlicerParameterEvent with params as 
        attribute
        
        """
        wx.PostEvent(self.base.parent,
                     StatusEvent(status="SectorSlicer._onEVT_SLICER_PARS"))
        event.Skip()
        if event.type == self.__class__.__name__:
            self.set_params(event.params)
            self.base.update()
            
    def set_layer(self, n):
        """
         Allow adding plot to the same panel
         
        :param n: the number of layer
        
        """
        self.layernum = n
        self.update()
        
    def clear(self):
        """
        Clear the slicer and all connected events related to this slicer
        """
        self.clear_markers()
        self.main_line.clear()
        self.left_line.clear()
        self.right_line.clear()
        self.base.connect.clearall()
        self.base.Unbind(EVT_SLICER_PARS)
        
    def update(self):
        """
        Respond to changes in the model by recalculating the profiles and
        resetting the widgets.
        """
        # Update locations  
        ## Check if the middle line was dragged and 
        #update the picture accordingly     
        if self.main_line.has_move:
            self.main_line.update()
            self.right_line.update(delta=-self.left_line.phi/2,
                                    mline=self.main_line.theta)
            self.left_line.update(delta=self.left_line.phi/2,
                                   mline=self.main_line.theta)
        ## Check if the left side has moved and update the slicer accordingly  
        if self.left_line.has_move:
            self.main_line.update()
            self.left_line.update(phi=None, delta=None, mline=self.main_line,
                                  side=True, left=True)
            self.right_line.update(phi=self.left_line.phi, delta=None,
                                     mline=self.main_line, side=True,
                                     left=False, right=True)
        ## Check if the right side line has moved and 
        #update the slicer accordingly
        if self.right_line.has_move:
            self.main_line.update()
            self.right_line.update(phi=None, delta=None, mline=self.main_line,
                                   side=True, left=False, right=True)
            self.left_line.update(phi=self.right_line.phi, delta=None,
                                    mline=self.main_line, side=True, left=False)
            
    def save(self, ev):
        """
        Remember the roughness for this layer and the next so that we
        can restore on Esc.
        """
        self.base.freeze_axes()
        self.main_line.save(ev)
        self.right_line.save(ev)
        self.left_line.save(ev)

    def _post_data(self, nbins=None):
        """
        compute sector averaging of data2D into data1D
        
        :param nbins: the number of point to plot for the average 1D data
        """
        ## get the data2D to average
        data = self.base.data2D
        # If we have no data, just return
        if data == None:
            return
        ## Averaging
        from DataLoader.manipulations import SectorQ
        radius = self.qmax 
        phimin =  -self.left_line.phi + self.main_line.theta
        phimax = self.left_line.phi + self.main_line.theta
        if nbins == None:
            nbins = 20
        sect = SectorQ(r_min=0.0, r_max=radius,
                        phi_min=phimin + math.pi,
                        phi_max=phimax + math.pi, nbins=nbins)
     
        sector = sect(self.base.data2D)
        ##Create 1D data resulting from average
       
        if hasattr(sector, "dxl"):
            dxl = sector.dxl
        else:
            dxl = None
        if hasattr(sector, "dxw"):
            dxw = sector.dxw
        else:
            dxw = None
        new_plot = Data1D(x=sector.x, y=sector.y, dy=sector.dy)
        new_plot.dxl = dxl
        new_plot.dxw = dxw
        new_plot.name = "SectorQ" + "(" + self.base.data2D.name + ")"
        new_plot.source = self.base.data2D.source
        #new_plot.info=self.base.data2D.info
        new_plot.interactive = True
        new_plot.detector = self.base.data2D.detector
        # If the data file does not tell us what the axes are, just assume...
        new_plot.xaxis("\\rm{Q}", 'A^{-1}')
        new_plot.yaxis("\\rm{Intensity} ", "cm^{-1}")
        new_plot.group_id = "SectorQ" + self.base.data2D.name
        new_plot.id = "SectorQ" + self.base.data2D.name
        new_plot.is_data = True
        wx.PostEvent(self.base.parent, NewPlotEvent(plot=new_plot,
                                    title="SectorQ" + self.base.data2D.name))
        
    def moveend(self, ev):
        """
        Called a dragging motion ends.Get slicer event 
        """
        self.base.thaw_axes()
        ## Post parameters
        event = SlicerParameterEvent()
        event.type = self.__class__.__name__
        event.params = self.get_params()
        ## Send slicer paramers to plotter2D
        wx.PostEvent(self.base, event)
        
    def restore(self):
        """
        Restore the roughness for this layer.
        """
        self.main_line.restore()
        self.left_line.restore()
        self.right_line.restore()

    def move(self, x, y, ev):
        """
        Process move to a new position, making sure that the move is allowed.
        """
        pass
        
    def set_cursor(self, x, y):
        """
        """
        pass
        
    def get_params(self):
        """
        Store a copy of values of parameters of the slicer into a dictionary.
        
        :return params: the dictionary created
        
        """
        params = {}
        ## Always make sure that the left and the right line are at phi 
        ## angle of the middle line
        if math.fabs(self.left_line.phi) != math.fabs(self.right_line.phi):
            msg = "Phi left and phi right are different"
            msg += " %f, %f" % (self.left_line.phi, self.right_line.phi)
            raise ValueError, msg
        params["Phi"] = self.main_line.theta
        params["Delta_Phi"] = math.fabs(self.left_line.phi)
        params["nbins"] = self.nbins
        return params
    
    def set_params(self, params):
        """
        Receive a dictionary and reset the slicer with values contained 
        in the values of the dictionary.
        
        :param params: a dictionary containing name of slicer parameters and 
            values the user assigned to the slicer.
        """
        main = params["Phi"] 
        phi = math.fabs(params["Delta_Phi"])
        self.nbins = int(params["nbins"])
        self.main_line.theta = main
        ## Reset the slicer parameters
        self.main_line.update()
        self.right_line.update(phi=phi, delta=None, mline=self.main_line,
                               side=True, right=True)
        self.left_line.update(phi=phi, delta=None, 
                              mline=self.main_line, side=True)
        ## post the new corresponding data
        self._post_data(nbins=self.nbins)
        
    def freeze_axes(self):
        """
        """
        self.base.freeze_axes()
    
    def thaw_axes(self):
        """
        """
        self.base.thaw_axes()

    def draw(self):
        """
        """
        self.base.draw()

        
class SideInteractor(_BaseInteractor):
    """
    Draw an oblique line
    
    :param phi: the phase between the middle line and one side line
    :param theta2: the angle between the middle line and x- axis
    
    """
    def __init__(self, base, axes, color='black', zorder=5, r=1.0,
                 phi=math.pi/4, theta2= math.pi/3):
        """
        """
        _BaseInteractor.__init__(self, base, axes, color=color)
        ## Initialize the class
        self.markers = []
        self.axes = axes
        ## compute the value of the angle between the current line and
        ## the x-axis  
        self.save_theta = theta2 + phi
        self.theta = theta2 + phi
        ## the value of the middle line angle with respect to the x-axis
        self.theta2 = theta2
        ## Radius to find polar coordinates this line's endpoints
        self.radius = r
        ## phi is the phase between the current line and the middle line
        self.phi = phi
        ## End points polar coordinates
        x1 = self.radius * math.cos(self.theta)
        y1 = self.radius * math.sin(self.theta)
        x2 = -1 * self.radius * math.cos(self.theta)
        y2 = -1 * self.radius * math.sin(self.theta)
        ## defining a new marker 
        try:
            self.inner_marker = self.axes.plot([x1/2.5], [y1/2.5], linestyle='',
                                          marker='s', markersize=10,
                                          color=self.color, alpha=0.6,
                                          pickradius=5, label="pick", 
                                          # Prefer this to other lines
                                          zorder=zorder, visible=True)[0]
        except:
            self.inner_marker = self.axes.plot([x1/2.5],[y1/2.5], linestyle='',
                                          marker='s', markersize=10,
                                          color=self.color, alpha=0.6,
                                          label="pick", visible=True)[0]
            message  = "\nTHIS PROTOTYPE NEEDS THE LATEST"
            message += " VERSION OF MATPLOTLIB\n Get the SVN version that"
            message += " is at least as recent as June 1, 2007"
            owner = self.base.base.parent
            wx.PostEvent(owner, 
                         StatusEvent(status="sectorSlicer: %s" % message))
        
        ## Defining the current line
        self.line = self.axes.plot([x1, x2], [y1, y2],
                                      linestyle='-', marker='',
                                      color=self.color, visible=True)[0]
        ## Flag to differentiate the left line from the right line motion
        self.left_moving = False
        ## Flag to define a motion
        self.has_move = False
        ## connecting markers and draw the picture
        self.connect_markers([self.inner_marker, self.line])
       
    def set_layer(self, n):
        """
        Allow adding plot to the same panel
         
        :param n: the number of layer
        
        """
        self.layernum = n
        self.update()
        
    def clear(self):
        """
        Clear the slicer and all connected events related to this slicer
        """
        self.clear_markers()
        try:
            self.line.remove()
            self.inner_marker.remove()
        except:
            # Old version of matplotlib
            for item in range(len(self.axes.lines)):
                del self.axes.lines[0]
    
    def update(self, phi=None, delta=None, mline=None,
               side=False, left= False, right=False):
        """
        Draw oblique line
        
        :param phi: the phase between the middle line and the current line
        :param delta: phi/2 applied only when the mline was moved
        
        """
        #print "update left or right ", self.has_move
        self.left_moving = left
        theta3 = 0
        if phi != None:
            self.phi = phi
        if delta == None:
            delta = 0
        if  right:
            self.phi = -1 * math.fabs(self.phi)
            #delta=-delta
        else:
            self.phi = math.fabs(self.phi)
        if side:
            self.theta = mline.theta + self.phi
                    
        if mline != None :
            if delta != 0:
                self.theta2 = mline + delta
            else:
                self.theta2 = mline.theta
        if delta == 0:
            theta3 = self.theta + delta
        else:
            theta3 = self.theta2 + delta
        x1 = self.radius * math.cos(theta3)
        y1 = self.radius * math.sin(theta3)
        x2 = -1 * self.radius * math.cos(theta3)
        y2 = -1 * self.radius * math.sin(theta3)
        self.inner_marker.set(xdata=[x1/2.5], ydata=[y1/2.5])
        self.line.set(xdata=[x1, x2], ydata=[y1, y2])  
        
    def save(self, ev):
        """
        Remember the roughness for this layer and the next so that we
        can restore on Esc.
        """
        self.save_theta = self.theta
        self.base.freeze_axes()

    def moveend(self, ev):
        """
        """
        self.has_move = False
        self.base.moveend(ev)
            
    def restore(self):
        """
        Restore the roughness for this layer.
        """
        self.theta = self.save_theta

    def move(self, x, y, ev):
        """
        Process move to a new position, making sure that the move is allowed.
        """
        self.theta = math.atan2(y, x)
        self.has_move = True
        #ToDo: Simplify below
        if not self.left_moving:
            if  self.theta2 - self.theta <= 0 and self.theta2 > 0:
                self.restore()
                return 
            elif self.theta2 < 0 and self.theta < 0 and \
                self.theta-self.theta2 >= 0:
                self.restore()
                return                             
            elif  self.theta2 < 0 and self.theta > 0 and \
                (self.theta2 + 2 * math.pi - self.theta) >= math.pi/2:
                #print "my theta", self.theta
                self.restore()
                return 
            elif  self.theta2 < 0 and self.theta < 0 and \
                (self.theta2 - self.theta) >= math.pi/2:
                #print "my theta", self.theta
                self.restore()
                return 
            elif self.theta2 > 0 and (self.theta2-self.theta >= math.pi/2 or \
                (self.theta2-self.theta >= math.pi/2)):
                #print "self theta encore"
                self.restore()
                return 
        else:
            #print "left move"
            if  self.theta < 0 and (self.theta + math.pi*2-self.theta2) <= 0:
                self.restore()
                return 
            elif self.theta2 < 0 and (self.theta-self.theta2) <= 0:
                self.restore()
                return                             
            elif  self.theta > 0 and self.theta-self.theta2 <= 0:
                #print "my theta", self.theta
                self.restore()
                return 
            elif self.theta-self.theta2 >= math.pi/2 or  \
                ((self.theta + math.pi * 2 - self.theta2) >= math.pi/2 and \
                 self.theta < 0 and self.theta2 > 0):
                #print "self theta encore"
                self.restore()
                return 
            
        self.phi = math.fabs(self.theta2 - self.theta)
        if self.phi > math.pi:
            self.phi = 2 * math.pi - math.fabs(self.theta2 - self.theta)
        self.base.base.update()
        
    def set_cursor(self, x, y):
        """
        """
        self.move(x, y, None)
        self.update()
    
    def get_params(self):
        """
        """
        params = {}
        params["radius"] = self.radius
        params["theta"] = self.theta
        return params
    
    def set_params(self, params):
        """
        """
        x = params["radius"] 
        self.set_cursor(x, self._inner_mouse_y)
        

class LineInteractor(_BaseInteractor):
    """
    Select an annulus through a 2D plot
    """
    def __init__(self, base, axes, color='black',
                 zorder=5, r=1.0, theta=math.pi/4):
        """
        """
        _BaseInteractor.__init__(self, base, axes, color=color)
        
        self.markers = []
        self.axes = axes
        self.save_theta = theta 
        self.theta= theta
        self.radius = r
        self.scale = 10.0
        # Inner circle
        x1 = self.radius * math.cos(self.theta)
        y1 = self.radius * math.sin(self.theta)
        x2 = -1*self.radius * math.cos(self.theta)
        y2 = -1*self.radius * math.sin(self.theta)
        try:
            # Inner circle marker
            self.inner_marker = self.axes.plot([x1/2.5], [y1/2.5], linestyle='',
                                          marker='s', markersize=10,
                                          color=self.color, alpha=0.6,
                                          pickradius=5, label="pick", 
                                          # Prefer this to other lines
                                          zorder=zorder, 
                                          visible=True)[0]
        except:
            self.inner_marker = self.axes.plot([x1/2.5], [y1/2.5], linestyle='',
                                          marker='s', markersize=10,
                                          color=self.color, alpha=0.6,
                                          label="pick", 
                                          visible=True)[0]
            message  = "\nTHIS PROTOTYPE NEEDS THE LATEST VERSION"
            message += " OF MATPLOTLIB\n Get the SVN version that is at"
            message += " least as recent as June 1, 2007"
        self.line = self.axes.plot([x1, x2], [y1, y2],
                                      linestyle='-', marker='',
                                      color=self.color, visible=True)[0]
        self.npts = 20
        self.has_move = False
        self.connect_markers([self.inner_marker, self.line])
        self.update()

    def set_layer(self, n):
        """
        """
        self.layernum = n
        self.update()
        
    def clear(self):
        """
        """
        self.clear_markers()
        try:
            self.inner_marker.remove()
            self.line.remove()
        except:
            # Old version of matplotlib
            for item in range(len(self.axes.lines)):
                del self.axes.lines[0]
  
    def update(self, theta=None):
        """
        Draw the new roughness on the graph.
        """
       
        if theta != None:
            self.theta = theta
        x1 = self.radius * math.cos(self.theta)
        y1 = self.radius * math.sin(self.theta)
        x2 = -1 * self.radius * math.cos(self.theta)
        y2 = -1 * self.radius * math.sin(self.theta)
        
        self.inner_marker.set(xdata=[x1/2.5], ydata=[y1/2.5])
        self.line.set(xdata=[x1, x2], ydata=[y1, y2])  
    
    def save(self, ev):
        """
        Remember the roughness for this layer and the next so that we
        can restore on Esc.
        """
        self.save_theta= self.theta
        self.base.freeze_axes()

    def moveend(self, ev):
        """
        """
        self.has_move = False
        self.base.moveend(ev)
            
    def restore(self):
        """
        Restore the roughness for this layer.
        """
        self.theta = self.save_theta

    def move(self, x, y, ev):
        """
        Process move to a new position, making sure that the move is allowed.
        """
        self.theta = math.atan2(y, x)
        self.has_move = True
        self.base.base.update()
        
    def set_cursor(self, x, y):
        """
        """
        self.move(x, y, None)
        self.update()
        
    def get_params(self):
        """
        """
        params = {}
        params["radius"] = self.radius
        params["theta"] = self.theta
        return params
    
    def set_params(self, params):
        """
        """
        x = params["radius"] 
        self.set_cursor(x, self._inner_mouse_y)
        