"""
    Application settings
"""
import time
import os
from sas.guiframe.gui_style import GUIFRAME
import sas.sasview
import logging

# Version of the application
__appname__ = "SasView"
__version__ = sas.sasview.__version__
__build__ = sas.sasview.__build__
__download_page__ = 'http://sourceforge.net/projects/sasview/files/'
__update_URL__ = ['svn.code.sf.net', 
                  '/p/sasview/code/trunk/sasview.latestversion']


# Debug message flag
__EVT_DEBUG__ = False

# Flag for automated testing
__TEST__ = False

# Debug message should be written to a file?
__EVT_DEBUG_2_FILE__   = False
__EVT_DEBUG_FILENAME__ = "debug.log"

# About box info
_do_aboutbox = True
_do_acknowledge = True
_do_tutorial = True
_acknowledgement_preamble =\
'''To ensure the long term support and development of this software please''' +\
''' remember to do the following.'''
_acknowledgement_preamble_bullet1 =\
'''Acknowledge its use in your publications as suggested below'''
_acknowledgement_preamble_bullet2 =\
'''Reference the following website: http://www.sasview.org'''
_acknowledgement_preamble_bullet3 =\
'''Send us your reference for our records: sansdanse@gmail.com'''
_acknowledgement_publications = \
'''This work benefited from the use of the SasView application, originally 
developed under NSF award DMR-0520547.
'''
_acknowledgement =  \
'''This work originally developed as part of the DANSE project funded by the NSF
under grant DMR-0520547, and currently maintained by NIST, UMD, ORNL, ISIS, ESS 
and ILL.

'''
_homepage = "http://www.sasview.org"
_download = __download_page__
_authors = []
_paper = "http://sourceforge.net/p/sasview/tickets/"
_license = "mailto:help@sasview.org"


icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "images"))
logging.info("icon path: %s" % icon_path)
media_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))
test_path =  os.path.abspath(os.path.join(os.path.dirname(__file__), "test"))

_nist_logo = os.path.join(icon_path, "nist_logo.png")
_umd_logo = os.path.join(icon_path, "umd_logo.png")
_sns_logo = os.path.join(icon_path, "sns_logo.png")
_isis_logo = os.path.join(icon_path, "isis_logo.png")
_ess_logo = os.path.join(icon_path, "ess_logo.png")
_ill_logo = os.path.join(icon_path, "ill_logo.png")
_nsf_logo = os.path.join(icon_path, "nsf_logo.png")
_danse_logo = os.path.join(icon_path, "danse_logo.png")
_inst_logo = os.path.join(icon_path, "utlogo.gif")
_nist_url = "http://www.nist.gov/"
_umd_url = "http://www.umd.edu/"
_sns_url = "http://neutrons.ornl.gov/"
_nsf_url = "http://www.nsf.gov"
_isis_url = "http://www.isis.stfc.ac.uk/"
_ess_url = "http://ess-scandinavia.eu/"
_ill_url = "http://www.ill.eu/"
_danse_url = "http://www.cacr.caltech.edu/projects/danse/release/index.html"
_inst_url = "http://www.utk.edu"
_corner_image = os.path.join(icon_path, "angles_flat.png")
_welcome_image = os.path.join(icon_path, "SVwelcome.png")
_copyright = "(c) 2009 - 2013, UTK, UMD, NIST, ORNL, ISIS, ESS and ILL"


#edit the list of file state your plugin can read
APPLICATION_WLIST = 'SasView files (*.svs)|*.svs'
APPLICATION_STATE_EXTENSION = '.svs'
GUIFRAME_WIDTH = 1150
GUIFRAME_HEIGHT = 840
PLUGIN_STATE_EXTENSIONS = ['.fitv', '.inv', '.prv']
PLUGINS_WLIST = ['Fitting files (*.fitv)|*.fitv',
                  'Invariant files (*.inv)|*.inv',
                  'P(r) files (*.prv)|*.prv']
PLOPANEL_WIDTH = 415
PLOPANEL_HEIGTH = 370
DATAPANEL_WIDTH = 235
DATAPANEL_HEIGHT = 700
SPLASH_SCREEN_PATH = os.path.join(icon_path,"SVwelcome_mini.png")
TUTORIAL_PATH = os.path.join(media_path,"Tutorial.pdf")
DEFAULT_STYLE = GUIFRAME.MULTIPLE_APPLICATIONS|GUIFRAME.MANAGER_ON\
                    |GUIFRAME.CALCULATOR_ON|GUIFRAME.TOOLBAR_ON
SPLASH_SCREEN_WIDTH = 512
SPLASH_SCREEN_HEIGHT = 366
SS_MAX_DISPLAY_TIME = 2000
WELCOME_PANEL_ON  = True
WELCOME_PANEL_SHOW = False
CLEANUP_PLOT = False
# OPEN and SAVE project menu
OPEN_SAVE_PROJECT_MENU = True
#VIEW MENU
VIEW_MENU = True
#EDIT MENU
EDIT_MENU = True

SetupIconFile_win = os.path.join(icon_path, "ball.ico")
SetupIconFile_mac = os.path.join(icon_path, "ball.icns")
DefaultGroupName = "."
OutputBaseFilename = "setupSasView"

FIXED_PANEL = True
DATALOADER_SHOW = True
CLEANUP_PLOT = False
WELCOME_PANEL_SHOW = False
#Show or hide toolbar at the start up
TOOLBAR_SHOW = True
# set a default perspective
DEFAULT_PERSPECTIVE = 'None'

def printEVT(message):
    if __EVT_DEBUG__:
        print "%g:  %s" % (time.clock(), message)
        
        if __EVT_DEBUG_2_FILE__:
            out = open(__EVT_DEBUG_FILENAME__, 'a')
            out.write("%10g:  %s\n" % (time.clock(), message))
            out.close()
            
