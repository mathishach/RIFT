from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class Christensen_Plugin_plugin(AFXForm):

    [
        ID_1,
    ] = range(AFXForm.ID_LAST, AFXForm.ID_LAST + 1)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        # AFXForm
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='outerMethod',
            objectName='Christensen_Plugin_Backend', registerQuery=False)
        pickedDefault = ''
        self.odbKw = AFXStringKeyword(self.cmd, 'odb_name', True, '')
        self.Steps_Keywords = []
        for i in range(10): # preset amount of steps
            self.Steps_Keywords.append(AFXBoolKeyword(self.cmd, 'step'+ str(i), AFXBoolKeyword.TRUE_FALSE, True, False))
        
        self.instance_nameKw = AFXStringKeyword(self.cmd, 'instance_name', True)

        FXMAPFUNC(self, SEL_COMMAND, self.ID_1,
                  Christensen_Plugin_plugin.getNextDialog)

        self.materials_Keyword = AFXTableKeyword(self.cmd, 'material_entries', True, 0, -1)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import christensen_PluginDB
        print('Test get first dialog')
        self.dialog1 = christensen_PluginDB.FailureIndex1(self)
        return self.dialog1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getNextDialog(self, previousDb):
        
        if previousDb == self.dialog1:
            import christensen_PluginDB
            
            odbname = self.odbKw.getValue()
            openOdbCommand = "odb = Christensen_Plugin_Backend.openOdb('" + odbname + "')"
            try:
                sendCommand(openOdbCommand)
                
            except:
                print 'Something went wrong with opening the odb.'
            
            dialog2 = christensen_PluginDB.FailureIndex2(self, odbname)
            
            return dialog2
        
        
        else:
            return None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):

        # Try to set the appropriate radio button on. If the user did
        # not specify any buttons to be on, do nothing.
        #
        for kw1,kw2,d in self.radioButtonGroups.values():
            try:
                value = d[kw1.getValue()]
                kw2.setValue(value)
            except:
                pass
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Register the plug-in
#
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


# needed to show the plugin in the Abaqus GUI
toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Christensen Plugin', 
    object=Christensen_Plugin_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import Christensen_Plugin_Backend',
    applicableModules=ALL,
    version='1.0',
    author='Mathis Hach',
    description='This Plugin allows the User to calculate the Failure Index in an .odb File according to the Christensen Failure Criterion',
    helpUrl='https://www.cld.uni-rostock.de'
)
