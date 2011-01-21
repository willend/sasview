
################################################################################
#This software was developed by the University of Tennessee as part of the
#Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
#project funded by the US National Science Foundation. 
#
#See the license text in license.txt
#
#copyright 2008, University of Tennessee
################################################################################


import wx
import wx.aui
import os
import sys
import xml

try:
    # Try to find a local config
    import imp
    path = os.getcwd()
    if(os.path.isfile("%s/%s.py" % (path, 'local_config'))) or \
        (os.path.isfile("%s/%s.pyc" % (path, 'local_config'))):
        fObj, path, descr = imp.find_module('local_config', [path])
        config = imp.load_module('local_config', fObj, path, descr)  
    else:
        # Try simply importing local_config
        import local_config as config
except:
    # Didn't find local config, load the default 
    import config
    
import warnings
warnings.simplefilter("ignore")

import logging

from sans.guiframe.events import EVT_STATUS
from sans.guiframe.events import EVT_ADD_MANY_DATA
from sans.guiframe.events import StatusEvent
from sans.guiframe.events import NewPlotEvent


STATE_FILE_EXT = ['.inv', '.fitv', '.prv']

DATA_MANAGER = False
AUTO_PLOT = False
AUTO_SET_DATA = True

class ViewerFrame(wx.Frame):
    """
    Main application frame
    """
    
    def __init__(self, parent, id, title, 
                 window_height=300, window_width=300):
        """
        Initialize the Frame object
        """
        
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition,
                          size=(window_width, window_height))
        # Preferred window size
        self._window_height = window_height
        self._window_width  = window_width
        
        # Logging info
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='sans_app.log',
                    filemode='w')        
        path = os.path.dirname(__file__)
        temp_path = os.path.join(path,'images')
        ico_file = os.path.join(temp_path,'ball.ico')
        if os.path.isfile(ico_file):
            self.SetIcon(wx.Icon(ico_file, wx.BITMAP_TYPE_ICO))
        else:
            temp_path = os.path.join(os.getcwd(),'images')
            ico_file = os.path.join(temp_path,'ball.ico')
            if os.path.isfile(ico_file):
                self.SetIcon(wx.Icon(ico_file, wx.BITMAP_TYPE_ICO))
        
        ## Application manager
        self.app_manager = None
        self._mgr = None
        #data manager
        from data_manager import DataManager
        self.data_manager = DataManager()
        #add current perpsective
        self._current_perspective = None
        #file menu
        self.file_menu = None
        
        ## Find plug-ins
        # Modify this so that we can specify the directory to look into
        self.plugins = []
        #add local plugin
      
        from sans.guiframe.local_perspectives.plotting import plotting
        from sans.guiframe.local_perspectives.data_loader import data_loader
        self.plugins.append(plotting.Plugin())
        self.plugins.append(data_loader.Plugin())
        
        self.plugins += self._find_plugins()
      
        ## List of panels
        self.panels = {}

        ## Next available ID for wx gui events 
        #TODO:  No longer used - remove all calls to this 
        self.next_id = 20000

        # Default locations
        self._default_save_location = os.getcwd()        
        
        # Welcome panel
        self.defaultPanel = None
        #panel on focus
        self.panel_on_focus = None
        # Check for update
        #self._check_update(None)
        # Register the close event so it calls our own method
        wx.EVT_CLOSE(self, self._onClose)
        # Register to status events
        self.Bind(EVT_STATUS, self._on_status_event)
        #Register add extra data on the same panel event on load
        self.Bind(EVT_ADD_MANY_DATA, self.set_panel_on_focus)
        
    def set_panel_on_focus(self, event):
        """
        Store reference to the last panel on focus
        """
        self.panel_on_focus = event.panel
        
    def build_gui(self):
        """
        """
        # Set up the layout
        self._setup_layout()
        
        # Set up the menu
        self._setup_menus()
        #self.Fit()
        #self._check_update(None)
             
    def _setup_layout(self):
        """
        Set up the layout
        """
        # Status bar
        from statusbar import StatusBar
        self.sb = StatusBar(self, wx.ID_ANY)
        self.SetStatusBar(self.sb)
        # Add panel
        self._mgr = wx.aui.AuiManager(self)
        self._mgr.SetDockSizeConstraint(0.5, 0.5) 
        # Load panels
        self._load_panels()
        self._mgr.Update()
        
    def SetStatusText(self, *args, **kwds):
        """
        """
        number = self.sb.get_msg_position()
        wx.Frame.SetStatusText(number=number, *args, **kwds)
        
    def PopStatusText(self, *args, **kwds):
        """
        """
        field = self.sb.get_msg_position()
        wx.Frame.PopStatusText(field=field)
        
    def PushStatusText(self, *args, **kwds):
        """
        """
        field = self.sb.get_msg_position()
        wx.Frame.PushStatusText(self, field=field, string=string)

    def add_perspective(self, plugin):
        """
        Add a perspective if it doesn't already
        exist.
        """
        is_loaded = False
        for item in self.plugins:
            if plugin.__class__ == item.__class__:
                msg = "Plugin %s already loaded" % plugin.__class__.__name__
                logging.info(msg)
                is_loaded = True    
        if not is_loaded:
            self.plugins.append(plugin)
      
    def _find_plugins(self, dir="perspectives"):
        """
        Find available perspective plug-ins
        
        :param dir: directory in which to look for plug-ins
        
        :return: list of plug-ins
        
        """
        import imp
        plugins = []
        # Go through files in panels directory
        try:
            list = os.listdir(dir)
            ## the default panel is the panel is the last plugin added
            for item in list:
                toks = os.path.splitext(os.path.basename(item))
                name = None
                if not toks[0] == '__init__':
                    
                    if toks[1] == '.py' or toks[1] == '':
                        name = toks[0]
                
                    path = [os.path.abspath(dir)]
                    file = None
                    try:
                        if toks[1] == '':
                            mod_path = '.'.join([dir, name])
                            module = __import__(mod_path, globals(),
                                                locals(), [name])
                        else:
                            (file, path, info) = imp.find_module(name, path)
                            module = imp.load_module( name, file, item, info)
                        if hasattr(module, "PLUGIN_ID"):
                            try: 
                                plug = module.Plugin()
                                if plug.set_default_perspective():
                                    self._current_perspective = plug
                                plugins.append(plug)
                                msg = "Found plug-in: %s" % module.PLUGIN_ID
                                logging.info(msg)
                            except:
                                msg = "Error accessing PluginPanel"
                                msg += " in %s\n  %s" % (name, sys.exc_value)
                                config.printEVT(msg)
                    except:
                        #print sys.exc_value
                        msg = "ViewerFrame._find_plugins: %s" % sys.exc_value
                        logging.error(msg)
                    finally:
                        if not file == None:
                            file.close()
        except:
            # Should raise and catch at a higher level and 
            # display error on status bar
            pass   
        return plugins
    
    def set_welcome_panel(self, panel_class):
        """
        Sets the default panel as the given welcome panel 
        
        :param panel_class: class of the welcome panel to be instantiated
        
        """
        self.defaultPanel = panel_class(self, -1, style=wx.RAISED_BORDER)
        
    def _load_panels(self):
        """
        Load all panels in the panels directory
        """
        
        # Look for plug-in panels
        panels = []    
        for item in self.plugins:
            if hasattr(item, "get_panels"):
                ps = item.get_panels(self)
                panels.extend(ps)

        # Show a default panel with some help information
        # It also sets the size of the application windows
        #TODO: Use this for slpash screen
        if self.defaultPanel is None:
            self.defaultPanel = DefaultPanel(self, -1, style=wx.RAISED_BORDER)
            
        self.panels["default"] = self.defaultPanel
        
        self._mgr.AddPane(self.defaultPanel, wx.aui.AuiPaneInfo().
                              Name("default").
                              CenterPane().
                              # This is where we set the size of
                              # the application window
                              BestSize(wx.Size(self._window_width, 
                                               self._window_height)).
                              #MinSize(wx.Size(self._window_width, 
                              #self._window_height)).
                              Show())
     
        # Add the panels to the AUI manager
        for panel_class in panels:
            p = panel_class
            id = wx.NewId()
            
            # Check whether we need to put this panel
            # in the center pane
            if hasattr(p, "CENTER_PANE") and p.CENTER_PANE:
                if p.CENTER_PANE:
                    self.panels[str(id)] = p
                    self._mgr.AddPane(p, wx.aui.AuiPaneInfo().
                                          Name(p.window_name).Caption(p.window_caption).
                                          CenterPane().
                                          #BestSize(wx.Size(550,600)).
                                          #MinSize(wx.Size(500,500)).
                                          Hide())
            else:
                self.panels[str(id)] = p
                self._mgr.AddPane(p, wx.aui.AuiPaneInfo().
                                  Name(p.window_name).Caption(p.window_caption).
                                  Right().
                                  Dock().
                                  TopDockable().
                                  BottomDockable().
                                  LeftDockable().
                                  RightDockable().
                                  MinimizeButton().
                                  Hide())
                                  #BestSize(wx.Size(550,600)))
                                  #MinSize(wx.Size(500,500)))                 
      
    def get_context_menu(self, graph=None):
        """
        Get the context menu items made available 
        by the different plug-ins. 
        This function is used by the plotting module
        """
        menu_list = []
        for item in self.plugins:
            if hasattr(item, "get_context_menu"):
                menu_list.extend(item.get_context_menu(graph))
        return menu_list
        
    def popup_panel(self, p):
        """
        Add a panel object to the AUI manager
        
        :param p: panel object to add to the AUI manager
        
        :return: ID of the event associated with the new panel [int]
        
        """
        ID = wx.NewId()
        self.panels[str(ID)] = p
        
        count = 0
        for item in self.panels:
            if self.panels[item].window_name.startswith(p.window_name): 
                count += 1
        windowname = p.window_name
        caption = p.window_caption
        if count > 0:
            windowname += str(count+1)
            caption += (' '+str(count))
        p.window_name = windowname
        p.window_caption = caption
            
        self._mgr.AddPane(p, wx.aui.AuiPaneInfo().
                          Name(windowname).Caption(caption).
                          Floatable().
                          #Float().
                          Right().
                          Dock().
                          TopDockable().
                          BottomDockable().
                          LeftDockable().
                          RightDockable().
                          MinimizeButton().
                          #Hide().
                          #Show().
                          Resizable(True).
                          # Use a large best size to make sure the AUI manager
                          # takes all the available space
                          BestSize(wx.Size(400,400)))
        pane = self._mgr.GetPane(windowname)
        self._mgr.MaximizePane(pane)
        self._mgr.RestoreMaximizedPane()
        # Register for showing/hiding the panel
        wx.EVT_MENU(self, ID, self._on_view)
        
        self._mgr.Update()
        return ID
        
    def _populate_file_menu(self):
        """
        Insert menu item under file menu
        """
        for plugin in self.plugins:
            if len(plugin.populate_file_menu()) > 0:
                for item in plugin.populate_file_menu():
                    id = wx.NewId()
                    m_name, m_hint, m_handler = item
                    self.filemenu.Append(id, m_name, m_hint)
                    wx.EVT_MENU(self, id, m_handler)
                self.filemenu.AppendSeparator()
                
    def _setup_menus(self):
        """
        Set up the application menus
        """
        # Menu
        self._menubar = wx.MenuBar()
        # File menu
        self.filemenu = wx.Menu()
        
        # some menu of plugin to be seen under file menu
        self._populate_file_menu()
        id = wx.NewId()
        self.filemenu.Append(id, '&Save state into File',
                             'Save project as a SansView (svs) file')
        wx.EVT_MENU(self, id, self._on_save)
        #self.filemenu.AppendSeparator()
        
        id = wx.NewId()
        self.filemenu.Append(id, '&Quit', 'Exit') 
        wx.EVT_MENU(self, id, self.Close)
        
        # Add sub menus
        self._menubar.Append(self.filemenu, '&File')
        
        # Window menu
        # Attach a menu item for each panel in our
        # panel list that also appears in a plug-in.
        
        # Only add the panel menu if there is only one perspective and
        # it has more than two panels.
        # Note: the first plug-in is always the plotting plug-in. 
        #The first application
        # plug-in is always the second one in the list.
        if len(self.plugins) == 2:
            plug = self.plugins[1]
            pers = plug.get_perspective()
       
            if len(pers) > 1:
                viewmenu = wx.Menu()
                for item in self.panels:
                    if item == 'default':
                        continue
                    panel = self.panels[item]
                    if panel.window_name in pers:
                        viewmenu.Append(int(item), panel.window_caption,
                                        "Show %s window" % panel.window_caption)
                        wx.EVT_MENU(self, int(item), self._on_view)
                self._menubar.Append(viewmenu, '&Window')

        # Perspective
        # Attach a menu item for each defined perspective.
        # Only add the perspective menu if there are more than one perspectives
        n_perspectives = 0
        for plug in self.plugins:
            if len(plug.get_perspective()) > 0:
                n_perspectives += 1
        
        if n_perspectives > 1:
            p_menu = wx.Menu()
            for plug in self.plugins:
                if len(plug.get_perspective()) > 0:
                    id = wx.NewId()
                    p_menu.Append(id, plug.sub_menu,
                                  "Switch to %s perspective" % plug.sub_menu)
                    wx.EVT_MENU(self, id, plug.on_perspective)
            self._menubar.Append(p_menu, '&Perspective')
 
        # Tools menu
        # Go through plug-ins and find tools to populate the tools menu
        toolsmenu = None
        for item in self.plugins:
            if hasattr(item, "get_tools"):
                for tool in item.get_tools():
                    # Only create a menu if we have at least one tool
                    if toolsmenu is None:
                        toolsmenu = wx.Menu()
                    id = wx.NewId()
                    toolsmenu.Append(id, tool[0], tool[1])
                    wx.EVT_MENU(self, id, tool[2])
        if toolsmenu is not None:
            self._menubar.Append(toolsmenu, '&Tools')
 
        # Help menu
        helpmenu = wx.Menu()
        # add the welcome panel menu item
        if self.defaultPanel is not None:
            id = wx.NewId()
            helpmenu.Append(id, '&Welcome', '')
            helpmenu.AppendSeparator()
            wx.EVT_MENU(self, id, self.show_welcome_panel)
        # Look for help item in plug-ins 
        for item in self.plugins:
            if hasattr(item, "help"):
                id = wx.NewId()
                helpmenu.Append(id,'&%s help' % item.sub_menu, '')
                wx.EVT_MENU(self, id, item.help)
        if config._do_aboutbox:
            id = wx.NewId()
            helpmenu.Append(id,'&About', 'Software information')
            wx.EVT_MENU(self, id, self._onAbout)
            
        # Checking for updates needs major refactoring to work with py2exe
        # We need to make sure it doesn't hang the application if the server
        # is not up. We also need to make sure there's a proper executable to
        # run if we spawn a new background process.
        #id = wx.NewId()
        #helpmenu.Append(id,'&Check for update', 
        #'Check for the latest version of %s' % config.__appname__)
        #wx.EVT_MENU(self, id, self._check_update)
        
        # Look for plug-in menus
        # Add available plug-in sub-menus. 
        for item in self.plugins:
            if hasattr(item, "populate_menu"):
                for (self.next_id, menu, name) in \
                    item.populate_menu(self.next_id, self):
                    self._menubar.Append(menu, name)
                   
        self._menubar.Append(helpmenu, '&Help')
        self.SetMenuBar(self._menubar)
    
    def _on_status_event(self, evt):
        """
        Display status message
        """
        self.sb.set_status(event=evt)
       
    def _on_view(self, evt):
        """
        A panel was selected to be shown. If it's not already
        shown, display it.
        
        :param evt: menu event
        
        """
        self.show_panel(evt.GetId())
        
    def on_close_welcome_panel(self):
        """
        Close the welcome panel
        """
        if self.defaultPanel is None:
            return 
        self._mgr.GetPane(self.panels["default"].window_name).Hide()
        self._mgr.Update()
        # set a default perspective
        self.set_default_perspective()
        
    def show_welcome_panel(self, event):
        """    
        Display the welcome panel
        """
        if self.defaultPanel is None:
            return 
        for id in self.panels.keys():
            if self._mgr.GetPane(self.panels[id].window_name).IsShown():
                self._mgr.GetPane(self.panels[id].window_name).Hide()
        # Show default panel
        if not self._mgr.GetPane(self.panels["default"].window_name).IsShown():
            self._mgr.GetPane(self.panels["default"].window_name).Show()
        
        self._mgr.Update()
        
    def show_panel(self, uid):
        """
        Shows the panel with the given id
        
        :param uid: unique ID number of the panel to show
        
        """
        ID = str(uid)
        config.printEVT("show_panel: %s" % ID)
        if ID in self.panels.keys():
            if not self._mgr.GetPane(self.panels[ID].window_name).IsShown():
                self._mgr.GetPane(self.panels[ID].window_name).Show()
                # Hide default panel
                self._mgr.GetPane(self.panels["default"].window_name).Hide()
            self._mgr.Update()
   
    def _on_open(self, event):
        """
        """
        path = self.choose_file()
        if path is None:
            return
        
        from data_loader import plot_data
        from sans.perspectives import invariant
        if path and os.path.isfile(path):
            basename  = os.path.basename(path)
            if  basename.endswith('.svs'):
                #remove panels for new states
                for item in self.panels:
                    try:
                        self.panels[item].clear_panel()
                    except:
                        pass
                #reset states and plot data 
                for item in STATE_FILE_EXT:
                    exec "plot_data(self, path,'%s')" % str(item)
            else:
                plot_data(self, path)
        if self.defaultPanel is not None and \
            self._mgr.GetPane(self.panels["default"].window_name).IsShown():
            self.on_close_welcome_panel()
            
    def _on_save(self, event):
        """
        Save state into a file
        """
        # Ask the user the location of the file to write to.
        
        ## Default file location for save
        self._default_save_location = os.getcwd()
        path = None
        dlg = wx.FileDialog(self, "Choose a file",
                            self._default_save_location, "", "*.svs", wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self._default_save_location = os.path.dirname(path)
        else:
            return None
        dlg.Destroy()
        if path is None:
            return
        # default cansas xml doc
        doc = None
        for item in self.panels:
            try:
                if self.panels[item].window_name == 'Invariant':
                    data = self.panels[item]._data
                    if data != None:
                        state = self.panels[item].state
                        manager = self.panels[item]._manager
                        new_doc = manager.state_reader.write_toXML(data, state)
                        if hasattr(doc, "firstChild"):
                            child = new_doc.firstChild.firstChild
                            doc.firstChild.appendChild(child)  
                        else:
                            doc = new_doc 
                elif self.panels[item].window_name == 'pr_control':
                    data = self.panels[item].manager.current_plottable
                    if data != None:
                        state = self.panels[item].get_state()
                        manager = self.panels[item].manager
                        new_doc = manager.state_reader.write_toXML(data, state)
                        if hasattr(doc, "firstChild"):
                            child = new_doc.firstChild.firstChild
                            doc.firstChild.appendChild(child)  
                        else:
                            doc = new_doc 
                elif self.panels[item].window_name == 'Fit panel':
                    for index in range(self.panels[item].GetPageCount()):
                        selected_page = self.panels[item].GetPage(index) 
                        if hasattr(selected_page,"get_data"):
                            data = selected_page.get_data()
                            state = selected_page.state
                            reader = selected_page.manager.state_reader
                            new_doc = reader.write_toXML(data, state)
                            if doc != None and hasattr(doc, "firstChild"):
                                child = new_doc.firstChild.firstChild
                                doc.firstChild.appendChild(child)
                            else:
                                doc = new_doc
            except: 
                pass
        # Write the XML document
        if doc != None:
            fd = open(path, 'w')
            fd.write(doc.toprettyxml())
            fd.close()
        else:
            #print "Nothing to save..."
            raise RuntimeError, "%s is not a SansView (.svs) file..." % path

    def _onClose(self, event):
        """
        Store info to retrieve in xml before closing the application
        """
        wx.Exit()
        sys.exit()
                 
    def quit_guiframe(self):
        """
        Pop up message to make sure the user wants to quit the application
        """
        message = "Do you really want to quit \n"
        message += "this application?"
        dial = wx.MessageDialog(self, message, 'Question',
                           wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            return True
        else:
            return False    
        
    def Close(self, event=None):
        """
        Quit the application
        """
        flag = self.quit_guiframe()
        if flag:
            wx.Frame.Close(self)
            wx.Exit()
            sys.exit()

    def _check_update(self, event=None): 
        """
        Check with the deployment server whether a new version
        of the application is available.
        A thread is started for the connecting with the server. The thread calls
        a call-back method when the current version number has been obtained.
        """
        if hasattr(config, "__update_URL__"):
            import version
            checker = version.VersionThread(config.__update_URL__,
                                            self._process_version,
                                            baggage=event==None)
            checker.start()  
    
    def _process_version(self, version, standalone=True):
        """
        Call-back method for the process of checking for updates.
        This methods is called by a VersionThread object once the current
        version number has been obtained. If the check is being done in the
        background, the user will not be notified unless there's an update.
        
        :param version: version string
        :param standalone: True of the update is being checked in 
           the background, False otherwise.
           
        """
        try:
            if cmp(version, config.__version__) > 0:
                msg = "Version %s is available! See the Help "
                msg += "menu to download it." % version
                self.SetStatusText(msg)
                if not standalone:
                    import webbrowser
                    webbrowser.open(config.__download_page__)
            else:
                if not standalone:
                    msg = "You have the latest version"
                    msg += " of %s" % config.__appname__
                    self.SetStatusText(msg)
        except:
            msg = "guiframe: could not get latest application"
            msg += " version number\n  %s" % sys.exc_value
            logging.error(msg)
            if not standalone:
                msg = "Could not connect to the application server."
                msg += " Please try again later."
                self.SetStatusText(msg)
                    
    def _onAbout(self, evt):
        """
        Pop up the about dialog
        
        :param evt: menu event
        
        """
        if config._do_aboutbox:
            import aboutbox 
            dialog = aboutbox.DialogAbout(None, -1, "")
            dialog.ShowModal()            
            
    def set_manager(self, manager):
        """
        Sets the application manager for this frame
        
        :param manager: frame manager
        """
        self.app_manager = manager
        
    def post_init(self):
        """
        This initialization method is called after the GUI 
        has been created and all plug-ins loaded. It calls
        the post_init() method of each plug-in (if it exists)
        so that final initialization can be done.
        """
        for item in self.plugins:
            if hasattr(item, "post_init"):
                item.post_init()
        
    def set_default_perspective(self):
        """
        Choose among the plugin the first plug-in that has 
        "set_default_perspective" method and its return value is True will be
        as a default perspective when the welcome page is closed
        """
        for item in self.plugins:
            if hasattr(item, "set_default_perspective"):
                if item.set_default_perspective():
                    self._current_perspective = item
                    item.on_perspective(event=None)
                    return 
        
    def set_perspective(self, panels):
        """
        Sets the perspective of the GUI.
        Opens all the panels in the list, and closes
        all the others.
        
        :param panels: list of panels
        """
       
        for item in self.panels:
            # Check whether this is a sticky panel
            if hasattr(self.panels[item], "ALWAYS_ON"):
                if self.panels[item].ALWAYS_ON:
                    continue 
            if self.panels[item].window_name in panels:
                if not self._mgr.GetPane(self.panels[item].window_name).IsShown():
                    self._mgr.GetPane(self.panels[item].window_name).Show()
            else:
                if self._mgr.GetPane(self.panels[item].window_name).IsShown():
                    self._mgr.GetPane(self.panels[item].window_name).Hide()
        self._mgr.Update()
        
    def choose_file(self, path=None):
        """ 
        Functionality that belongs elsewhere
        Should add a hook to specify the preferred file type/extension.
        """
        #TODO: clean this up
        from .data_loader import choose_data_file
        # Choose a file path
        if path == None:
            path = choose_data_file(self, self._default_save_location)
        if not path == None:
            try:
                self._default_save_location = os.path.dirname(path)
            except:
                pass
        return path
    
    def add_data(self, data_list):
        """
        receive a list of data . store them its data manager if possible
        determine if data was be plot of send to data perspectives
        """
        self.data_manager.add_data(data_list)
        if AUTO_SET_DATA:
            if self._current_perspective is not None:
                try:
                    self._current_perspective.set_data(data_list)
                except:
                    msg = str(sys.exc_value)
                    wx.PostEvent(self, StatusEvent(status=msg,
                                              info="error"))
            else:
                msg = "Guiframe does not have a current perspective"
                logging.info(msg)
        if DATA_MANAGER:
            print "will show data panel"
        if AUTO_PLOT:
            self.plot_data(data_list)
            
    def plot_data(self, data_list):
        """
        send a list of data to plot
        """
        for new_plot in data_list:
            wx.PostEvent(self, NewPlotEvent(plot=new_plot,
                                                  title=str(new_plot.title)))
            
    def set_current_perspective(self, perspective):
        """
        set the current active perspective 
        """
        self._current_perspective = perspective

class DefaultPanel(wx.Panel):
    """
    Defines the API for a panels to work with
    the GUI manager
    """
    ## Internal nickname for the window, used by the AUI manager
    window_name = "default"
    ## Name to appear on the window title bar
    window_caption = "Welcome panel"
    ## Flag to tell the AUI manager to put this panel in the center pane
    CENTER_PANE = True

  
# Toy application to test this Frame
class ViewApp(wx.App):
    """
    """
    def OnInit(self):
        """
        """
        self.frame = ViewerFrame(None, -1, config.__appname__)    
        self.frame.Show(True)

        if hasattr(self.frame, 'special'):
            self.frame.special.SetCurrent()
        self.SetTopWindow(self.frame)
        return True
    
    def set_manager(self, manager):
        """
        Sets a reference to the application manager
        of the GUI manager (Frame) 
        """
        self.frame.set_manager(manager)
        
    def build_gui(self):
        """
        Build the GUI
        """
        self.frame.build_gui()
        self.frame.post_init()
        
    def set_welcome_panel(self, panel_class):
        """
        Set the welcome panel
        
        :param panel_class: class of the welcome panel to be instantiated
        
        """
        self.frame.set_welcome_panel(panel_class)
        
    def add_perspective(self, perspective):
        """
        Manually add a perspective to the application GUI
        """
        self.frame.add_perspective(perspective)
        

if __name__ == "__main__": 
    app = ViewApp(0)
    app.MainLoop()

             