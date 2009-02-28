import os, sys,numpy
import wx
from dataFitting import Data1D, Theory1D
from danse.common.plottools.plottables import Data2D

from DataLoader.loader import Loader

def choose_data_file(parent, location=None):
    path = None
    if location==None:
        location = os.getcwd()
    
    l = Loader()
    cards = l.get_wildcards()
    wlist = '|'.join(cards)
    
    dlg = wx.FileDialog(parent, "Choose a file", location, "", wlist, wx.OPEN)
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
        mypath = os.path.basename(path)
    dlg.Destroy()
    
    return path


def load_ascii_1D(path):
    """
        Load a 1D ascii file, with errors
    """
    if path and os.path.isfile(path):
    
        file_x = numpy.zeros(0)
        file_y = numpy.zeros(0)
        file_dy = numpy.zeros(0)
        
        input_f = open(path,'r')
        buff = input_f.read()
        lines = buff.split('\n')
        
        has_dy = False
        
        for line in lines:
            try:
                toks = line.split()
                x = float(toks[0])
                y = float(toks[1])
                if len(toks)==3:
                    has_dy = True
                    err = float(toks[2])
                else:
                    err = 0.0
                file_x  = numpy.append(file_x, x)
                file_y  = numpy.append(file_y, y)
                file_dy = numpy.append(file_dy, err)
            except:
                print "READ ERROR", line
    
        if has_dy==False:
            file_dy = None
            
        return file_x, file_y, file_dy
    return None, None, None

def plot_data(parent, path):
    """
        Use the DataLoader loader to created data to plot.
        @param path: the path of the data to load
    """
    from sans.guicomm.events import NewPlotEvent, StatusEvent
    from DataLoader.loader import  Loader
    
    #Instantiate a loader 
    L = Loader()
    
    #Recieves data 
    try:
        output=L.load(path)
        
    except:
        wx.PostEvent(parent, StatusEvent(status="Problem loading file: %s" % sys.exc_value))
        return
    filename = os.path.basename(path)
    
    if not  output.__class__.__name__=="list":
        try:
            dxl=output.dxl
            dxw=output.dxw
        except:
            dxl=None
            dxw=None
        if hasattr(output,'data'):
            temp = output.err_data
            temp[temp==0]=1

            wx.PostEvent(parent, StatusEvent(status="Loading 2D error bars of value 1 \
            were added to : %s"% output.filename))
            new_plot = Data2D(image=output.data,err_image=temp,
                              xmin=output.xmin,xmax=output.xmax,
                              ymin=output.ymin,ymax=output.ymax)
            new_plot.x_bins=output.x_bins
            new_plot.y_bins=output.y_bins
        else:
           
            if output.dy ==None :
                new_plot = Theory1D(output.x,output.y, dxl, dxw)
            elif len(output.dy[output.dy==0])==len(output.dy):
                output.dy[output.dy==0]=1 
                wx.PostEvent(parent, StatusEvent(status="Loading 1D error bars of value 1 \
                    were added to : %s"%output.filename))
                new_plot = Theory1D(output.x,output.y,output.dy, dxl, dxw)
            else:
                new_plot = Data1D(x=output.x,y=output.y,dx=output.dx,dy=output.dy, dxl=dxl, dxw=dxw)
        if output.filename==None:
            output.filename=str(filename)
        new_plot.source=output.source
        new_plot.name = output.filename
        new_plot.interactive = True
        new_plot.id = True
        new_plot.info= output
        if hasattr(output, "dxl"):
            new_plot.dxl = output.dxl
        if hasattr(output, "dxw"):
            new_plot.dxw = output.dxw
        new_plot.detector =output.detector
        
        # If the data file does not tell us what the axes are, just assume...
        new_plot.xaxis(output._xaxis,output._xunit)
        new_plot.yaxis(output._yaxis,output._yunit)
        new_plot.group_id = output.filename
        new_plot.id = output.filename
        try:
            title=output.filename
        except:
            title= filename
        
        wx.PostEvent(parent, NewPlotEvent(plot=new_plot, title=str(title)))
    else:
        i=1
        for item in output:
            
            try:
                dxl=item.dxl
                dxw=item.dxw
            except:
                dxl=None
                dxw=None
            if item.dy ==None:
                new_plot = Theory1D(item.x,item.y,dxl,dxw)
            else:
                new_plot = Data1D(x=item.x,y=item.y,dx=item.dx,dy=item.dy,dxl=dxl,dxw=dxw)
           
            new_plot.source=item.source
            new_plot.name = str(item.run[0])
            new_plot.interactive = True
            new_plot.detector =item.detector
            # If the data file does not tell us what the axes are, just assume...
            new_plot.xaxis(item._xaxis,item._xunit)
            new_plot.yaxis(item._yaxis,item._yunit)
            new_plot.group_id = str(item.run[0])
            new_plot.id = str(item.run[0])
            new_plot.info= item
            
            if hasattr(item,"title"):
                title= item.title
            else:
                title= str(item.run[0])
            wx.PostEvent(parent, NewPlotEvent(plot=new_plot, title=str(title)))
            i+=1
           
            