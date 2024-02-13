from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class FailureIndex1(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    [
        ID_1,
    ] = range(AFXDataDialog.ID_LAST, AFXDataDialog.ID_LAST + 1)

   
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'Generate Failure Index Field Output Object 1/2',
            self.CONTINUE|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        FXMAPFUNC(self, SEL_COMMAND, self.ID_1,
                  FailureIndex1.onClick)
        
        
        okBtn = self.getActionButton(self.ID_CLICKED_CONTINUE)
        okBtn.setText('Continue')
        
        fileHandler = FailureIndex_DBFileHandler(form, 'odb', '*.odb')

        fileTextHf = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        AFXTextField(p=fileTextHf, ncols=12, labelText='Chose the .odb-File you want to change :', tgt=form.odbKw, sel=0,
            opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL )
        FXButton(p=fileTextHf, text='	Select File\nFrom Dialog', ic=icon, tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)
        

    def onClick(self, sender, sel, ptr):
        
        return 1

###########################################################################
# Class definition
###########################################################################

class FailureIndex_DBFileHandler(FXObject):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*.odb'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.fileNameKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, FailureIndex_DBFileHandler.activate)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

       fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
           self.fileNameKw, self.readOnlyKw,
           AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
       fileDb.setReadOnlyPatterns('*.odb')
       fileDb.create()
       fileDb.showModal()


class FailureIndex2(AFXDataDialog):

    [
        ID_1,
    ] = range(AFXDataDialog.ID_LAST, AFXDataDialog.ID_LAST + 1)

   
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, odb_name):
        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'Generate Failure Index Field Output Object 2/2',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            
        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('Calculate Christensen Field Variable')

        # Instance Selection        
        ComboBox_2 = AFXComboBox(p=self, ncols=0, nvis=1, text='Choose Instance:', tgt=form.instance_nameKw) #, sel=0)
        ComboBox_2.setMaxVisible(10)
     
        instances = session.odbs[odb_name].rootAssembly.instances.keys()
        instances.sort()
        for instance in instances:
            ComboBox_2.appendItem(instance)

        # Step Selection
        self.stepLabel = FXLabel(p=self, text="Choose steps:")
        steps = session.odbs[odb_name].steps.keys()
        for i in range(len(steps)):
            FXCheckButton(p=self, text=steps[i], tgt=form.Steps_Keywords[i])

        # Material Parameters Definition
        self.materialLabel = FXLabel(p=self, text="Please fill out the table. If you dont want to calculate the failure index \n for a material, put in 0 as the tensile and compression strength.")
        materials = session.odbs[odb_name].materials.keys()
        amount_mat = len(materials)
        # Defines the Table
        matTable = AFXTable(p=self, numVisRows=6, numVisColumns=3, numRows=amount_mat+1, numColumns=3, tgt=form.materials_Keyword)
        matTable.showHorizontalGrid(True)
        matTable.showVerticalGrid(True)
        matTable.setColumnEditable(1,True)
        matTable.setColumnEditable(2,True)
        matTable.setLeadingColumns(1)        
        matTable.setLeadingRows(1)
        matTable.setLeadingRowLabels('Tensile Strength \t Compressive Strength')
        # matTable.setDefaultFloatValue(0.) # sets the default entry in the table to zero
        
        # For the starting column
        leadingColumnsString = ''
        for mat in materials:
            leadingColumnsString += mat + '\t'
        matTable.setLeadingColumnLabels(leadingColumnsString)

        
    def onClick(self, sender, sel, ptr):

        return 1