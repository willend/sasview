

import sys
import wx
import wx.lib.newevent
import numpy
import copy
import math
import time
from sans.models.dispersion_models import ArrayDispersion, GaussianDispersion
from sans.dataloader.data_info import Data1D
from sans.guiframe.events import StatusEvent 
from sans.guiframe.events import NewPlotEvent  
from sans.guiframe.utils import format_number,check_float

(Chi2UpdateEvent, EVT_CHI2_UPDATE)   = wx.lib.newevent.NewEvent()
_BOX_WIDTH = 76
_DATA_BOX_WIDTH = 300
SMEAR_SIZE_L = 0.00
SMEAR_SIZE_H = 0.00

import basepage
from basepage import BasicPage
from basepage import PageInfoEvent
from sans.models.qsmearing import smear_selection


class FitPage(BasicPage):
    """
    FitPanel class contains fields allowing to display results when
    fitting  a model and one data
    
    :note: For Fit to be performed the user should check at least one parameter
        on fit Panel window.
    """
    
    def __init__(self,parent, color='rand'):
        """ 
        Initialization of the Panel
        """
        BasicPage.__init__(self, parent, color=color)
        
        ## draw sizer
        self._fill_data_sizer()
        self.is_2D = None
        self.fit_started = False
        # get smear info from data
        self._get_smear_info()
        self._fill_model_sizer( self.sizer1)
        self._get_defult_custom_smear()
        self._fill_range_sizer() 
        self._set_smear(self.data)
        self.Bind(EVT_CHI2_UPDATE, self.on_complete_chisqr)
        # bind key event
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self._set_bookmark_flag(False)
        self._set_save_flag(False)
        self._set_preview_flag(False)
        self._set_copy_flag(False)
        self._set_paste_flag(False)
        self.btFit.SetFocus()
        self.fill_data_combobox(data_list=self.data_list)
    
    
    def _fill_data_sizer(self):
        """
        fill sizer 0 with data info
        """
        box_description= wx.StaticBox(self, -1, 'I(q) Data Source')
        boxsizer1 = wx.StaticBoxSizer(box_description, wx.VERTICAL)
        #----------------------------------------------------------
        sizer_data = wx.BoxSizer(wx.HORIZONTAL)
        self.dataSource = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        wx.EVT_COMBOBOX(self.dataSource, -1, self.on_select_data)
        self.dataSource.SetMinSize((_DATA_BOX_WIDTH, -1))
        sizer_data.Add(wx.StaticText(self, -1, 'Name : '))
        sizer_data.Add(self.dataSource)
        sizer_data.Add( (0,5) )
        boxsizer1.Add(sizer_data,0, wx.ALL, 10)
        self.sizer0.Add(boxsizer1,0, wx.EXPAND | wx.ALL, 10)
        self.sizer0.Layout()
        
    def enable_datasource(self):
        """
        Enable or disable data source control depending on existing data
        """
        if not self.data_list:
            self.dataSource.Disable()
        else:
            self.dataSource.Enable()
            
    def fill_data_combobox(self, data_list):
        """
        Get a list of data and fill the corresponding combobox
        """
        self.dataSource.Clear()
        self.data_list = data_list
        self.enable_datasource()
        if data_list:
            qmin, qmax, npts = self.compute_data_range(data_list[0])
            self.qmin_data_set, self.qmax_data_set = qmin, qmax
            self.npts_data_set = npts
        for data in self.data_list:
            if data is not None:
                self.compute_data_set_range(data)
                self.dataSource.Append(str(data.name), clientData=data)
                
        print "fill_data_combox", self.qmin_data_set, self.qmax_data_set
        self.dataSource.SetSelection(0)
        self.on_select_data(event=None)
                
    def on_select_data(self, event=None):
        """
        """
        if event is None and self.dataSource.GetCount() > 0:
            data = self.dataSource.GetClientData(0)
            self.set_data(data)
        elif self.dataSource.GetCount() > 0:
            pos = self.dataSource.GetSelection()
            data = self.dataSource.GetClientData(pos)
            self.set_data(data)
    
    
        
    def _on_fit_complete(self):
        """
        When fit is complete ,reset the fit button label.
        """
        self.btFit.SetLabel("Fit")
        self.bind_fit_button()
        
    def _is_2D(self):
        """
        Check if data_name is Data2D
        
        :return: True or False
        
        """
        if self.data.__class__.__name__ == "Data2D" or \
                        self.enable2D:
            return True
        return False
            
    def _on_engine_change(self, name):
        """
        get the current name of the fit engine type
         and update the panel accordingly
        """
        
        self.engine_type = str(name)
        self.state.engine_type = self.engine_type
        if not self.is_mac:
            if len(self.parameters) == 0:
                self.Layout()
                return
            self.Layout()
            self.Refresh()
        
  
        
    def _fill_range_sizer(self):
        """
        Fill the sizer containing the plotting range
        add  access to npts
        """
        is_2Ddata = False
        
        # Check if data is 2D
        if self.data.__class__.__name__ ==  "Data2D" or \
                        self.enable2D:
            is_2Ddata = True
            
        title = "Fitting"
        #smear messages & titles
        smear_message_none  =  "No smearing is selected..."
        smear_message_dqdata  =  "The dQ data is being used for smearing..."
        smear_message_2d  =  "Higher accuracy is very time-expensive. Use it with care..."
        smear_message_new_ssmear  =  "Please enter only the value of interest to customize smearing..."
        smear_message_new_psmear  =  "Please enter both; the dQ will be generated by interpolation..."
        smear_message_2d_x_title = "<dQp>[1/A]:"
        smear_message_2d_y_title = "<dQs>[1/A]:"        
        smear_message_pinhole_min_title = "dQ_low[1/A]:"
        smear_message_pinhole_max_title = "dQ_high[1/A]:"
        smear_message_slit_height_title = "Slit height[1/A]:"
        smear_message_slit_width_title = "Slit width[1/A]:"
        
        self._get_smear_info()
        
        #Sizers
        box_description_range = wx.StaticBox(self, -1,str(title))
        boxsizer_range = wx.StaticBoxSizer(box_description_range, wx.VERTICAL)      
        self.sizer_set_smearer = wx.BoxSizer(wx.VERTICAL)
        sizer_smearer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_new_smear= wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_set_masking = wx.BoxSizer(wx.HORIZONTAL)
        sizer_chi2 = wx.BoxSizer(wx.VERTICAL)
        smear_set_box= wx.StaticBox(self, -1,'Set Instrumental Smearing')
        sizer_smearer_box = wx.StaticBoxSizer(smear_set_box, wx.HORIZONTAL)
        sizer_smearer_box.SetMinSize((_DATA_BOX_WIDTH,85))
        sizer_fit = wx.GridSizer(2, 4, 2, 6)
        
        # combobox for smear2d accuracy selection
        self.smear_accuracy = wx.ComboBox(self, -1,size=(50,-1),style=wx.CB_READONLY)
        self._set_accuracy_list()
        self.smear_accuracy.SetValue(self.smear2d_accuracy)
        self.smear_accuracy.SetSelection(0)
        self.smear_accuracy.SetToolTipString("'Higher' uses more Gaussian points for smearing computation.")
                   
        wx.EVT_COMBOBOX(self.smear_accuracy,-1, self._on_select_accuracy)

        #Fit button
        self.btFit = wx.Button(self,wx.NewId(),'Fit', size=(88,25))
        self.default_bt_colour =  self.btFit.GetDefaultAttributes()
        self.btFit.Bind(wx.EVT_BUTTON, self._onFit,id= self.btFit.GetId())
        self.btFit.SetToolTipString("Start fitting.")
        
        #textcntrl for custom resolution
        self.smear_pinhole_max = self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH-25,20),style=wx.TE_PROCESS_ENTER,
                                            text_enter_callback = self.onPinholeSmear)
        self.smear_pinhole_min = self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH-25,20),style=wx.TE_PROCESS_ENTER,
                                            text_enter_callback = self.onPinholeSmear)
        self.smear_slit_height= self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH-25,20),style=wx.TE_PROCESS_ENTER,
                                            text_enter_callback = self.onSlitSmear)
        self.smear_slit_width = self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH-25,20),style=wx.TE_PROCESS_ENTER,
                                            text_enter_callback = self.onSlitSmear)

        ## smear
        self.smear_data_left= BGTextCtrl(self, -1, size=(_BOX_WIDTH-25,20), style=0)
        self.smear_data_left.SetValue(str(self.dq_l))
        self.smear_data_right = BGTextCtrl(self, -1, size=(_BOX_WIDTH-25,20), style=0)
        self.smear_data_right.SetValue(str(self.dq_r))

        #set default values for smear
        self.smear_pinhole_max.SetValue(str(self.dx_max))
        self.smear_pinhole_min.SetValue(str(self.dx_min))
        self.smear_slit_height.SetValue(str(self.dxl))
        self.smear_slit_width.SetValue(str(self.dxw))

        #Filling the sizer containing instruments smearing info.
        self.disable_smearer = wx.RadioButton(self, -1, 'None', style=wx.RB_GROUP)
        self.enable_smearer = wx.RadioButton(self, -1, 'Use dQ Data')
        #self.enable_smearer.SetToolTipString("Click to use the loaded dQ data for smearing.")
        self.pinhole_smearer = wx.RadioButton(self, -1, 'Custom Pinhole Smear')
        #self.pinhole_smearer.SetToolTipString("Click to input custom resolution for pinhole smearing.")
        self.slit_smearer = wx.RadioButton(self, -1, 'Custom Slit Smear')
        #self.slit_smearer.SetToolTipString("Click to input custom resolution for slit smearing.")
        self.Bind(wx.EVT_RADIOBUTTON, self.onSmear, id=self.disable_smearer.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.onSmear, id=self.enable_smearer.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.onPinholeSmear, id=self.pinhole_smearer.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.onSlitSmear, id=self.slit_smearer.GetId())
        self.disable_smearer.SetValue(True)
        
        # add 4 types of smearing to the sizer
        sizer_smearer.Add( self.disable_smearer,0, wx.LEFT, 10)
        sizer_smearer.Add((10,10))
        sizer_smearer.Add( self.enable_smearer)
        sizer_smearer.Add((10,10))
        sizer_smearer.Add( self.pinhole_smearer ) 
        sizer_smearer.Add((10,10))
        sizer_smearer.Add( self.slit_smearer ) 
        sizer_smearer.Add((10,10))       
        
        # StaticText for chi2, N(for fitting), Npts
        self.tcChi    =  BGTextCtrl(self, -1, "-", size=(75,20), style=0)
        self.tcChi.SetToolTipString("Chi2/Npts(Fit)")
        self.Npts_fit    =  BGTextCtrl(self, -1, "-", size=(75,20), style=0)
        self.Npts_fit.SetToolTipString(\
                            " Npts : number of points selected for fitting")
        self.Npts_total  =  self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH, 20), 
                        style=wx.TE_PROCESS_ENTER, 
                        text_enter_callback=self._onQrangeEnter)
        self.Npts_total.SetValue(format_number(self.npts_x))
        self.Npts_total.SetToolTipString(\
                                " Total Npts : total number of data points")
        
        # Update and Draw button
        self.draw_button = wx.Button(self,wx.NewId(),'Compute', size=(88,24))
        self.draw_button.Bind(wx.EVT_BUTTON, \
                              self._onDraw,id= self.draw_button.GetId())
        self.draw_button.SetToolTipString("Compute and Draw.")
        
        box_description_1= wx.StaticText(self, -1,'    Chi2/Npts')
        box_description_2= wx.StaticText(self, -1,'Npts(Fit)')
        box_description_3= wx.StaticText(self, -1,'Total Npts')
        box_description_3.SetToolTipString( \
                                " Total Npts : total number of data points")
        #box_description_4= wx.StaticText(self, -1,' ')
        
        
        sizer_fit.Add(box_description_1,0,0)
        sizer_fit.Add(box_description_2,0,0)
        sizer_fit.Add(box_description_3,0,0)       
        sizer_fit.Add(self.draw_button,0,0)
        sizer_fit.Add(self.tcChi,0,0)
        sizer_fit.Add(self.Npts_fit ,0,0)
        sizer_fit.Add(self.Npts_total,0,0)
        sizer_fit.Add(self.btFit,0,0) 

        # StaticText for smear
        #self.tcChi    =  wx.StaticText(self, -1, "-", style=wx.ALIGN_LEFT)
        self.smear_description_none =  wx.StaticText(self, -1, 
                                    smear_message_none , style=wx.ALIGN_LEFT)
        self.smear_description_dqdata =  wx.StaticText(self, 
                                -1, smear_message_dqdata , style=wx.ALIGN_LEFT)
        self.smear_description_type =  wx.StaticText(self,
                                     -1, "Type:" , style=wx.ALIGN_LEFT)
        self.smear_description_accuracy_type =  wx.StaticText(self, -1, 
                                        "Accuracy:" , style=wx.ALIGN_LEFT)
        self.smear_description_smear_type =  BGTextCtrl(self, -1, 
                                                        size=(57,20), style=0)
        self.smear_description_smear_type.SetValue(str(self.dq_l))
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.smear_description_2d =  wx.StaticText(self, -1, 
                                    smear_message_2d  , style=wx.ALIGN_LEFT)
        self.smear_message_new_s = wx.StaticText(self, -1,
                         smear_message_new_ssmear, style=wx.ALIGN_LEFT)
        self.smear_message_new_p = wx.StaticText(self, -1,
                                 smear_message_new_psmear , style=wx.ALIGN_LEFT)
        self.smear_description_2d_x     =  wx.StaticText(self, -1, smear_message_2d_x_title  , style=wx.ALIGN_LEFT)
        self.smear_description_2d_x.SetToolTipString("  dQp(parallel) in q_r direction.")
        self.smear_description_2d_y     =  wx.StaticText(self, -1, smear_message_2d_y_title  , style=wx.ALIGN_LEFT)
        self.smear_description_2d_y.SetToolTipString(" dQs(perpendicular) in q_phi direction.")
        self.smear_description_pin_min     =  wx.StaticText(self, -1, smear_message_pinhole_min_title  , style=wx.ALIGN_LEFT)
        self.smear_description_pin_max     =  wx.StaticText(self, -1, smear_message_pinhole_max_title  , style=wx.ALIGN_LEFT)
        self.smear_description_slit_height    =  wx.StaticText(self, -1, smear_message_slit_height_title   , style=wx.ALIGN_LEFT)
        self.smear_description_slit_width    =  wx.StaticText(self, -1, smear_message_slit_width_title   , style=wx.ALIGN_LEFT)
        
        #arrange sizers 
        #boxsizer1.Add( self.tcChi )  
        self.sizer_set_smearer.Add(sizer_smearer )
        self.sizer_set_smearer.Add((10,10))
        self.sizer_set_smearer.Add( self.smear_description_none,0, wx.CENTER, 10 ) 
        self.sizer_set_smearer.Add( self.smear_description_dqdata,0, wx.CENTER, 10 )
        self.sizer_set_smearer.Add( self.smear_description_2d,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_type,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_accuracy_type,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_accuracy )
        self.sizer_new_smear.Add( self.smear_description_smear_type,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add((15,-1))
        self.sizer_new_smear.Add( self.smear_description_2d_x,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_pin_min,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_slit_height,0, wx.CENTER, 10 )

        self.sizer_new_smear.Add( self.smear_pinhole_min,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_slit_height,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_data_left,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add((20,-1))
        self.sizer_new_smear.Add( self.smear_description_2d_y,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_pin_max,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_description_slit_width,0, wx.CENTER, 10 )

        self.sizer_new_smear.Add( self.smear_pinhole_max,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_slit_width,0, wx.CENTER, 10 )
        self.sizer_new_smear.Add( self.smear_data_right,0, wx.CENTER, 10 )
           
        self.sizer_set_smearer.Add( self.smear_message_new_s,0, wx.CENTER, 10)
        self.sizer_set_smearer.Add( self.smear_message_new_p,0, wx.CENTER, 10)
        self.sizer_set_smearer.Add((5,2))
        self.sizer_set_smearer.Add( self.sizer_new_smear,0, wx.CENTER, 10 )
        
        # add all to chi2 sizer 
        sizer_smearer_box.Add(self.sizer_set_smearer)       
        sizer_chi2.Add(sizer_smearer_box)
        sizer_chi2.Add((-1,5))
        
        # hide all smear messages and textctrl
        self._hide_all_smear_info()
        
        # get smear_selection
        self.current_smearer= smear_selection( self.data, self.model )

        # Show only the relevant smear messages, etc
        if self.current_smearer == None:
            if not is_2Ddata:
                self.smear_description_none.Show(True)
                self.enable_smearer.Disable()  
            else:
                self.smear_description_none.Show(True)
                #self.smear_description_2d.Show(True) 
                #self.pinhole_smearer.Disable() 
                self.slit_smearer.Disable()   
                #self.enable_smearer.Disable() 
            if self.data == None:
                self.slit_smearer.Disable() 
                self.pinhole_smearer.Disable() 
                self.enable_smearer.Disable() 
        else: self._show_smear_sizer()
        boxsizer_range.Add(self.sizer_set_masking)
         #2D data? default
        is_2Ddata = False
        
        #check if it is 2D data
        if self.data.__class__.__name__ ==  "Data2D" or \
                        self.enable2D:
            is_2Ddata = True
            
        self.sizer5.Clear(True)
     
        self.qmin  = self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH,20),
                                          style=wx.TE_PROCESS_ENTER,
                                    text_enter_callback = self._onQrangeEnter)
        self.qmin.SetValue(str(self.qmin_x))
        self.qmin.SetToolTipString("Minimun value of Q in linear scale.")
     
        self.qmax  = self.ModelTextCtrl(self, -1,size=(_BOX_WIDTH,20),
                                          style=wx.TE_PROCESS_ENTER,
                                        text_enter_callback=self._onQrangeEnter)
        self.qmax.SetValue(str(self.qmax_x))
        self.qmax.SetToolTipString("Maximum value of Q in linear scale.")
        """
        self.theory_npts_tcrtl  = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH, 20), 
                        style=wx.TE_PROCESS_ENTER, 
                        text_enter_callback=self._onQrangeEnter)
        self.theory_npts_tcrtl.SetValue(format_number(self.npts_x))
        self.theory_npts_tcrtl.SetToolTipString("Number of point to plot.")
        """
        id = wx.NewId()
        self.reset_qrange =wx.Button(self,id,'Reset',size=(77,20))
      
        self.reset_qrange.Bind(wx.EVT_BUTTON, self.on_reset_clicked,id=id)
        self.reset_qrange.SetToolTipString("Reset Q range to the default values")
     
        sizer_horizontal=wx.BoxSizer(wx.HORIZONTAL)
        sizer= wx.GridSizer(2, 4, 2, 6)

        self.btEditMask = wx.Button(self,wx.NewId(),'Editor', size=(88,23))
        self.btEditMask.Bind(wx.EVT_BUTTON, self._onMask,id= self.btEditMask.GetId())
        self.btEditMask.SetToolTipString("Edit Mask.")
        self.EditMask_title = wx.StaticText(self, -1, ' Masking(2D)')

        sizer.Add(wx.StaticText(self, -1, 'Q range'))     
        sizer.Add(wx.StaticText(self, -1, ' Min[1/A]'))
        sizer.Add(wx.StaticText(self, -1, ' Max[1/A]'))
        sizer.Add(self.EditMask_title)
        #sizer.Add(wx.StaticText(self, -1, ''))
        sizer.Add(self.reset_qrange)   
        sizer.Add(self.qmin)
        sizer.Add(self.qmax)
        #sizer.Add(self.theory_npts_tcrtl)
        sizer.Add(self.btEditMask)
        boxsizer_range.Add(sizer_chi2) 
        boxsizer_range.Add((10,10))
        boxsizer_range.Add(sizer)
        
        boxsizer_range.Add((10,15))
        boxsizer_range.Add(sizer_fit)
        if is_2Ddata:
            self.btEditMask.Enable()  
            self.EditMask_title.Enable() 
        else:
            self.btEditMask.Disable()  
            self.EditMask_title.Disable()
        ## save state
        self.save_current_state()
        self.sizer5.Add(boxsizer_range,0, wx.EXPAND | wx.ALL, 10)
        self.sizer5.Layout()

       
    def _fill_model_sizer(self, sizer):
        """
        fill sizer containing model info
        """
        ##Add model function Details button in fitpanel.
        ##The following 3 lines are for Mac. Let JHC know before modifying... 
        title = "Model"
        self.formfactorbox = None
        self.multifactorbox = None
        self.mbox_description= wx.StaticBox(self, -1,str(title))
        boxsizer1 = wx.StaticBoxSizer(self.mbox_description, wx.VERTICAL)
        
        id = wx.NewId()
        self.model_help =wx.Button(self,id,'Details', size=(80,23))
        self.model_help.Bind(wx.EVT_BUTTON, self.on_model_help_clicked,id=id)
        self.model_help.SetToolTipString("Model Function Help")
        id = wx.NewId()
        self.model_view = wx.Button(self, id,"1D Mode", size=(80, 23))
        self.model_view.Bind(wx.EVT_BUTTON, self._onModel2D, id=id)
        hint = "toggle view of model from 1D to 2D  or 2D to 1D"
        self.model_view.SetToolTipString(hint)
      
        self.shape_rbutton = wx.RadioButton(self, -1, 'Shapes',
                                             style=wx.RB_GROUP)
        self.shape_indep_rbutton = wx.RadioButton(self, -1, "Shape-Independent")
        self.struct_rbutton = wx.RadioButton(self, -1, "Structure Factor ")
        self.plugin_rbutton = wx.RadioButton(self, -1, "Customized Models")
                
        self.Bind(wx.EVT_RADIOBUTTON, self._show_combox,
                            id= self.shape_rbutton.GetId()) 
        self.Bind(wx.EVT_RADIOBUTTON, self._show_combox,
                            id= self.shape_indep_rbutton.GetId()) 
        self.Bind(wx.EVT_RADIOBUTTON, self._show_combox,
                            id= self.struct_rbutton.GetId()) 
        self.Bind(wx.EVT_RADIOBUTTON, self._show_combox,
                            id= self.plugin_rbutton.GetId())  
        #MAC needs SetValue
        self.shape_rbutton.SetValue(True)
      
        sizer_radiobutton = wx.GridSizer(2, 3, 5, 5)
        sizer_radiobutton.Add(self.shape_rbutton)
        sizer_radiobutton.Add(self.shape_indep_rbutton)
        #sizer_radiobutton.Add((5, 5))
        sizer_radiobutton.Add(self.model_view,1, wx.LEFT, 20)
        sizer_radiobutton.Add(self.plugin_rbutton)
        sizer_radiobutton.Add(self.struct_rbutton)
        #sizer_radiobutton.Add((5, 5))
        sizer_radiobutton.Add(self.model_help,1, wx.LEFT, 20)
        
        sizer_selection = wx.BoxSizer(wx.HORIZONTAL)
        mutifactor_selection = wx.BoxSizer(wx.HORIZONTAL)
        
        self.text1 = wx.StaticText(self,-1,"" )
        self.text2 = wx.StaticText(self,-1,"P(Q)*S(Q)" )
        self.mutifactor_text = wx.StaticText( self,-1,"No. of Shells: ")
        self.mutifactor_text1 = wx.StaticText( self,-1,"" )
        self.show_sld_button = wx.Button( self,-1,"Show SLD Profile" )
        self.show_sld_button.Bind(wx.EVT_BUTTON,self._on_show_sld)

        self.formfactorbox = wx.ComboBox(self, -1,style=wx.CB_READONLY)
        if self.model!= None:
            self.formfactorbox.SetValue(self.model.name)
        self.structurebox = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self.multifactorbox = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self.initialize_combox()
        wx.EVT_COMBOBOX(self.formfactorbox, -1, self._on_select_model)

        wx.EVT_COMBOBOX(self.structurebox, -1, self._on_select_model)
        wx.EVT_COMBOBOX(self.multifactorbox, -1, self._on_select_model)
        ## check model type to show sizer
        if self.model !=None:
            self._set_model_sizer_selection(self.model)
        
        sizer_selection.Add(self.text1)
        sizer_selection.Add((5, 5))
        sizer_selection.Add(self.formfactorbox)
        sizer_selection.Add((5, 5))
        sizer_selection.Add(self.text2)
        sizer_selection.Add((5, 5))
        sizer_selection.Add(self.structurebox)
       
        mutifactor_selection.Add((10,5))
        mutifactor_selection.Add(self.mutifactor_text)
        mutifactor_selection.Add(self.multifactorbox)
        mutifactor_selection.Add((5, 5))
        mutifactor_selection.Add(self.mutifactor_text1)
        mutifactor_selection.Add((10, 5))
        mutifactor_selection.Add(self.show_sld_button)

       
        boxsizer1.Add(sizer_radiobutton)
        boxsizer1.Add((10, 10))
        boxsizer1.Add(sizer_selection)
        boxsizer1.Add((10, 10))
        boxsizer1.Add(mutifactor_selection)
        
        self._set_multfactor_combobox()
        self.multifactorbox.SetSelection(1)
        self.show_sld_button.Hide()
        sizer.Add(boxsizer1,0, wx.EXPAND | wx.ALL, 10)
        sizer.Layout()
        
    def _set_sizer_dispersion(self):
        """
        draw sizer with gaussian dispersity parameters
        """
        self.fittable_param=[]
        self.fixed_param=[]
        self.orientation_params_disp=[]

        self.sizer4_4.Clear(True)
        if self.model==None:
            ##no model is selected
            return
        if not self.enable_disp.GetValue():
            ## the user didn't select dispersity display
            return 
            
        self._reset_dispersity()
        
        ## fill a sizer with the combobox to select dispersion type
        #sizer_select_dispers = wx.BoxSizer(wx.HORIZONTAL)  
        model_disp = wx.StaticText(self, -1, 'Function')
            
        import sans.models.dispersion_models 
        self.polydisp= sans.models.dispersion_models.models

        ix = 0
        iy = 0
        disp = wx.StaticText(self, -1, ' ')
        self.sizer4_4.Add(disp,( iy, ix),(1,1), 
                           wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1 
        values = wx.StaticText(self, -1, 'PD[ratio]')
        polytext = "Polydispersity (= STD/mean); "
        polytext +=  "the standard deviation over the mean value."
        values.SetToolTipString(polytext)

        self.sizer4_4.Add(values,( iy, ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 
                          0)
        ix +=2 
        if self.is_mac:
            err_text = 'Error'
        else:
            err_text = ''
        self.text_disp_1 = wx.StaticText(self, -1, err_text)
        self.sizer4_4.Add( self.text_disp_1,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        
        
        ix +=1 
        self.text_disp_min = wx.StaticText(self, -1, 'Min')
        self.sizer4_4.Add(self.text_disp_min,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 

        ix +=1 
        self.text_disp_max = wx.StaticText(self, -1, 'Max')
        self.sizer4_4.Add(self.text_disp_max,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
       
        ix += 1 
        npts = wx.StaticText(self, -1, 'Npts')
        npts.SetToolTipString("Number of sampling points for the numerical\n\
        integration over the distribution function.")
        self.sizer4_4.Add(npts,( iy, ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 1 
        nsigmas = wx.StaticText(self, -1, 'Nsigs')
        nsigmas.SetToolTipString("   Number of sigmas between which the range\n\
         of the distribution function will be used for weighting. \n\
        The value '3' covers 99.5% for Gaussian distribution \n\
        function. Note: Not recommended to change this value.")
        self.sizer4_4.Add(nsigmas,( iy, ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE,
                           0)
        ix +=1 
        self.sizer4_4.Add(model_disp,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        
        if self.engine_type=="park":
            self.text_disp_max.Show(True)
            self.text_disp_min.Show(True)

        for item in self.model.dispersion.keys():
            if not item in self.model.orientation_params:
                if not self.disp_cb_dict.has_key(item):
                    self.disp_cb_dict[item]= None
                name0="Distribution of " + item
                name1=item+".width"
                name2=item+".npts"
                name3=item+".nsigmas"
                if not self.model.details.has_key(name1):
                    self.model.details [name1] = ["",None,None] 

                iy += 1
                for p in self.model.dispersion[item].keys(): 
        
                    if p=="width":
                        ix = 0
                        cb = wx.CheckBox(self, -1, name0, (10, 10))
                        cb.SetToolTipString("Check mark to fit")
                        wx.EVT_CHECKBOX(self, cb.GetId(), self.select_param)
                        self.sizer4_4.Add( cb,( iy, ix),(1,1),  
                                           wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 
                                           5)
                        ix = 1
                        value= self.model.getParam(name1)
                        ctl1 = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH/1.3,20)
                                                  ,style=wx.TE_PROCESS_ENTER)
                        ctl1.SetLabel('PD[ratio]')
                        poly_text = "Polydispersity (STD/mean) of %s\n" % item
                        poly_text += "STD: the standard deviation"
                        poly_text += " from the mean value."
                        ctl1.SetToolTipString(poly_text)
                        ctl1.SetValue(str (format_number(value, True)))
                        self.sizer4_4.Add(ctl1, (iy,ix),(1,1),wx.EXPAND)
                        ## text to show error sign
                        ix = 2
                        text2=wx.StaticText(self, -1, '+/-')
                        self.sizer4_4.Add(text2,(iy, ix),(1,1),
                                          wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                        if not self.is_mac:
                            text2.Hide() 

                        ix = 3
                        ctl2 = wx.TextCtrl(self, -1, size=(_BOX_WIDTH/1.3,20), 
                                           style=0)
                  
                        self.sizer4_4.Add(ctl2, (iy,ix),(1,1), 
                                          wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                        if not self.is_mac:
                            ctl2.Hide()

                        ix = 4
                        ctl3 = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH/2,
                                            20), style=wx.TE_PROCESS_ENTER,
                                text_enter_callback = self._onparamRangeEnter)
                        
                        self.sizer4_4.Add(ctl3, (iy,ix),(1,1), 
                                          wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                       
                
                        ix = 5
                        ctl4 = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH/2,
                                            20), style=wx.TE_PROCESS_ENTER,
                            text_enter_callback = self._onparamRangeEnter)
                        
                        self.sizer4_4.Add(ctl4, (iy,ix),(1,1), 
                                          wx.EXPAND|wx.ADJUST_MINSIZE, 0)

                        
                        if self.engine_type=="park":
                            ctl3.Show(True)
                            ctl4.Show(True)
                                                              
                    elif p=="npts":
                            ix = 6
                            value= self.model.getParam(name2)
                            Tctl = self.ModelTextCtrl(self, -1, 
                                                       size=(_BOX_WIDTH/2.2,20),
                                                style=wx.TE_PROCESS_ENTER)
                            
                            Tctl.SetValue(str (format_number(value)))
                            self.sizer4_4.Add(Tctl, (iy,ix),(1,1),
                                               wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                            self.fixed_param.append([None,name2, Tctl,None,None,
                                                      None, None,None])
                    elif p=="nsigmas":
                            ix = 7
                            value= self.model.getParam(name3)
                            Tct2 = self.ModelTextCtrl(self, -1, 
                                                      size=(_BOX_WIDTH/2.2,20),
                                                style=wx.TE_PROCESS_ENTER)
                            
                            Tct2.SetValue(str (format_number(value)))
                            self.sizer4_4.Add(Tct2, (iy,ix),(1,1),
                                               wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                            #ix +=1
                            #self.sizer4_4.Add((20,20), (iy,ix),(1,1),
                            #                   wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                            
                            self.fixed_param.append([None, name3, Tct2,
                                                     None, None, None, 
                                                     None, None])


                ix = 8      
                disp_box = wx.ComboBox(self, -1,size=(65,-1),
                                style=wx.CB_READONLY, name = '%s'% name1)
                for key, value in self.polydisp.iteritems():
                    name_disp = str(key)
                    disp_box.Append(name_disp,value)
                    disp_box.SetStringSelection("gaussian") 
                wx.EVT_COMBOBOX(disp_box,-1, self._on_disp_func)      
                self.sizer4_4.Add(disp_box,(iy,ix),(1,1), wx.EXPAND)
                self.fittable_param.append([cb,name1,ctl1,text2,
                                                    ctl2, ctl3, ctl4, disp_box])                     
                           
        ix =0
        iy +=1 
        self.sizer4_4.Add((20,20),(iy,ix),(1,1), 
                          wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)  
        first_orient  = True
        for item in self.model.dispersion.keys():
            if  item in self.model.orientation_params:
                if not self.disp_cb_dict.has_key(item):
                    self.disp_cb_dict[item]= None
                name0="Distribution of " + item
                name1=item+".width"
                name2=item+".npts"
                name3=item+".nsigmas"
                
                if not self.model.details.has_key(name1):
                    self.model.details [name1] = ["",None,None]                  
 

                iy += 1
                for p in self.model.dispersion[item].keys(): 
        
                    if p=="width":
                        ix = 0
                        cb = wx.CheckBox(self, -1, name0, (10, 10))
                        cb.SetToolTipString("Check mark to fit")
                        wx.EVT_CHECKBOX(self, cb.GetId(), self.select_param)
                        self.sizer4_4.Add( cb,( iy, ix),(1,1),  
                                           wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 
                                           5)
                        if self.data.__class__.__name__ ==  "Data2D" or \
                                    self.enable2D:
                            cb.Show(True)
                        elif cb.IsShown():
                            cb.Hide()
                        ix = 1
                        value= self.model.getParam(name1)
                        ctl1 = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH/1.3,
                                        20),style=wx.TE_PROCESS_ENTER)
                        poly_tip = "Absolute Sigma for %s." % item
                        ctl1.SetToolTipString(poly_tip)
                        ctl1.SetValue(str (format_number(value, True)))
                        if self.data.__class__.__name__ == "Data2D" or \
                                    self.enable2D:
                            if first_orient:
                                values.SetLabel('PD[ratio], Sig[deg]')
                                poly_text = "PD(polydispersity for lengths):\n"
                                poly_text +=  "It should be a value between"
                                poly_text +=  "0 and 1\n"
                                poly_text += "Sigma for angles: \n"
                                poly_text += "It is the STD (ratio*mean)"
                                poly_text += " of the distribution.\n "
                            
                                values.SetToolTipString(poly_text)
                                first_orient = False
                            ctl1.Show(True)
                        elif ctl1.IsShown():
                            ctl1.Hide()
                        
                        self.sizer4_4.Add(ctl1, (iy,ix),(1,1),wx.EXPAND)
                        ## text to show error sign
                        ix = 2
                        text2=wx.StaticText(self, -1, '+/-')
                        self.sizer4_4.Add(text2,(iy, ix),(1,1),
                                          wx.EXPAND|wx.ADJUST_MINSIZE, 0)

                        text2.Hide() 

                        ix = 3
                        ctl2 = wx.TextCtrl(self, -1, size=(_BOX_WIDTH/1.3,20), 
                                           style=0)
                    
                        self.sizer4_4.Add(ctl2, (iy,ix),(1,1), 
                                          wx.EXPAND|wx.ADJUST_MINSIZE, 0)

                        ctl2.Hide()
                        if self.data.__class__.__name__ ==  "Data2D" or \
                                self.enable2D:
                            if self.is_mac:  
                                text2.Show(True)
                                ctl2.Show(True)  
                            
                        ix = 4
                        ctl3 = self.ModelTextCtrl(self, -1, 
                                                  size=(_BOX_WIDTH/2,20), 
                                                  style=wx.TE_PROCESS_ENTER,
                                text_enter_callback = self._onparamRangeEnter)

                        self.sizer4_4.Add(ctl3, (iy,ix),(1,1), 
                                          wx.EXPAND|wx.ADJUST_MINSIZE, 0)

                        ctl3.Hide()
                
                        ix = 5
                        ctl4 = self.ModelTextCtrl(self, -1, 
                            size=(_BOX_WIDTH/2,20), style=wx.TE_PROCESS_ENTER,
                                text_enter_callback = self._onparamRangeEnter)
                        self.sizer4_4.Add(ctl4, (iy,ix),(1,1), 
                                          wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                        ctl4.Hide()
                        
                        if self.data.__class__.__name__ ==  "Data2D" or \
                                self.enable2D:
                            ctl3.Show(True)
                            ctl4.Show(True) 
                             
                    elif p=="npts":
                            ix = 6
                            value= self.model.getParam(name2)
                            Tctl = self.ModelTextCtrl(self, -1, 
                                                     size=(_BOX_WIDTH/2.2, 20),
                                                style=wx.TE_PROCESS_ENTER)
                            
                            Tctl.SetValue(str (format_number(value)))
                            if self.data.__class__.__name__ ==  "Data2D" or \
                                    self.enable2D:
                                Tctl.Show(True)
                            else:
                                Tctl.Hide()
                            self.sizer4_4.Add(Tctl, (iy,ix),(1,1),
                                               wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                            self.fixed_param.append([None,name2, Tctl,None,None,
                                                      None, None,None])
                            self.orientation_params_disp.append([None,name2, 
                                                    Tctl,None,None,
                                                      None, None,None])
                    elif p=="nsigmas":
                            ix = 7
                            value= self.model.getParam(name3)
                            Tct2 = self.ModelTextCtrl(self, -1, 
                                                      size=(_BOX_WIDTH/2.2,20),
                                                style=wx.TE_PROCESS_ENTER)
                            
                            Tct2.SetValue(str (format_number(value)))
                            if self.data.__class__.__name__ ==  "Data2D" or \
                                    self.enable2D:
                                Tct2.Show(True)
                            else:
                                Tct2.Hide()
                            self.sizer4_4.Add(Tct2, (iy,ix),(1,1),
                                               wx.EXPAND|wx.ADJUST_MINSIZE, 0)


                            self.fixed_param.append([None,name3, Tct2
                                                 ,None,None, None, None,None])    
                                                       
                            self.orientation_params_disp.append([None,name3, 
                                            Tct2 ,None,None, None, None,None])
        

                ix = 8      
                disp_box = wx.ComboBox(self, -1,size=(65,-1),
                                style=wx.CB_READONLY, name = '%s'% name1)
                for key, value in self.polydisp.iteritems():
                    name_disp = str(key)
                    disp_box.Append(name_disp,value)
                    disp_box.SetStringSelection("gaussian") 
                wx.EVT_COMBOBOX(disp_box,-1, self._on_disp_func)      
                self.sizer4_4.Add(disp_box,(iy,ix),(1,1), wx.EXPAND)
                self.fittable_param.append([cb,name1,ctl1,text2,
                                            ctl2, ctl3, ctl4, disp_box])
                self.orientation_params_disp.append([cb,name1,ctl1,
                                            text2, ctl2, ctl3, ctl4, disp_box])
                       
                if self.data.__class__.__name__ == "Data2D" or \
                                self.enable2D:
                    disp_box.Show(True)
                else:
                    disp_box.Hide()
        

        self.state.disp_cb_dict = copy.deepcopy(self.disp_cb_dict)  
          
        self.state.model = self.model.clone()  
         ## save state into
        self.state.cb1 = self.cb1.GetValue()
        self._copy_parameters_state(self.parameters, self.state.parameters)
        self._copy_parameters_state(self.orientation_params_disp,
                                     self.state.orientation_params_disp)
        self._copy_parameters_state(self.fittable_param, 
                                    self.state.fittable_param)
        self._copy_parameters_state(self.fixed_param, self.state.fixed_param)


        wx.PostEvent(self.parent, StatusEvent(status=\
                        " Selected Distribution: Gaussian"))   
        #Fill the list of fittable parameters
        self.select_all_param(event=None)
        
        self.Layout()

    
    def _onDraw(self, event):
        """
        Update and Draw the model
        """ 
        if self.model ==None:
            msg="Please select a Model first..."
            wx.MessageBox(msg, 'Info')

            return
        flag = self._update_paramv_on_fit()         
        self._onparamEnter_helper()
        if not flag:
            msg= "The parameters are invalid"
            wx.PostEvent(self.parent.parent, StatusEvent(status= msg ))
            return 
        

    def _onFit(self, event):     
        """
        Allow to fit
        """
        if event != None:
            event.Skip()
        if len(self.parent._manager.fit_thread_list)>0 and\
                    self.parent._manager._fit_engine != "park":
            msg = "The FitEnging will be set to 'ParkMC'\n"
            msg += " to fit with more than one data set..."
            wx.MessageBox(msg, 'Info')
            #wx.PostEvent(self._manager.parent, StatusEvent(status=\
            #                "Fitting: %s"%msg))
            
        if self.data is None:
            msg = "Please get Data first..."
            wx.MessageBox(msg, 'Info')
            wx.PostEvent(self._manager.parent, StatusEvent(status=\
                            "Fit: %s" % msg))
            return
        if self.model is None:
            msg = "Please select a Model first..."
            wx.MessageBox(msg, 'Info')
            wx.PostEvent(self._manager.parent, StatusEvent(status=\
                            "Fit: %s"%msg, type="stop"))
            return
        
        if len(self.param_toFit) <= 0:
            msg= "Select at least one parameter to fit"
            wx.MessageBox(msg, 'Info')
            wx.PostEvent(self._manager.parent, StatusEvent(status= msg, 
                                                         type="stop" ))
            return 
        
        flag = self._update_paramv_on_fit() 
                
        if not flag:
            msg= "Fitting range or parameters are invalid"
            wx.PostEvent(self.parent.parent, StatusEvent(status= msg, 
                                                         type="stop"))
            return 
              
        self.select_param(event =None)
        
        #Clear errors if exist from previous fitting
        #self._clear_Err_on_Fit() 

        # Remove or do not allow fitting on the Q=0 point, especially 
        # when y(q=0)=None at x[0].         
        self.qmin_x = float(self.qmin.GetValue())
        self.qmax_x = float(self.qmax.GetValue())
        self._manager._reset_schedule_problem(value=0, uid=self.uid)
        self._manager.schedule_for_fit(uid=self.uid,value=1, fitproblem=None) 
        self._manager.set_fit_range(uid=self.uid,qmin=self.qmin_x, 
                                   qmax=self.qmax_x)
        #single fit 
        self._manager.onFit(uid=self.uid)
        self.btFit.SetLabel("Stop")
        self.bind_fit_button()
           
   
    def bind_fit_button(self):
        """
        bind the fit button to either fit handler or stop fit handler
        """
        self.btFit.Unbind(event=wx.EVT_BUTTON, id= self.btFit.GetId())
        if self.btFit.GetLabel().lower() == "stop":
            self.fit_started = True
            self.btFit.SetForegroundColour('red')
            self.btFit.Bind(event=wx.EVT_BUTTON, handler=self._StopFit,
                             id=self.btFit.GetId())
        elif self.btFit.GetLabel().lower() == "fit":
            self.fit_started = False
            self.btFit.SetDefault()
            self.btFit.SetForegroundColour('black')
            #self.btFit.SetBackgroundColour(self.default_bt_colour)
            self.btFit.Bind(event=wx.EVT_BUTTON, handler=self._onFit, 
                            id=self.btFit.GetId())
        else:
            msg = "FitPage: fit button has unknown label"
            raise ValuerError, msg
        self._manager._reset_schedule_problem(value=0)
          
    def is_fitting(self):
        if self.fit_started:
            self._StopFit(event=None)
            
    def _StopFit(self, event=None):
        """
        Stop fit 
        """
        #time.sleep(0.1)
        if event != None:
            event.Skip()
        #if self.engine_type=="scipy":
        self._manager.stop_fit(self.uid)
        self._manager._reset_schedule_problem(value=0)
        self._on_fit_complete()
         
    def _on_select_model(self, event=None): 
        """
        call back for model selection
        """  
        
        self.Show(False)    
        self._on_select_model_helper() 
        self.set_model_param_sizer(self.model)                   
        if self.model is None:
            self._set_bookmark_flag(False)
            self._keep.Enable(False)
            self._set_save_flag(False)
        self.enable_disp.SetValue(False)
        self.disable_disp.SetValue(True)
        try:
            self.set_dispers_sizer()
        except:
            pass
        #self.btFit.SetFocus() 
        self.state.enable_disp = self.enable_disp.GetValue()
        self.state.disable_disp = self.disable_disp.GetValue()
        self.state.pinhole_smearer = self.pinhole_smearer.GetValue()
        self.state.slit_smearer = self.slit_smearer.GetValue()
    
        self.state.structurecombobox = self.structurebox.GetCurrentSelection()
        self.state.formfactorcombobox = self.formfactorbox.GetCurrentSelection()
      
        if self.model != None:
            self._set_copy_flag(True)
            self._set_paste_flag(True)
            if self.data != None:
                self._set_bookmark_flag(True)
                self._keep.Enable(True)
            #self._set_save_flag(True)
            # Reset smearer, model and data
            self._set_smear(self.data)
            try:
                # update smearer sizer
                self.onSmear(None)
                temp_smear = None
                if self.enable_smearer.GetValue():
                    # Set the smearer environments
                    temp_smear = self.smearer
            except:
                raise
                ## error occured on chisqr computation
                #pass
            ## event to post model to fit to fitting plugins
            (ModelEventbox, EVT_MODEL_BOX) = wx.lib.newevent.NewEvent()
         
            ## set smearing value whether or not 
            #    the data contain the smearing info
            evt = ModelEventbox(model=self.model, 
                                        smearer=temp_smear, 
                                        qmin=float(self.qmin_x),
                                        uid=self.uid,
                                     qmax=float(self.qmax_x)) 
   
            self._manager._on_model_panel(evt=evt)
            self.mbox_description.SetLabel("Model [%s]" % str(self.model.name))
            self.state.model = self.model.clone()
            self.state.model.name = self.model.name

            
        if event != None:
            ## post state to fit panel
            new_event = PageInfoEvent(page = self)
            wx.PostEvent(self.parent, new_event) 
            #update list of plugins if new plugin is available
            if self.plugin_rbutton.GetValue():
                temp = self.parent.update_model_list()
                if temp:
                    self.model_list_box = temp
                    current_val = self.formfactorbox.GetValue()
                    pos = self.formfactorbox.GetSelection()
                    self._show_combox_helper()
                    self.formfactorbox.SetSelection(pos)
                    self.formfactorbox.SetValue(current_val)
            self._onDraw(event=None)
        else:
            self._draw_model()
        self.SetupScrolling()
        self.Show(True)   
      
    def _onparamEnter(self,event):
        """ 
        when enter value on panel redraw model according to changed
        """
        if self.model ==None:
            msg="Please select a Model first..."
            wx.MessageBox(msg, 'Info')
            #wx.PostEvent(self._manager.parent, StatusEvent(status=\
            #                "Parameters: %s"%msg))
            return

        #default flag
        flag = False
        self.fitrange = True
        #get event object
        tcrtl = event.GetEventObject()
        
        #wx.PostEvent(self._manager.parent, StatusEvent(status=" \
        #                        updating ... ",type="update"))
        #Clear msg if previously shown.
        msg= ""
        wx.PostEvent(self.parent.parent, StatusEvent(status = msg ))

        if check_float(tcrtl):
            flag = self._onparamEnter_helper() 
            self.set_npts2fit() 
            if self.fitrange:             
                temp_smearer = None
                if not self.disable_smearer.GetValue():
                    temp_smearer= self.current_smearer
                    ## set smearing value whether or not 
                    #        the data contain the smearing info
                    if self.slit_smearer.GetValue():
                        flag1 = self.update_slit_smear()
                        flag = flag or flag1
                    elif self.pinhole_smearer.GetValue():
                        flag1 = self.update_pinhole_smear()
                        flag = flag or flag1
                elif self.data.__class__.__name__ !=  "Data2D" and \
                        not self.enable2D:
                    self._manager.set_smearer(smearer=temp_smearer, 
                                              enable2D=self.enable2D,
                                              uid=self.uid,
                                             qmin= float(self.qmin_x),
                                            qmax= float(self.qmax_x),
                                            draw=True) 
                if flag:   
                    #self.compute_chisqr(smearer= temp_smearer)
        
                    ## new state posted
                    if self.state_change:
                        #self._undo.Enable(True)
                        event = PageInfoEvent(page = self)
                        wx.PostEvent(self.parent, event)
                    self.state_change= False 
            else: 
                # invalid fit range: do nothing here: 
                # msg already displayed in validate 
                return      
        else:
            self.save_current_state()
            msg= "Cannot Plot :Must enter a number!!!  "
            wx.PostEvent(self.parent.parent, StatusEvent(status = msg ))
             
        self.save_current_state() 
        return 
   
    def _onparamRangeEnter(self, event):
        """
        Check validity of value enter in the parameters range field
        """
        #if self.check_invalid_panel():
        #    return
        tcrtl= event.GetEventObject()
        #Clear msg if previously shown.
        msg= ""
        wx.PostEvent(self.parent.parent, StatusEvent(status = msg ))
        # Flag to register when a parameter has changed.
        is_modified = False
        if tcrtl.GetValue().lstrip().rstrip()!="":
            try:
                value = float(tcrtl.GetValue())
                tcrtl.SetBackgroundColour(wx.WHITE)
                self._check_value_enter(self.fittable_param ,is_modified)
                self._check_value_enter(self.parameters ,is_modified) 
            except:
                tcrtl.SetBackgroundColour("pink")
                msg= "Model Error:wrong value entered : %s"% sys.exc_value
                wx.PostEvent(self.parent.parent, StatusEvent(status = msg ))
                return 
        else:
           tcrtl.SetBackgroundColour(wx.WHITE)
           
        #self._undo.Enable(True)
        self.save_current_state()
        event = PageInfoEvent(page = self)
        wx.PostEvent(self.parent, event)
        self.state_change= False

                    
    def _onQrangeEnter(self, event):
        """
        Check validity of value enter in the Q range field
        """
        #if self.check_invalid_panel():
        #    return
        tcrtl= event.GetEventObject()
        #Clear msg if previously shown.
        msg= ""
        wx.PostEvent(self.parent.parent, StatusEvent(status = msg ))
        # Flag to register when a parameter has changed.
        is_modified = False
        if tcrtl.GetValue().lstrip().rstrip()!="":
            try:
                value = float(tcrtl.GetValue())
                tcrtl.SetBackgroundColour(wx.WHITE)

                # If qmin and qmax have been modified, update qmin and qmax
                if self._validate_qrange( self.qmin, self.qmax):
                    tempmin = float(self.qmin.GetValue())
                    if tempmin != self.qmin_x:
                        self.qmin_x = tempmin
                    tempmax = float(self.qmax.GetValue())
                    if tempmax != self.qmax_x:
                        self.qmax_x = tempmax
                else:
                    tcrtl.SetBackgroundColour("pink")
                    msg= "Model Error:wrong value entered : %s"% sys.exc_value
                    wx.PostEvent(self.parent.parent, StatusEvent(status = msg ))
                    return 
                
            except:
                tcrtl.SetBackgroundColour("pink")
                msg= "Model Error:wrong value entered : %s"% sys.exc_value
                wx.PostEvent(self.parent.parent, StatusEvent(status = msg ))
                return 
            #Check if # of points for theory model are valid(>0).
            # check for 2d
            if self.data is not None:
                if self.data.__class__.__name__ == "Data2D" or \
                        self.enable2D:
                    # set mask   
                    radius= numpy.sqrt( self.data.qx_data*self.data.qx_data + 
                                        self.data.qy_data*self.data.qy_data )
                    index_data = ((self.qmin_x <= radius)& \
                                    (radius<= self.qmax_x))
                    index_data = (index_data)&(self.data.mask)
                    index_data = (index_data)&(numpy.isfinite(self.data.data))
                    if len(index_data[index_data]) < 10:
                        msg = "Cannot Plot :No or too little npts in"
                        msg += " that data range!!!  "
                        wx.PostEvent(self.parent.parent, 
                                     StatusEvent(status=msg))
                        return
                    else:
                        self.data.mask = index_data
                        #self.Npts_fit.SetValue(str(len(self.data.mask)))
                        self.set_npts2fit() 
                else:
                    index_data = ((self.qmin_x <= self.data.x)& \
                                  (self.data.x <= self.qmax_x))
                    self.Npts_fit.SetValue(str(len(self.data.x[index_data])))
            else:
                self.npts_x = self.Npts_total.GetValue()
                self._save_plotting_range()

        else:
           tcrtl.SetBackgroundColour("pink")
           msg= "Model Error:wrong value entered!!!"
           wx.PostEvent(self.parent.parent, StatusEvent(status = msg ))
        
        self._draw_model()
        ##update chi2
        #self.compute_chisqr(smearer= temp_smearer)
        #self._undo.Enable(True)
        self.save_current_state()
        event = PageInfoEvent(page = self)
        wx.PostEvent(self.parent, event)
        self.state_change= False
        return
    
    def _clear_Err_on_Fit(self):
        """
        hide the error text control shown 
        after fitting
        """
        if self.is_mac:
            return
        if hasattr(self,"text2_3"):
            self.text2_3.Hide()

        if len(self.parameters)>0:
            for item in self.parameters:
                #Skip t ifhe angle parameters if 1D data
                if self.data.__class__.__name__ !=  "Data2D" and \
                        not self.enable2D:
                    if item in self.orientation_params:
                        continue
                if item in self.param_toFit:
                    continue
                ## hide statictext +/-    
                if len(item) < 4 :
                    continue
                if item[3]!=None and item[3].IsShown():
                    item[3].Hide()
                ## hide textcrtl  for error after fit
                if item[4]!=None and item[4].IsShown():                   
                    item[4].Hide()
  
        if len(self.fittable_param)>0:
            for item in self.fittable_param:
                #Skip t ifhe angle parameters if 1D data
                if self.data.__class__.__name__ !=  "Data2D" and \
                        not self.enable2D:
                    if item in self.orientation_params:
                        continue
                if item in self.param_toFit:
                    continue
                if len(item) < 4 :
                    continue
                ## hide statictext +/-    
                if item[3]!=None and item[3].IsShown():
                    item[3].Hide()
                ## hide textcrtl  for error after fit
                if item[4]!=None and item[4].IsShown():
                    item[4].Hide()
        return        
                
    def _get_defult_custom_smear(self):
        """
        Get the defult values for custum smearing.
        """
        # get the default values
        if self.dxl == None: self.dxl = 0.0
        if self.dxw == None: self.dxw = ""
        if self.dx_min == None: self.dx_min = SMEAR_SIZE_L
        if self.dx_max == None: self.dx_max = SMEAR_SIZE_H
        
    def _get_smear_info(self):
        """
        Get the smear info from data.
       
        :return: self.smear_type, self.dq_l and self.dq_r, 
            respectively the type of the smear, dq_min and 
            dq_max for pinhole smear data 
            while dxl and dxw for slit smear
            
        """

        # default
        self.smear_type = None
        self.dq_l = None
        self.dq_r = None
        data = self.data
        if self.data is None:
            return
        elif self.data.__class__.__name__ ==  "Data2D" or \
                        self.enable2D:  
            if data.dqx_data == None or  data.dqy_data ==None: 
                return
            elif self.smearer != None and (data.dqx_data.any()!=0) and \
                            (data.dqx_data.any()!=0): 
                self.smear_type = "Pinhole2d"
                self.dq_l = format_number(numpy.average(data.dqx_data)) 
                self.dq_r = format_number(numpy.average(data.dqy_data))  
                return 
            else: 
                return
        # check if it is pinhole smear and get min max if it is.
        if data.dx != None and all(data.dx !=0): 
            self.smear_type = "Pinhole" 
            self.dq_l = data.dx[0]
            self.dq_r = data.dx[-1]
            
        # check if it is slit smear and get min max if it is.
        elif data.dxl != None or data.dxw != None: 
            self.smear_type = "Slit" 
            if data.dxl != None and all(data.dxl !=0):
                self.dq_l = data.dxl[0]
            if data.dxw != None and all(data.dxw !=0): 
                self.dq_r = data.dxw[0]    
        #return self.smear_type,self.dq_l,self.dq_r       
    
    def _show_smear_sizer(self):    
        """
        Show only the sizers depending on smear selection
        """
        # smear disabled
        if self.disable_smearer.GetValue():
            self.smear_description_none.Show(True)
        # 2Dsmear
        elif self._is_2D():
            self.smear_description_accuracy_type.Show(True)
            self.smear_accuracy.Show(True)
            self.smear_description_accuracy_type.Show(True)
            self.smear_description_2d.Show(True)
            self.smear_description_2d_x.Show(True)
            self.smear_description_2d_y.Show(True)
            if self.pinhole_smearer.GetValue():
                self.smear_pinhole_min.Show(True)
                self.smear_pinhole_max.Show(True)
        # smear from data
        elif self.enable_smearer.GetValue():

            self.smear_description_dqdata.Show(True)
            if self.smear_type != None:
                self.smear_description_smear_type.Show(True)
                if self.smear_type == 'Slit':
                    self.smear_description_slit_height.Show(True)
                    self.smear_description_slit_width.Show(True)                
                elif self.smear_type == 'Pinhole':
                    self.smear_description_pin_min.Show(True)
                    self.smear_description_pin_max.Show(True)
                self.smear_description_smear_type.Show(True)
                self.smear_description_type.Show(True)
                self.smear_data_left.Show(True)
                self.smear_data_right.Show(True)
        # custom pinhole smear
        elif self.pinhole_smearer.GetValue():
            if self.smear_type == 'Pinhole':
                self.smear_message_new_p.Show(True)
                self.smear_description_pin_min.Show(True)
                self.smear_description_pin_max.Show(True)

            self.smear_pinhole_min.Show(True)
            self.smear_pinhole_max.Show(True)
        # custom slit smear
        elif self.slit_smearer.GetValue():
            self.smear_message_new_s.Show(True)
            self.smear_description_slit_height.Show(True)
            self.smear_slit_height.Show(True)
            self.smear_description_slit_width.Show(True)
            self.smear_slit_width.Show(True)

    def _hide_all_smear_info(self):
        """
        Hide all smearing messages in the set_smearer sizer
        """
        self.smear_description_none.Hide()
        self.smear_description_dqdata.Hide()
        self.smear_description_type.Hide()
        self.smear_description_smear_type.Hide()
        self.smear_description_accuracy_type.Hide()
        self.smear_description_2d_x.Hide()
        self.smear_description_2d_y.Hide()
        self.smear_description_2d.Hide()
        
        self.smear_accuracy.Hide()
        self.smear_data_left.Hide()
        self.smear_data_right.Hide()
        self.smear_description_pin_min.Hide()
        self.smear_pinhole_min.Hide()
        self.smear_description_pin_max.Hide()
        self.smear_pinhole_max.Hide()
        self.smear_description_slit_height.Hide()
        self.smear_slit_height.Hide()
        self.smear_description_slit_width.Hide()
        self.smear_slit_width.Hide()
        self.smear_message_new_p.Hide()
        self.smear_message_new_s.Hide()
    
    def _set_accuracy_list(self):
        """
        Set the list of an accuracy in 2D custum smear: Xhigh, High, Med, or Low
        """
        # list of accuracy choices
        list = ['Low','Med','High','Xhigh']
        for idx in range(len(list)):
            self.smear_accuracy.Append(list[idx],idx)
            
    def _set_fun_box_list(self,fun_box):
        """
        Set the list of func for multifunctional models
        """
        # Check if it is multi_functional model
        if self.model.__class__ not in self.model_list_box["Multi-Functions"] \
                and not self.temp_multi_functional:
            return None
        # Get the func name list
        list = self.model.fun_list
        if len(list) == 0:
            return None
        # build function (combo)box
        ind = 0
        while(ind < len(list)):
            for key, val in list.iteritems():
                if (val == ind):
                    fun_box.Append(key,val)
                    break
            ind += 1
        
    def _on_select_accuracy(self,event):
        """
        Select an accuracy in 2D custom smear: Xhigh, High, Med, or Low
        """
        #event.Skip()
        # Check if the accuracy is same as before
        #self.smear2d_accuracy = event.GetEventObject().GetValue()
        self.smear2d_accuracy = self.smear_accuracy.GetValue()
        if self.pinhole_smearer.GetValue():
            self.onPinholeSmear(event=None)
        else:    
            self.onSmear(event=None)
            if self.current_smearer != None:
                self.current_smearer.set_accuracy(accuracy = 
                                                  self.smear2d_accuracy) 
        event.Skip()

    def _on_fun_box(self,event):
        """
        Select an func: Erf,Rparabola,LParabola
        """
        fun_val = None
        fun_box = event.GetEventObject()
        name = fun_box.Name
        value = fun_box.GetValue()
        if self.model.fun_list.has_key(value):
            fun_val = self.model.fun_list[value]

        self.model.setParam(name,fun_val)
        # save state
        self._copy_parameters_state(self.str_parameters, 
                                    self.state.str_parameters)
        # update params
        self._update_paramv_on_fit() 
        # draw
        self._draw_model()
        self.Refresh()
        # get ready for new event
        event.Skip()
        
    def _onMask(self, event):     
        """
        Build a panel to allow to edit Mask
        """
        
        from sans.guiframe.local_perspectives.plotting.masking \
        import MaskPanel as MaskDialog
        
        self.panel = MaskDialog(base=self, data=self.data, id=wx.NewId())
        #self.panel.Bind(wx.EVT_CLOSE, self._draw_masked_model)
        self.panel.ShowModal()
        #wx.PostEvent(self.parent, event)
        
    def _draw_masked_model(self, event):
        """
        Draw model image w/mask
        """
        #event.Skip()
        is_valid_qrange = self._update_paramv_on_fit()

        if is_valid_qrange and self.model != None:
            #self.panel.Show(0)
            #self.panel.Destroy() # frame
            self.panel.MakeModal(False)
            event.Skip() 
            # try re draw the model plot if it exists
            self._draw_model()
            self.set_npts2fit()
        elif self.model == None:
            #self.panel.Show(0)
            #self.panel.Destroy() # frame
            self.panel.MakeModal(False)
            event.Skip()
            self.set_npts2fit()
            msg= "No model is found on updating MASK in the model plot... "
            wx.PostEvent(self.parent.parent, StatusEvent(status = msg ))
        else:
            event.Skip()
            msg = ' Please consider your Q range, too.'
            self.panel.ShowMessage(msg)

        
    def _set_smear(self, data):
        """
        """
        if data is None:
            return
        self.smearer = smear_selection(data, self.model)
        self.disable_smearer.SetValue(True)
        if self.smearer == None:
            self.enable_smearer.Disable()
        else:
            self.enable_smearer.Enable()

    def _mac_sleep(self, sec=0.2):
        """
        Give sleep to MAC
        """
        if self.is_mac:
            time.sleep(sec)

    def get_view_mode(self):
        """
        return True if the panel allow 2D or False if 1D
        """
        return self.enable2D
    
    def compute_data_set_range(self, data):
        """
        find the range that include all data  in the set
        return the minimum and the maximum values
        """
        if data is not None:
            qmin, qmax, npts = self.compute_data_range(data)
            self.qmin_data_set = min(self.qmin_data_set, qmin)
            self.qmax_data_set = max(self.qmax_data_set, qmax)
            self.npts_data_set += npts
        
    def compute_data_range(self, data):
        """
        compute the minimum and the maximum range of the data
        return the npts contains in data
        :param data:
        """
        qmin, qmax, npts = None, None, None
        if data is not None:
            if not hasattr(data,"data"):
                qmin = min(data.x)
                # Maximum value of data  
                qmax = max(data.x)
                npts = len(data.x)
            else:
                qmin = 0
                x = max(math.fabs(data.xmin), math.fabs(data.xmax)) 
                y = max(math.fabs(data.ymin), math.fabs(data.ymax))
                ## Maximum value of data  
                qmax = math.sqrt(x*x + y*y)
                npts = len(data.data)
        print "compute single data range", qmin, qmax
        return qmin, qmax, npts
            
    
    def set_data(self, data):
        """
        reset the current data 
        """
        id = None
        group_id = None
        flag = False
        if self.data is None and data is not None:
            flag = True
        if data is not None:
            id = data.id
            group_id = data.group_id
            if self.data is not None:
                flag = (data.id != self.data.id)
        self.data = data
        if self.data is None:
            data_min = ""
            data_max = ""
            data_name = ""
            self._set_bookmark_flag(False)
            self._keep.Enable(False)
            self._set_save_flag(False)
        else:
            if self.model != None:
                self._set_bookmark_flag(True)
                self._keep.Enable(True)
            self._set_save_flag(True)
            self._set_preview_flag(True)

            self._set_smear(data)
            # more disables for 2D
            if self.data.__class__.__name__ ==  "Data2D" or \
                        self.enable2D:
                self.slit_smearer.Disable()
                self.pinhole_smearer.Enable(True) 
                self.default_mask = copy.deepcopy(self.data.mask)
            else:
                self.slit_smearer.Enable(True) 
                self.pinhole_smearer.Enable(True)      
                
            self.formfactorbox.Enable()
            self.structurebox.Enable()
            data_name = self.data.name
            #data_min, data_max, npts = self.compute_data_range(self.data)
            data_min, data_max = self.qmin_data_set, self.qmax_data_set
            npts =  self.npts_data_set
            #set maximum range for x in linear scale
            if not hasattr(self.data,"data"): #Display only for 1D data fit
                self.btEditMask.Disable()  
                self.EditMask_title.Disable()
            else:
                
                self.btEditMask.Enable()  
                self.EditMask_title.Enable() 
        self.Npts_total.SetValue(str(npts))
        #default:number of data points selected to fit
        self.Npts_fit.SetValue(str(npts))
        self.Npts_total.SetEditable(False)
        self.Npts_total.SetBackgroundColour(\
                                    self.GetParent().GetBackgroundColour())
        
        self.Npts_total.Bind(wx.EVT_MOUSE_EVENTS, self._npts_click)
        #self.Npts_total.Disable()
        self.dataSource.SetValue(data_name)
        self.qmin_x = data_min
        self.qmax_x = data_max
        #self.minimum_q.SetValue(str(data_min))
        #self.maximum_q.SetValue(str(data_max))
        if data_min is None:
            data_min = ""
        if data_max is None:
            data_max = ""
        self.qmin.SetValue(str(data_min))
        self.qmax.SetValue(str(data_max))
        self.qmin.SetBackgroundColour("white")
        self.qmax.SetBackgroundColour("white")
        self.state.data = data
        self.state.qmin = self.qmin_x
        self.state.qmax = self.qmax_x
        
        #update model plot with new data information
        if flag:
            #set model view button
            if self.data.__class__.__name__ == "Data2D":
                self.enable2D = True
                self.model_view.SetLabel("2D Mode")
            else:
                self.enable2D = False
                self.model_view.SetLabel("1D Mode")
                
            self.model_view.Disable()
            
            #replace data plot on combo box selection
            #by removing the previous selected data
            wx.PostEvent(self._manager.parent, NewPlotEvent(action="remove",
                                                    group_id=group_id, id=id))
            #plot the current selected data
            wx.PostEvent(self._manager.parent, NewPlotEvent(plot=self.data, 
                                                title=str(self.data.title)))
            self._manager.store_data(uid=self.uid, data=data,
                                     data_list=self.data_list,
                                      caption=self.window_name)
            self._draw_model()
    
    def _npts_click(self, event):
        """
        Prevent further handling of the mouse event on Npts_total
        by not calling Skip().
        """ 
        pass
    
    def reset_page(self, state,first=False):
        """
        reset the state
        """
        self.reset_page_helper(state)
        #import sans.guiframe.gui_manager
        #evt = ModelEventbox(model=state.model)
        #wx.PostEvent(self.event_owner, evt)  
   
        if self.engine_type != None:
            self._manager._on_change_engine(engine=self.engine_type)

        self.select_param(event = None) 
        #Save state_fit
        self.save_current_state_fit()
        self._lay_out()
        self.Refresh()
        
    def get_range(self):
        """
        return the fitting range
        """
        return float(self.qmin_x) , float(self.qmax_x)
    
    def get_npts2fit(self):
        """
        return numbers of data points within qrange
        
        :Note: This is for Park where chi2 is not normalized by Npts of fit
        
        """
        if self.data is None:
            return
        npts2fit = 0
        qmin,qmax = self.get_range()
        if self.data.__class__.__name__ == "Data2D" or \
                        self.enable2D:
            radius= numpy.sqrt( self.data.qx_data*self.data.qx_data + 
                                self.data.qy_data*self.data.qy_data )
            index_data = (self.qmin_x <= radius)&(radius<= self.qmax_x)
            index_data= (index_data)&(self.data.mask)
            index_data = (index_data)&(numpy.isfinite(self.data.data))
            npts2fit = len(self.data.data[index_data])
        else:
            for qx in self.data.x:
                   if qx >= qmin and qx <= qmax:
                       npts2fit += 1
        return npts2fit

    def set_npts2fit(self):
        """
        setValue Npts for fitting 
        """
        self.Npts_fit.SetValue(str(self.get_npts2fit()))
        
    def get_chi2(self):
        """
        return the current chi2
        """
        return self.tcChi.GetValue()
        
    def get_param_list(self):
        """
        :return self.param_toFit: list containing  references to TextCtrl
            checked.Theses TextCtrl will allow reference to parameters to fit.
        
        :raise: if return an empty list of parameter fit will nnote work 
            properly so raise ValueError,"missing parameter to fit"
        """
        if self.param_toFit !=[]:
            return self.param_toFit
        else:
            msg = "missing parameters to fit"  
            wx.MessageBox(msg, 'warning')
            return False
            #raise ValueError,"missing parameters to fit"    
      
    def onsetValues(self, chisqr, p_name, out, cov):
        """
        Build the panel from the fit result
        
        :param chisqr: Value of the goodness of fit metric
        :param p_name: the name of parameters
        :param out: list of parameter with the best value found during fitting
        :param cov: Covariance matrix
   
        """
        if out == None or not numpy.isfinite(chisqr):
            raise ValueError,"Fit error occured..." 
        
        is_modified = False
        has_error = False 
        dispersity = ''   
        
        #Hide textctrl boxes of errors.
        self._clear_Err_on_Fit()    
        
        #Check if chi2 is finite
        if chisqr != None and numpy.isfinite(chisqr):
        #format chi2  
            if self.engine_type == "park":  
                npt_fit = float(self.get_npts2fit()) 
                if npt_fit > 0:
                    chisqr =chisqr/npt_fit    
            chi2 = format_number(chisqr, True)    
            self.tcChi.SetValue(chi2)    
            self.tcChi.Refresh()    
        else:
            self.tcChi.SetValue("-")
        
        #Hide error title
        if self.text2_3.IsShown() and not self.is_mac:
            self.text2_3.Hide()
      
        try:
            if self.enable_disp.GetValue():
                if hasattr(self,"text_disp_1" ):
                    if self.text_disp_1 != None and not self.is_mac:
                        self.text_disp_1.Hide()
        except:
            dispersity = None
            pass
        #set the panel when fit result are float not list
        if out.__class__== numpy.float64:
            self.param_toFit[0][2].SetValue(format_number(out, True))
            
            if self.param_toFit[0][4].IsShown and not self.is_mac:
                self.param_toFit[0][4].Hide()
            if cov !=None :
                self.text2_3.Show(True)
                try:
                    if self.enable_disp.GetValue():
                        if hasattr(self,"text_disp_1" ):
                            if self.text_disp_1 !=None:
                                self.text_disp_1.Show(True)
                except:
                    pass

                if cov[0]==None or  not numpy.isfinite(cov[0]): 
                    if self.param_toFit[0][3].IsShown and not self.is_mac:
                        self.param_toFit[0][3].Hide()
                else:                    
                    self.param_toFit[0][3].Show(True)               
                    self.param_toFit[0][4].Show(True)
                    self.param_toFit[0][4].SetValue(format_number(cov[0], True))
                    has_error = True
        else:

            i = 0
            #Set the panel when fit result are list
            for item in self.param_toFit:     
                if len(item)>5 and item != None:     
                    ## reset error value to initial state
                    if not self.is_mac:
                        item[3].Hide()
                        item[4].Hide()
                    
                    for ind in range(len(out)):
                        
                        if item[1] == p_name[ind]:
                            break        
                    if len(out)<=len(self.param_toFit) and out[ind] !=None:   
                        val_out = format_number(out[ind], True)                  
                        item[2].SetValue(val_out)


                    if(cov !=None):
                        
                        try:
                            if dispersity !=None:
                                if self.enable_disp.GetValue():
                                    if hasattr(self,"text_disp_1" ):
                                        if self.text_disp_1!=None:
                                            if not self.text_disp_1.IsShown()\
                                                and not self.is_mac:
                                                self.text_disp_1.Show(True)
                        except:
                            pass    
                   
                        if cov[ind]!=None :
                            if numpy.isfinite(float(cov[ind])):
                                val_err = format_number(cov[ind], True)
                                if not self.is_mac:
                                    item[3].Show(True)
                                    item[4].Show(True)
                                item[4].SetValue(val_err)
                                
                                has_error = True
                    i += 1         
        #Show error title when any errors displayed
        if has_error: 
            if not self.text2_3.IsShown():
                self.text2_3.Show(True)   
        ## save current state  
        self.save_current_state()          
        
        #self._lay_out() 
        if not self.is_mac:
            self.Layout() 
            self.Refresh() 
        self._mac_sleep(0.1)  
        #plot model ( when drawing, do not update chisqr value again)
        self._draw_model(update_chisqr=False)    
        #PostStatusEvent     
        #msg = "Fit completed!dddd "
        #wx.PostEvent(self._manager.parent, StatusEvent(status=msg))

    def onPinholeSmear(self, event):
        """
        Create a custom pinhole smear object that will change the way residuals
        are compute when fitting
        
        :Note: accuracy is given by strings'High','Med', 'Low' FOR 2d,
                     None for 1D
                     
        """

        #if self.check_invalid_panel():
        #    return
        if self.model ==None:
            self.disable_smearer.SetValue(True)
            msg="Please select a Model first..."
            wx.MessageBox(msg, 'Info')
            wx.PostEvent(self._manager.parent, StatusEvent(status=\
                            "Smear: %s"%msg))
            return

        # Need update param values
        self._update_paramv_on_fit()     

        # msg default
        msg = None
        if event != None:
            tcrtl= event.GetEventObject()
            # event case of radio button
            if tcrtl.GetValue()== True:
                self.dx_min = 0.0
                self.dx_max = 0.0
                is_new_pinhole = True
            else:
                is_new_pinhole = self._is_changed_pinhole()
        else:
            is_new_pinhole = True 
        # if any value is changed
        if is_new_pinhole:
            msg = self._set_pinhole_smear()
        # hide all silt sizer    
        self._hide_all_smear_info()
        
        ##Calculate chi2
        temp_smearer = self.current_smearer
        #self.compute_chisqr(smearer= temp_smearer)
            
        # show relevant slit sizers 
        self._show_smear_sizer()

        self.sizer_set_smearer.Layout()
        self.Layout()   
        
        if event != None: 
            event.Skip()                  
        #self._undo.Enable(True)
        self.save_current_state()
        event = PageInfoEvent(page = self)
        wx.PostEvent(self.parent, event)
        
    def _is_changed_pinhole(self):  
        """
        check if any of pinhole smear is changed
        
        :return: True or False
        
        """
        # get the values
        pin_min = self.smear_pinhole_min.GetValue()
        pin_max = self.smear_pinhole_max.GetValue()
                    
        # Check changes in slit width    
        try:
            dx_min = float(pin_min)
        except:
            return True
        if self.dx_min != dx_min:
            return True
        
        # Check changes in slit heigth
        try:
            dx_max = float(pin_max)
        except:
            return True
        if self.dx_max != dx_max:
            return True
        return False
    
    def _set_pinhole_smear(self):
        """
        Set custom pinhole smear
        
        :return: msg
        
        """
        # copy data
        data = copy.deepcopy(self.data)
        if self._is_2D():
            self.smear_type = 'Pinhole2d'
            len_data = len(data.data)
            data.dqx_data = numpy.zeros(len_data)
            data.dqy_data = numpy.zeros(len_data)
        else:
            self.smear_type = 'Pinhole'
            len_data = len(data.x)
            data.dx = numpy.zeros(len_data)
            data.dxl = None
            data.dxw = None
        msg = None
   
        get_pin_min = self.smear_pinhole_min
        get_pin_max = self.smear_pinhole_max        

        if not check_float(get_pin_min):
            get_pin_min.SetBackgroundColour("pink")
            msg= "Model Error:wrong value entered!!!"
        elif not check_float(get_pin_max ):
            get_pin_max.SetBackgroundColour("pink")
            msg= "Model Error:wrong value entered!!!"
        else:
            if len_data < 2: len_data = 2     
            self.dx_min = float(get_pin_min.GetValue())
            self.dx_max = float(get_pin_max.GetValue())
            if self.dx_min < 0:
                get_pin_min.SetBackgroundColour("pink")
                msg= "Model Error:This value can not be negative!!!"
            elif self.dx_max <0:
                get_pin_max.SetBackgroundColour("pink")
                msg= "Model Error:This value can not be negative!!!"
            elif self.dx_min != None and self.dx_max != None:   
                if self._is_2D():
                    data.dqx_data[data.dqx_data==0] = self.dx_min
                    data.dqy_data[data.dqy_data==0] = self.dx_max          
                elif self.dx_min == self.dx_max:
                    data.dx[data.dx==0] = self.dx_min
                else:
                    step = (self.dx_max - self.dx_min)/(len_data-1)    
                    data.dx = numpy.arange(self.dx_min,self.dx_max+step/1.1,
                                           step)            
            elif self.dx_min != None: 
                if self._is_2D(): data.dqx_data[data.dqx_data==0] = self.dx_min
                else: data.dx[data.dx==0] = self.dx_min 
            elif self.dx_max != None:
                if self._is_2D(): data.dqy_data[data.dqy_data==0] = self.dx_max
                else: data.dx[data.dx==0] = self.dx_max          
            self.current_smearer = smear_selection(data, self.model)
            # 2D need to set accuracy
            if self._is_2D(): 
                self.current_smearer.set_accuracy(accuracy = \
                                                  self.smear2d_accuracy)

        if msg != None:
            wx.PostEvent(self._manager.parent, StatusEvent(status = msg ))
        else:
            get_pin_min.SetBackgroundColour("white")
            get_pin_max.SetBackgroundColour("white")
        ## set smearing value whether or not the data contain the smearing info
        self._manager.set_smearer(smearer=self.current_smearer,
                                 enable2D=self.enable2D,
                                 qmin=float(self.qmin_x),
                                 qmax= float(self.qmax_x),
                                 uid=self.uid)
        return msg
        
    def update_pinhole_smear(self):
        """
        called by kill_focus on pinhole TextCntrl
        to update the changes 
        
        :return: False when wrong value was entered
        
        """
        # msg default
        msg = None
        # check if any value is changed
        if self._is_changed_pinhole():
            msg = self._set_pinhole_smear()           
        #self._undo.Enable(True)
        self.save_current_state()

        if msg != None:
            return False   
        else:
            return True
                     
    def onSlitSmear(self, event):
        """
        Create a custom slit smear object that will change the way residuals
        are compute when fitting
        """
 
        #if self.check_invalid_panel():
        #    return

        if self.model ==None:
            self.disable_smearer.SetValue(True)
            
            msg="Please select a Model first..."
            wx.MessageBox(msg, 'Info')
            wx.PostEvent(self._manager.parent, StatusEvent(status=\
                            "Smear: %s"%msg))
            return

        # Need update param values
        self._update_paramv_on_fit()

        # msg default
        msg = None
        # for event given
        if event != None:
            tcrtl= event.GetEventObject()
            # event case of radio button
            if tcrtl.GetValue():
                self.dxl = 0.0
                self.dxw = 0.0
                is_new_slit = True
            else:
                is_new_slit = self._is_changed_slit()
        else:
            is_new_slit = True 
        
        # if any value is changed
        if is_new_slit:
            msg = self._set_slit_smear()
            
        # hide all silt sizer
        self._hide_all_smear_info()        
        ##Calculate chi2
        #self.compute_chisqr(smearer= self.current_smearer)  
        # show relevant slit sizers       
        self._show_smear_sizer()
        self.sizer_set_smearer.Layout()
        self.Layout()

        if event != None:
            event.Skip()     
        #self._undo.Enable(True)
        self.save_current_state()
        event = PageInfoEvent(page = self)
        wx.PostEvent(self.parent, event)
        if msg != None:
            wx.PostEvent(self._manager.parent, StatusEvent(status = msg))

    def _is_changed_slit(self):  
        """
        check if any of slit lengths is changed
        
        :return: True or False
        
        """
        # get the values
        width = self.smear_slit_width.GetValue()
        height = self.smear_slit_height.GetValue()
        
        # check and change the box bg color if it was pink 
        #    but it should be white now
        # because this is the case that _set_slit_smear() will not handle
        if height.lstrip().rstrip()=="":
            self.smear_slit_height.SetBackgroundColour(wx.WHITE)
        if width.lstrip().rstrip()=="":
            self.smear_slit_width.SetBackgroundColour(wx.WHITE)
            
        # Check changes in slit width    
        if width == "": 
            dxw = 0.0
        else:
            try:
                dxw = float(width)
            except:
                return True
        if self.dxw != dxw:
            return True
        
        # Check changes in slit heigth
        if height == "": 
            dxl = 0.0
        else:
            try:
                dxl = float(height)
            except:
                return True
        if self.dxl != dxl:
            return True

        return False
    
    def _set_slit_smear(self):
        """
        Set custom slit smear
        
        :return: message to inform the user about the validity
            of the values entered for slit smear
        """
        if self.data.__class__.__name__ ==  "Data2D" or \
                        self.enable2D:
            return
        temp_smearer = None
        # make sure once more if it is smearer
        data = copy.deepcopy(self.data)
        data_len = len(data.x)
        data.dx = None
        data.dxl = None
        data.dxw = None
        msg = None
   
        try:
            self.dxl = float(self.smear_slit_height.GetValue())
            data.dxl = self.dxl* numpy.ones(data_len)
            self.smear_slit_height.SetBackgroundColour(wx.WHITE)
        except: 
            data.dxl = numpy.zeros(data_len)
            if self.smear_slit_height.GetValue().lstrip().rstrip()!="":
                self.smear_slit_height.SetBackgroundColour("pink")
                msg = "Wrong value entered... "  
            else:
                self.smear_slit_height.SetBackgroundColour(wx.WHITE)
        try:
            self.dxw = float(self.smear_slit_width.GetValue())
            self.smear_slit_width.SetBackgroundColour(wx.WHITE)
            data.dxw = self.dxw* numpy.ones(data_len)
        except: 
            data.dxw = numpy.zeros(data_len)
            if self.smear_slit_width.GetValue().lstrip().rstrip()!="":
                self.smear_slit_width.SetBackgroundColour("pink")
                msg = "Wrong Fit value entered... "
            else:
                self.smear_slit_width.SetBackgroundColour(wx.WHITE)
              
        self.current_smearer = smear_selection(data, self.model)
        #temp_smearer = self.current_smearer
        ## set smearing value whether or not the data contain the smearing info
        self._manager.set_smearer(smearer=self.current_smearer, 
                                 enable2D=self.enable2D,
                                 qmin=float(self.qmin_x), 
                                 qmax= float(self.qmax_x),
                                 uid=self.uid) 
        return msg
    
    def update_slit_smear(self):
        """
        called by kill_focus on pinhole TextCntrl
        to update the changes 
        
        :return: False when wrong value was entered
        
        """             
        # msg default
        msg = None
        # check if any value is changed
        if self._is_changed_slit():
            msg = self._set_slit_smear()           
        #self._undo.Enable(True)
        self.save_current_state()

        if msg != None:
            return False   
        else:
            return True
                            
    def onSmear(self, event):
        """
        Create a smear object that will change the way residuals
        are compute when fitting
        """
        if event != None: 
            event.Skip()    
        if self.data is None:
            return
        
        if self.model == None:
            self.disable_smearer.SetValue(True)
            msg="Please select a Model first..."
            wx.MessageBox(msg, 'Info')
            wx.PostEvent(self._manager.parent, StatusEvent(status=\
                            "Smear: %s"%msg))
            return
        
        # Need update param values
        self._update_paramv_on_fit()
        
        temp_smearer = None
        self._get_smear_info()
        
        #renew smear sizer
        if self.smear_type != None:
            self.smear_description_smear_type.SetValue(str(self.smear_type))
            self.smear_data_left.SetValue(str(self.dq_l))   
            self.smear_data_right.SetValue(str(self.dq_r))       

        self._hide_all_smear_info()
        
        data = copy.deepcopy(self.data)
        # make sure once more if it is smearer
        self.current_smearer = smear_selection(data, self.model)
        
        if self.enable_smearer.GetValue():
            if hasattr(self.data,"dxl"):
                
                msg= ": Resolution smearing parameters"
            if hasattr(self.data,"dxw"):
                msg= ": Slit smearing parameters"
            if self.smearer ==None:
                wx.PostEvent(self._manager.parent, StatusEvent(status=\
                            "Data contains no smearing information"))
            else:
                wx.PostEvent(self._manager.parent, StatusEvent(status=\
                            "Data contains smearing information"))

            #self.smear_description_dqdata.Show(True)
            self.smear_data_left.Show(True)
            self.smear_data_right.Show(True)
            temp_smearer= self.current_smearer
        elif self.disable_smearer.GetValue():
            self.smear_description_none.Show(True)
            
        self._show_smear_sizer()
        
        self.sizer_set_smearer.Layout()
        self.Layout()
        ## set smearing value whether or not the data contain the smearing info
        self._manager.set_smearer(uid=self.uid, smearer=temp_smearer,
                        enable2D=self.enable2D,
                        qmin= float(self.qmin_x),
                        qmax= float(self.qmax_x), draw=True) 
        
        self.state.enable_smearer=  self.enable_smearer.GetValue()
        self.state.disable_smearer=self.disable_smearer.GetValue()
        self.state.pinhole_smearer = self.pinhole_smearer.GetValue()
        self.state.slit_smearer = self.slit_smearer.GetValue()
      
    def on_complete_chisqr(self, event):  
        """
        print result chisqr 
        
        :event: activated by fitting/ complete after draw
        
        """
        try:
            if event == None:
                output= "-"
            elif not numpy.isfinite(event.output):
                output= "-"
            else:
                output = event.output
            self.tcChi.SetValue(str(format_number(output, True)))

            self.state.tcChi = self.tcChi.GetValue()
        except:
            pass  
            

    def select_all_param(self,event): 
        """
        set to true or false all checkBox given the main checkbox value cb1
        """            
        self.param_toFit=[]
        if  self.parameters !=[]:
            if  self.cb1.GetValue():
                for item in self.parameters:
                    ## for data2D select all to fit
                    if self.data.__class__.__name__==  "Data2D" or \
                            self.enable2D:
                        item[0].SetValue(True)
                        self.param_toFit.append(item )
                    else:
                        ## for 1D all parameters except orientation
                        if not item in self.orientation_params:
                            item[0].SetValue(True)
                            self.param_toFit.append(item )
                #if len(self.fittable_param)>0:
                for item in self.fittable_param:
                    if self.data.__class__.__name__== "Data2D" or \
                            self.enable2D:
                        item[0].SetValue(True)
                        self.param_toFit.append(item )
                        try:
                            if len(self.values[item[1]]) > 0:
                                item[0].SetValue(False)
                        except:
                            pass

                    else:
                        ## for 1D all parameters except orientation
                        if not item in self.orientation_params_disp:
                            item[0].SetValue(True)
                            self.param_toFit.append(item )
                            try:
                                if len(self.values[item[1]]) > 0:
                                    item[0].SetValue(False)
                            except:
                                pass

            else:
                for item in self.parameters:
                    item[0].SetValue(False)
                for item in self.fittable_param:
                    item[0].SetValue(False)
                self.param_toFit=[]
           
        self.save_current_state_fit()  
       
        if event !=None:
            #self._undo.Enable(True)
            ## post state to fit panel
            event = PageInfoEvent(page = self)
            wx.PostEvent(self.parent, event) 
     
    def select_param(self,event):
        """ 
        Select TextCtrl  checked for fitting purpose and stores them
        in  self.param_toFit=[] list
        """
        self.param_toFit=[]
        for item in self.parameters:
            #Skip t ifhe angle parameters if 1D data
            if self.data.__class__.__name__ != "Data2D" and\
                        not self.enable2D:
                if item in self.orientation_params:
                    continue
            #Select parameters to fit for list of primary parameters
            if item[0].GetValue():
                if not (item in self.param_toFit):
                    self.param_toFit.append(item )  
            else:
                #remove parameters from the fitting list
                if item in self.param_toFit:
                    self.param_toFit.remove(item)

        #Select parameters to fit for list of fittable parameters 
        #        with dispersion          
        for item in self.fittable_param:
            #Skip t ifhe angle parameters if 1D data
            if self.data.__class__.__name__ !=  "Data2D" and\
                        not self.enable2D:
                if item in self.orientation_params:
                    continue
            if item[0].GetValue():
                if not (item in self.param_toFit):
                    self.param_toFit.append(item)  
            else:
                #remove parameters from the fitting list
                if item in self.param_toFit:
                    self.param_toFit.remove(item)

        #Calculate num. of angle parameters 
        if self.data.__class__.__name__ ==  "Data2D" or \
                       self.enable2D:
            len_orient_para = 0
        else:
            len_orient_para = len(self.orientation_params)  #assume even len 
        #Total num. of angle parameters
        if len(self.fittable_param) > 0:
            len_orient_para *= 2
        #Set the value of checkbox that selected every checkbox or not            
        if len(self.parameters)+len(self.fittable_param)-len_orient_para ==\
                len(self.param_toFit):
            self.cb1.SetValue(True)
        else:
            self.cb1.SetValue(False)
        self.save_current_state_fit()
        if event !=None:
            #self._undo.Enable(True)
            ## post state to fit panel
            event = PageInfoEvent(page = self)
            wx.PostEvent(self.parent, event) 
    
    def set_model_param_sizer(self, model):
        """
        Build the panel from the model content
        
        :param model: the model selected in combo box for fitting purpose
        
        """
        self.sizer3.Clear(True)
        self.parameters = []
        self.str_parameters = []
        self.param_toFit=[]
        self.fittable_param=[]
        self.fixed_param=[]
        self.orientation_params=[]
        self.orientation_params_disp=[]
        
        if model ==None:
            self.sizer3.Layout()
            self.SetupScrolling()
            return
        ## the panel is drawn using the current value of the fit engine
        if self.engine_type==None and self._manager !=None:
            self.engine_type= self._manager._return_engine_type()

        box_description= wx.StaticBox(self, -1,str("Model Parameters"))
        boxsizer1 = wx.StaticBoxSizer(box_description, wx.VERTICAL)
        sizer = wx.GridBagSizer(5,5)
        ## save the current model
        self.model = model
           
        keys = self.model.getParamList()
        #list of dispersion paramaters
        self.disp_list=self.model.getDispParamList()

        def custom_compare(a,b):
            """
            Custom compare to order, first by alphabets then second by number.
            """ 
            # number at the last digit
            a_last = a[len(a)-1]
            b_last = b[len(b)-1]
            # default
            num_a = None
            num_b = None
            # split the names
            a2 = a.lower().split('_')
            b2 = b.lower().split('_')
            # check length of a2, b2
            len_a2 = len(a2)
            len_b2 = len(b2)
            # check if it contains a int number(<10)
            try: 
                num_a = int(a_last)
            except: pass
            try:
                num_b = int(b_last)
            except: pass
            # Put 'scale' near the top; happens 
            # when numbered param name exists
            if a == 'scale':
                return -1
            # both have a number    
            if num_a != None and num_b != None:
                if num_a > num_b: return -1
                # same number
                elif num_a == num_b: 
                    # different last names
                    if a2[len_a2-1] != b2[len_b2-1] and num_a != 0:
                        return -cmp(a2[len_a2-1], b2[len_b2-1])
                    else: 
                        return cmp(a, b) 
                else: return 1
            # one of them has a number
            elif num_a != None: return 1
            elif num_b != None: return -1
            # no numbers
            else: return cmp(a.lower(), b.lower())

                        
        keys.sort(custom_compare)
    
        iy = 0
        ix = 0
        select_text = "Select All"
        self.cb1 = wx.CheckBox(self, -1,str(select_text), (10, 10))
        wx.EVT_CHECKBOX(self, self.cb1.GetId(), self.select_all_param)
        self.cb1.SetToolTipString("To check/uncheck all the boxes below.")
        self.cb1.SetValue(True)
        
        sizer.Add(self.cb1,(iy, ix),(1,1),\
                             wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
        ix +=1
        self.text2_2 = wx.StaticText(self, -1, 'Value')
        sizer.Add(self.text2_2,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix +=2 
        self.text2_3 = wx.StaticText(self, -1, 'Error')
        sizer.Add(self.text2_3,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        if not self.is_mac:
            self.text2_3.Hide()
        ix +=1 
        self.text2_min = wx.StaticText(self, -1, 'Min')
        sizer.Add(self.text2_min,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        #self.text2_min.Hide()
        ix +=1 
        self.text2_max = wx.StaticText(self, -1, 'Max')
        sizer.Add(self.text2_max,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        #self.text2_max.Hide()
        ix += 1
        self.text2_4 = wx.StaticText(self, -1, '[Units]')
        sizer.Add(self.text2_4,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        self.text2_4.Hide()
        
        for item in keys:
            if not item in self.disp_list and not item in \
                    self.model.orientation_params:
                
                ##prepare a spot to store errors
                if not self.model.details.has_key(item):
                    self.model.details [item] = ["",None,None] 
         
                iy += 1
                ix = 0
                if (self.model.__class__ in \
                    self.model_list_box["Multi-Functions"] or \
                    self.temp_multi_functional)\
                    and (item in self.model.non_fittable):
                    non_fittable_name = wx.StaticText(self, -1, item )
                    sizer.Add(non_fittable_name,(iy, ix),(1,1),\
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 21)
                    ## add parameter value
                    ix += 1
                    value= self.model.getParam(item)
                    if len(self.model.fun_list) > 0:
                        num = item.split('_')[1][5:7]
                        fun_box = wx.ComboBox(self, -1,size=(100,-1),
                                    style=wx.CB_READONLY, name = '%s'% item)
                        self._set_fun_box_list(fun_box)
                        fun_box.SetSelection(0)
                        #self.fun_box.SetToolTipString("A function 
                        #    describing the interface")
                        wx.EVT_COMBOBOX(fun_box,-1, self._on_fun_box)
                    else:
                        fun_box = self.ModelTextCtrl(self, -1, 
                                                     size=(_BOX_WIDTH,20),
                                style=wx.TE_PROCESS_ENTER, name ='%s'% item)
                        fun_box.SetToolTipString("Hit 'Enter' after typing.")
                        fun_box.SetValue(format_number(value, True))
                    sizer.Add(fun_box, (iy,ix),(1,1), wx.EXPAND)
                    self.str_parameters.append([None,item, fun_box,
                                                None, None, None, 
                                                None, None])

                    
                else:
                    ## add parameters name with checkbox for selecting to fit
                    cb = wx.CheckBox(self, -1, item )              
                    cb.SetToolTipString(" Check mark to fit.")
                    #cb.SetValue(True)
                    wx.EVT_CHECKBOX(self, cb.GetId(), self.select_param)
                    
                    sizer.Add( cb,( iy, ix),(1,1),
                                 wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 5)

                    ## add parameter value
                    ix += 1
                    value= self.model.getParam(item)
                    ctl1 = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH,20),
                                        style=wx.TE_PROCESS_ENTER)
                    ctl1.SetToolTipString("Hit 'Enter' after typing.")
                    ctl1.SetValue(format_number(value, True))
                    sizer.Add(ctl1, (iy,ix),(1,1), wx.EXPAND)
                    ## text to show error sign
                    ix += 1
                    text2=wx.StaticText(self, -1, '+/-')
                    sizer.Add(text2,(iy, ix),(1,1),\
                                    wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
                    if not self.is_mac:
                        text2.Hide() 
                    ix += 1
                    ctl2 = wx.TextCtrl(self, -1, size=(_BOX_WIDTH/1.2,20), style=0)
                    sizer.Add(ctl2, (iy,ix),(1,1), 
                              wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                    if not self.is_mac:
                        ctl2.Hide()
                    
                    ix += 1
                    ctl3 = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH/1.9,20),
                                               style=wx.TE_PROCESS_ENTER,
                                text_enter_callback = self._onparamRangeEnter)
         
                    sizer.Add(ctl3, (iy,ix),(1,1), 
                              wx.EXPAND|wx.ADJUST_MINSIZE, 0)
            
                    ix += 1
                    ctl4 = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH/1.9,20),
                                               style=wx.TE_PROCESS_ENTER,
                                text_enter_callback = self._onparamRangeEnter)
                    sizer.Add(ctl4, (iy,ix),(1,1), 
                              wx.EXPAND|wx.FIXED_MINSIZE, 0)
    
                    ix +=1
                    # Units
                    if self.model.details.has_key(item):
                        units = wx.StaticText(self, -1, 
                            self.model.details[item][0], style=wx.ALIGN_LEFT)
                    else:
                        units = wx.StaticText(self, -1, "", style=wx.ALIGN_LEFT)
                    sizer.Add(units, (iy,ix),(1,1), 
                               wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                        
                    ##[cb state, name, value, "+/-", error of fit, min, max , units]
                    self.parameters.append([cb,item, ctl1,
                                            text2,ctl2, ctl3, ctl4,units])
                                  
        iy+=1
        sizer.Add((10,10),(iy,ix),(1,1), 
                  wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        
        # type can be either Guassian or Array
        if len(self.model.dispersion.values())>0:
            type= self.model.dispersion.values()[0]["type"]
        else:
            type = "Gaussian"
            
        iy += 1
        ix = 0
        #Add tile for orientational angle
        for item in keys:
            if item in self.model.orientation_params:       
                orient_angle = wx.StaticText(self, -1, '[For 2D only]:')
                sizer.Add(orient_angle,(iy, ix),(1,1), 
                          wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15) 
                if not self.data.__class__.__name__ == "Data2D" and \
                        not self.enable2D:
                    orient_angle.Hide()
                else:
                    orient_angle.Show(True)
                break
      
        #For Gaussian only
        if type.lower() != "array":
            for item in self.model.orientation_params:
                if not item in self.disp_list:
                    ##prepare a spot to store min max
                    if not self.model.details.has_key(item):
                        self.model.details [item] = ["",None,None] 
                          
                    iy += 1
                    ix = 0
                    ## add parameters name with checkbox for selecting to fit
                    cb = wx.CheckBox(self, -1, item )
                    cb.SetValue(False)
                    cb.SetToolTipString("Check mark to fit")
                    wx.EVT_CHECKBOX(self, cb.GetId(), self.select_param)
                    if self.data.__class__.__name__ == "Data2D" or \
                            self.enable2D:
                        cb.Show(True)
                    else:
                        cb.Hide()
                    sizer.Add( cb,( iy, ix),(1,1),
                                 wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 5)
    
                    ## add parameter value
                    ix += 1
                    value= self.model.getParam(item)
                    ctl1 = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH,20),
                                        style=wx.TE_PROCESS_ENTER)
                    ctl1.SetToolTipString("Hit 'Enter' after typing.")
                    ctl1.SetValue(format_number(value, True))
                    if self.data.__class__.__name__ == "Data2D" or \
                            self.enable2D:
                        ctl1.Show(True)
                    else:
                        ctl1.Hide()
                    sizer.Add(ctl1, (iy,ix),(1,1), wx.EXPAND)
                    ## text to show error sign
                    ix += 1
                    text2=wx.StaticText(self, -1, '+/-')
                    sizer.Add(text2,(iy, ix),(1,1),\
                                    wx.EXPAND|wx.ADJUST_MINSIZE, 0) 

                    text2.Hide() 
                    ix += 1
                    ctl2 = wx.TextCtrl(self, -1, size=(_BOX_WIDTH/1.2,20), style=0)
                    sizer.Add(ctl2, (iy,ix),(1,1), 
                              wx.EXPAND|wx.ADJUST_MINSIZE, 0)

                    ctl2.Hide()
                    
                    
                    ix += 1
                    ctl3 = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH/1.8,20), 
                                              style=wx.TE_PROCESS_ENTER,
                                text_enter_callback = self._onparamRangeEnter)
                    
                    sizer.Add(ctl3, (iy,ix),(1,1), 
                              wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                    ctl3.Hide()
                 
                    ix += 1
                    ctl4 = self.ModelTextCtrl(self, -1, size=(_BOX_WIDTH/1.8,20),
                                               style=wx.TE_PROCESS_ENTER,
                            text_enter_callback = self._onparamRangeEnter)
                    sizer.Add(ctl4, (iy,ix),(1,1), 
                              wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                   
                    ctl4.Hide()
                    
                    if self.data.__class__.__name__ == "Data2D" or \
                            self.enable2D:  
                        if self.is_mac:  
                            text2.Show(True)
                            ctl2.Show(True)                 
                        ctl3.Show(True)
                        ctl4.Show(True)
                    
                    ix +=1
                    # Units
                    if self.model.details.has_key(item):
                        units = wx.StaticText(self, -1, 
                                              self.model.details[item][0], 
                                              style=wx.ALIGN_LEFT)
                    else:
                        units = wx.StaticText(self, -1, "", style=wx.ALIGN_LEFT)
                    if self.data.__class__.__name__ == "Data2D" or \
                            self.enable2D:
                        units.Show(True)
                    
                    else:
                        units.Hide()
                    
                    sizer.Add(units, (iy,ix),(1,1),  
                              wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                                          
                    ##[cb state, name, value, "+/-", error of fit,min,max,units]
                    self.parameters.append([cb,item, ctl1,
                                            text2,ctl2, ctl3, ctl4,units])
                    self.orientation_params.append([cb,item, ctl1,
                                            text2,ctl2, ctl3, ctl4,units])
              
        iy+=1
        
        #Display units text on panel
        for item in keys:   
            if self.model.details.has_key(item):
                self.text2_4.Show()
        #Fill the list of fittable parameters
        self.select_all_param(event=None)

        self.save_current_state_fit()
        boxsizer1.Add(sizer)
        self.sizer3.Add(boxsizer1,0, wx.EXPAND | wx.ALL, 10)
        self.sizer3.Layout()
        self.Layout()
        #self.Refresh()

    def on_right_down(self, event):
        """
        Get key stroke event
        """
        if self.data == None:
            return
        # Figuring out key combo: Cmd for copy, Alt for paste
        if event.AltDown() and event.ShiftDown():
            self._manager.show_ftol_dialog()
            flag = True
        elif event.AltDown() or event.ShiftDown():
            flag = False
        else:
            return
        # make event free
        event.Skip()
        # messages depending on the flag
        if not flag:
            msg = " Could not open ftol dialog;"
            msg += " Check if the Scipy fit engine is selected in the menubar."
            infor = 'warning'
            # inform msg to wx
            wx.PostEvent( self.parent.parent, 
                          StatusEvent(status= msg, info=infor))

        
    def _onModel2D(self, event):
        """
        toggle view of model from 1D to 2D  or 2D from 1D
        """
        if self.model_view.GetLabelText() == "1D Mode":
            self.model_view.SetLabel("2D Mode")
            self.enable2D = True
              
        else:
            self.model_view.SetLabel("1D Mode")
            self.enable2D = False

        self.set_model_param_sizer(self.model)
        self._set_sizer_dispersion()  
        self._draw_model()
        
        
        self.state.enable2D =  copy.deepcopy(self.enable2D)
        
class BGTextCtrl(wx.TextCtrl):
    """
    Text control used to display outputs.
    No editing allowed. The background is 
    grayed out. User can't select text.
    """
    def __init__(self, *args, **kwds):
        wx.TextCtrl.__init__(self, *args, **kwds)
        self.SetEditable(False)
        self.SetBackgroundColour(self.GetParent().parent.GetBackgroundColour())
        
        # Bind to mouse event to avoid text highlighting
        # The event will be skipped once the call-back
        # is called.
        self.Bind(wx.EVT_MOUSE_EVENTS, self._click)
        
    def _click(self, event):
        """
        Prevent further handling of the mouse event
        by not calling Skip().
        """ 
        pass
 
