
import os
import sys
import numpy
import wx
import re

from dataFitting import Data1D
from dataFitting import Data2D
from DataLoader.loader import Loader
from load_thread import DataReader
from sans.guicomm.events import FitStateUpdateEvent
from sans.guicomm.events import InvStateUpdateEvent
from sans.guicomm.events import StatusEvent
from sans.guicomm.events import NewPlotEvent

SVS_FILE_EXT = ['.svs', '.inv', '.prv', '.fitv']

def enable_add_data(existing_panel, new_plot):
    """
    Enable append data on a plot panel
    """
    is_theory = len(existing_panel.plots) <= 1 and \
        existing_panel.plots.values()[0].__class__.__name__ == "Theory1D"
        
    is_data2d = hasattr(new_plot, 'data')
    is_data1d = existing_panel.__class__.__name__ == "ModelPanel1D"\
        and existing_panel.group_id is not None
    has_meta_data = hasattr(new_plot, 'meta_data')
    
    #disable_add_data if the data is being recovered from  a saved state file.
    is_state_data = False
    if has_meta_data:
        if 'invstate' in new_plot.meta_data: is_state_data = True
        if  'prstate' in new_plot.meta_data: is_state_data = True
        if  'fitstate' in new_plot.meta_data: is_state_data = True

    return is_data1d and not is_data2d and not is_theory and not is_state_data

def parse_name(name, expression):
    """
    remove "_" in front of a name
    """
    if re.match(expression, name) is not None:
        word = re.split(expression, name, 1)
        for item in word:           
            if item.lstrip().rstrip() != '':
                return item
    else:
        return name
    
def choose_data_file(parent, location=None):
    """
    """
    path = None
    if location == None:
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

def open_dialog_append_data(panel_name, data_name):
    """
    Pop up an error message.
    
    :param panel_name: the name of the current panel
    :param data_name: the name of the current data
    
    """
    message = " Do you want to append %s data\n in " % (str(data_name))
    message += " %s panel?\n\n" % (str(panel_name))
    dial = wx.MessageDialog(None, message, 'Question',
                       wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
    if dial.ShowModal() == wx.ID_YES:
        return True
    else:
        return False
   
# where is this method used?
def load_ascii_1D(path):
    """
    Load a 1D ascii file, with errors
    """
    if path and os.path.isfile(path):
    
        file_x = numpy.zeros(0)
        file_y = numpy.zeros(0)
        file_dy = numpy.zeros(0)
        file_dx = numpy.zeros(0)
        
        input_f = open(path,'r')
        buff = input_f.read()
        lines = buff.split('\n')
        
        has_dy = False
        has_dx = False
        
        for line in lines:
            try:
                toks = line.split()
                x = float(toks[0])
                y = float(toks[1])
                if len(toks) == 3:
                    has_dy = True
                    errdy = float(toks[2])
                else:
                    errdy = 0.0
                if len(toks) == 4:
                    has_dx = True
                    errdx = float(toks[3])
                else:
                    errdx = 0.0
                file_x  = numpy.append(file_x, x)
                file_y  = numpy.append(file_y, y)
                file_dy = numpy.append(file_dy, dyerr)
                file_dx = numpy.append(file_dx, dxerr)
            except:
                print "READ ERROR", line
    
        if has_dy == False:
            file_dy = None
        if has_dx == False:
            file_dx = None
            
        return file_x, file_y, file_dy, file_dx
    return None, None, None, None

def load_error(error=None):
    """
    Pop up an error message.
    
    :param error: details error message to be displayed
    """
    message = "The data file you selected could not be loaded.\n"
    message += "Make sure the content of your file is properly formatted.\n\n"
    
    if error is not None:
        message += "When contacting the DANSE team, mention the"
        message += " following:\n%s" % str(error)
    
    dial = wx.MessageDialog(None, message, 'Error Loading File',
                            wx.OK | wx.ICON_EXCLAMATION)
    dial.ShowModal()    

def on_load_error(parent):
    """
    """
    wx.PostEvent(parent, StatusEvent(status="Load cancel..", info="warning",
                                                type="stop"))
    
def plot_data(parent, path, format=None):
    """
    Use the DataLoader loader to created data to plot.
    
    :param path: the path of the data to load
    : param format: file format (as file extension)
    """
    #from sans.guicomm.events import NewPlotEvent, StatusEvent
    #from DataLoader.loader import  Loader
    # Instantiate a loader 
    L = Loader()
    
    # Load data 
    try:
        output = L.load(path, format)
    except:
        load_error(sys.exc_value)
        return
    basename  = os.path.basename(path)
    # Notify user if the loader completed the load but no data came out
    if output == None:
        if  not basename.endswith('.svs'):
            load_error("The data file appears to be empty.")
        return
  
    root, extension = os.path.splitext(basename)
    ext =  extension.lower()
    filename = os.path.basename(path)
    if not  output.__class__.__name__ == "list":
        ## Creating a Data2D with output
        if hasattr(output,'data'):
            msg = "Loading 2D data: %s" % output.filename
            wx.PostEvent(parent, StatusEvent(status=msg, info="info",
                                             type="stop"))
            new_plot = Data2D(image=None, err_image=None)
      
        else:
            msg = "Loading 1D data: %s" % output.filename
            wx.PostEvent(parent, StatusEvent(status=msg, info="info",
                                             type="stop"))
            new_plot = Data1D(x=[], y=[], dx=None, dy=None)
            
        new_plot.copy_from_datainfo(output) 
        output.clone_without_data(clone=new_plot)      
      
        ## data 's name
        if output.filename is None or output.filename == "":
            output.filename = str(filename)
        ## name of the data allow to differentiate data when plotted
        name = parse_name(name=output.filename, expression="_")
       
        new_plot.name = name
        ## allow to highlight data when plotted
        new_plot.interactive = True
        ## when 2 data have the same id override the 1 st plotted
        new_plot.id = name
        ##group_id specify on which panel to plot this data
        new_plot.group_id = name
        new_plot.is_data = True
        ##post data to plot
        title = output.filename
        if hasattr(new_plot,"title"):
            title = str(new_plot.title.lstrip().rstrip())
            if title == "":
                title = str(name)
        else:
            title = str(name)
        if hasattr(parent, "panel_on_focus") and \
            not(parent.panel_on_focus is None):
            existing_panel  = parent.panel_on_focus
            panel_name = existing_panel.window_caption
            data_name = new_plot.name
            if enable_add_data(existing_panel, new_plot):
                if open_dialog_append_data(panel_name, data_name):
                    #add this plot the an existing panel
                    new_plot.group_id = existing_panel.group_id
        # plot data
        wx.PostEvent(parent, NewPlotEvent(plot=new_plot, title=title))
        if ext in SVS_FILE_EXT:
            # set state and plot computation if exists
            wx.PostEvent(parent, InvStateUpdateEvent())
            wx.PostEvent(parent, FitStateUpdateEvent())
    ## the output of the loader is a list , some xml files contain 
    #more than one data
    else:
        i = 0
        for item in output: 
            try:
                ## Creating a Data2D with output
                if hasattr(item, 'data'):
                    msg = "Loading 2D data: %s" % item.filename
                    wx.PostEvent(parent, StatusEvent(status=msg, info="info",
                                                     type="stop"))
                    new_plot = Data2D(image=None, err_image=None)
              
                else:
                    msg = "Loading 1D data: %s" % str(item.run[0])
                    wx.PostEvent(parent, StatusEvent(status=msg, info="info",
                                                     type="stop"))
                    try:
                        dx = item.dx
                        dxl = item.dxl
                        dxw = item.dxw
                    except:
                        dx = None
                        dxl = None
                        dxw = None
        
                    new_plot = Data1D(x=item.x, y=item.y, dx=dx, dy=item.dy)
                    if dxl != None:
                        new_plot.dxl = dxl
                    if dxl != None:
                        new_plot.dxw = dxw
                
                new_plot.copy_from_datainfo(item)    
                item.clone_without_data(clone=new_plot)    
                # find original data file name without timestemp
                name = parse_name(name=str(item.run[0]), expression="_")
                max_char = name.find("[")
                if max_char < 0:
                    max_char = len(name)
                original_name = name[0:max_char]
                #TODO: this is a very annoying feature. We should make this
                # an option. Excel doesn't do this. Why should we?
                # What is the requirement for this feature, and are the
                # counter arguments stronger? Is this feature developed
                # to please at least 80% of the users or a special few?                    
                new_plot.name = name
                new_plot.interactive = True
                new_plot.group_id = original_name
                new_plot.id = name
                new_plot.is_data = True
                title = item.filename
                
                if hasattr(item, "title"):
                    title = item.title.lstrip().rstrip()
                    if title == "":
                        title = str(name)
                else:
                    title = name
                if hasattr(parent, "panel_on_focus") and \
                    not(parent.panel_on_focus is None):
                    existing_panel  = parent.panel_on_focus
                    panel_name = existing_panel.window_caption
                    data_name = new_plot.name
                    if enable_add_data(existing_panel, new_plot):
                        if open_dialog_append_data(panel_name, data_name):
                            #add this plot the an existing panel
                            new_plot.group_id = existing_panel.group_id
                # plot data
                wx.PostEvent(parent, NewPlotEvent(plot=new_plot,
                                                  title=str(title)))
                if ext in SVS_FILE_EXT:
                    # set state and plot computation if exists
                    wx.PostEvent(parent, InvStateUpdateEvent())
                    wx.PostEvent(parent, FitStateUpdateEvent())
            except:
                raise
