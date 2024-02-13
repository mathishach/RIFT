# -*- coding: mbcs -*-
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import numpy as np
from datetime import datetime

class Christensen_class:
    
    def __init__(self, entries_of_stress_tensor, T=100., C=300.):
        """
        Creates a new Christensen_class Object which can calculate the failure index according to Christensen
    
        Parameters:
        ---------------
            entries_of_stress_tensor: Array
                has to have 6 entries for threedimensional stress states 
    
            T: Float
                tensile strength of the material

            C: Float
                tensile strength of the material
        """
        self.T = T
        self.C = C

        if len(entries_of_stress_tensor) == 6:
            self.S11 = entries_of_stress_tensor[0]
            self.S22 = entries_of_stress_tensor[1]
            self.S33 = entries_of_stress_tensor[2]
            self.S12 = entries_of_stress_tensor[3]
            self.S13 = entries_of_stress_tensor[4]
            self.S23 = entries_of_stress_tensor[5]
        elif len(entries_of_stress_tensor) == 4:
            self.S11 = entries_of_stress_tensor[0]
            self.S22 = entries_of_stress_tensor[1]
            self.S33 = entries_of_stress_tensor[2]
            self.S12 = entries_of_stress_tensor[3]
            self.S13 = 0.
            self.S23 = 0.

    def calc_main(self):
        
        # 1. Calculation of the Principal Stresses
        self.calc_PC()
    
        # 2. Calculation of the polar coordinates
        self.calc_polar()

        # 3. Calculation of the two sub-criteria
        self.calc_rho_invariant_criterion()
        self.calc_fracture_criterion()
    
        # 4. calculation of the single failure index of the material
        self.calc_failure_index()

        self.calc_fn()

        return self.failure_index


    
    # 1. Calculation of the Principal Stresses
    def calc_PC(self):
        Stress_tens = np.array([(self.S11, self.S12, self.S13), (self.S12,self.S22,self.S23), (self.S13,self.S23,self.S33)])
        self.Principal_Stresses, eigenvec = np.linalg.eig(Stress_tens)


    # 2 Auxilary Method, calculates the polar coordinates in principal stress space
    def calc_polar(self):
        self.rho = np.sqrt(self.Principal_Stresses[0]**2 + self.Principal_Stresses[1]**2 + self.Principal_Stresses[2]**2)
        self.theta = np.arctan2(np.sqrt(self.Principal_Stresses[0]**2 + self.Principal_Stresses[1]**2), self.Principal_Stresses[2])
        self.phi = np.arctan2(self.Principal_Stresses[1], self.Principal_Stresses[0])
    
        self.sin_t = np.sin(self.theta)
        self.cos_t = np.cos(self.theta)
        self.sin_p = np.sin(self.phi)
        self.cos_p = np.cos(self.phi)



   # 3.1 Calculation of the Radius rho for the failure surface given the principal stresses and material strength
    def calc_rho_invariant_criterion(self):
        # Auxilary variables for the quadratic formula
        aux_a_1 = 1./(2.*self.T*self.C)
        aux_a_2 = ((self.sin_t * self.cos_p - self.sin_t * self.sin_p)**2 + (self.sin_t * self.cos_p - self.cos_t)**2 + (self.sin_t * self.sin_p - self.cos_t)**2)
        self.aux_a = 1./(2.*self.T*self.C) * ((self.sin_t * self.cos_p - self.sin_t * self.sin_p)**2 + (self.sin_t * self.cos_p - self.cos_t)**2 + (self.sin_t * self.sin_p - self.cos_t)**2)
        self.aux_b = (1./self.T-1/self.C) * (self.sin_t * self.sin_p + self.sin_t * self.cos_p + self.cos_t)
        self.aux_c = -1.

        if self.aux_a > 10**-20:   # if a is NOT extremely small, proceed with the usual 
            rho = [np.abs((-self.aux_b + np.sqrt(self.aux_b**2 - 4*self.aux_a*self.aux_c))) / (2*self.aux_a), np.abs((-self.aux_b - np.sqrt(self.aux_b**2 - 4*self.aux_a*self.aux_c)) / (2*self.aux_a))]
            if self.Principal_Stresses[0]+self.Principal_Stresses[1]+self.Principal_Stresses[2] > 0:
                self.rho_invariant_criterion = min(rho)
            else:
                self.rho_invariant_criterion = max(rho)
        
        # if a is extremely small -> hydrostatic stress situation
        else:
            # hydrostatic tension
            if sum(self.Principal_Stresses) > 0:
                # if T 0/= C
                if self.aux_b != 0:
                    self.rho_invariant_criterion = -self.aux_c/self.aux_b
                else:
                    self.rho_invariant_criterion = None 
            
            # hydrostatic compression
            else:
                self.rho_invariant_criterion = None # in the case of hydrostatic pressure, there is no failure
        
        return self.rho_invariant_criterion


    # 3.2
    def calc_fracture_criterion(self):
        self.max_ps = max(self.Principal_Stresses)
        return self.max_ps


    # 4 Calculation of the Failure Index
    def calc_failure_index(self):
        
        # If the stress situation is not one of hydrostostatic pressure or tension for von-Mises like materials
        if self.rho_invariant_criterion != None: 

            # If T/C is smaller then .5, the fracture criterion is relevant
            if self.T/self.C < 1/2:    
                self.failure_index = max(self.rho / self.rho_invariant_criterion, self.max_ps / self.T)
    
            # Otherwise, the fracture criterion is not relevant
            else:
                self.failure_index = self.rho/self.rho_invariant_criterion

        else:
            self.failure_index = float('NaN')


    # 5 Calculation of the Failure Number
    def calc_fn(self):
        principal_stresses_at_failure = [0., 0., 0.]
        principal_stresses_at_failure[0] = (self.rho / self.failure_index) * self.sin_t * self.cos_p    
        principal_stresses_at_failure[1] = (self.rho / self.failure_index) * self.sin_t * self.sin_p
        principal_stresses_at_failure[2] = (self.rho / self.failure_index) * self.cos_t
        
        self.Fn = 1./2. * (3*self.T/self.C-(sum(principal_stresses_at_failure)/self.C))
        if self.Fn > 1:
            self.Fn = 1
        elif self.Fn < 0:
            self.Fn = 0

# --------------------------------------------------------------------------------------------------------------------------------------

def create_Christensen_field_variable_multiple_materials(odb_name, instance_name, step_name, mat_dict):
    """
    Creates a new FieldOutput Object which includes the failure index of a given material according to Christensen
    
    Parameters:
    ---------------
        odb_name: String
            needed to open an Abaqus .odb file, depending on the working directory this also needs to include the path 
    
        instance_name: String
            name of the instance for which the new field variable will be implemented

        step_name: String
            name of the step for which the new field variable will be implemented

        mat_dict: Dictionary
            key: String
                name of the Material
            value: float-Array
                includes the tensile strength [0] and the compressive strength [1] of the material 
    """

    # 0. Definition of utility variables
    odb = openOdb(odb_name, readOnly=False)
    instance1 = odb.rootAssembly.instances[instance_name]
    elData = []
    lastFrame = odb.steps[step_name].frames[-1] 
    elLabels = [el.label for el in instance1.elements]
    stress = lastFrame.fieldOutputs['S']
    stresses_at_int_points = stress.getSubset(position=INTEGRATION_POINT, region=instance1)
    
    #  1. Instantiation of a new FieldOutput Object
    fieldVarName = setFieldVarName(lastFrame)    
    RIFT = lastFrame.FieldOutput(name=fieldVarName, description='This field shows the utilzation of the material according to the Christensen Failure Theory. A value of 1 indicates, that the material is on the edge of failure (plastic deformation or brittle rupture).', 
            type=VECTOR, componentLabels=['Failure Index', 'Failure Number', 'Equivalent Stress'])

    #  2. Defining the field variable for each element as NaN
    for el in instance1.elements:
        elData.append([float('NaN'), float('NaN'), float('NaN')]) 

    print('The calculation is running ...')
    counter = 0
   
    #  3. Iterate over the sectionAssignment objects of the given instance
    for sectasobj in instance1.sectionAssignments:
        
        #   4. Grab the ID of the section in the sectionAssignment object
        sect = odb.sections[sectasobj.sectionName]
        
        #  5. Grab the material of the section
        mat_name = sect.material

        #  6. if T and C values for the material are known 
        if mat_name in mat_dict:
            #  7. Get T and C from the material dictionary  
            T = mat_dict[mat_name][0]
            T = 1
            C = mat_dict[mat_name][1]
            C = 2
            #  8. Iterate over the elements in the SectionAssignment Object
            for el in sectasobj.region.elements: 
                #  9. Get stresses at the given element
                stress = stresses_at_int_points.values[el.label-1]
                #  10. Calculate the failure index of the element
                ChristensenInst = Christensen_class(stress.data, T, C)
                testf = ChristensenInst.calc_main()
                elData[counter][0] = ChristensenInst.calc_main()
                elData[counter][1] = ChristensenInst.Fn
                elData[counter][2] = elData[counter][0] * T
                counter +=1
    
    

    # 11. Add the data to the FieldOutput Object
    print('Trying to add the data ...')
    RIFT.addData(position=INTEGRATION_POINT, instance=instance1, labels=elLabels, data=elData)

    # Update the odb in the GUI
    odb.save()
    odb.close()
    odb = openOdb(odb_name, readOnly=False)
    print('The calculation is finished.')

#------------------------------------------------------------------------------------------------------------------------------------------- 

def create_Christensen_field_variable_multiple_materials_also_for_quadratic_elements(odb_name, instance_name, step_name, mat_dict={}):
    """
    Creates a new FieldOutput Object which includes the failure index of a given material according to Christensen
    
    Parameters:
    ---------------
        odb_name: String
            needed to open an Abaqus .odb file, depending on the working directory this also needs to include the path 
    
        instance_name: String
            name of the instance for which the new field variable will be implemented

        step_name: String AKTUELL ALS LIST
            name of the step for which the new field variable will be implemented

        Mat_dict: Dictionary
            key: String
                name of the Material
            value: float-Array
                includes the tensile strength [0] and the compressive strength [1] of the material 
    """

    # 0. Definition of utility variables
    odb = openOdb(odb_name, readOnly=False)
    instance1 = odb.rootAssembly.instances[instance_name]
    elData = []
    lastFrame = odb.steps[step_name].frames[-1] 
    elLabels = [el.label for el in instance1.elements]
    stress = lastFrame.fieldOutputs['S']
    stresses_at_int_points = stress.getSubset(position=INTEGRATION_POINT, region=instance1)
    
    
    #  1. Instantiation of a new FieldOutput Object
    fieldVarName = setFieldVarName(lastFrame)    
    RIFT = lastFrame.FieldOutput(name=fieldVarName, description='This field shows the utilzation of the material according to the Christensen Failure Theory. A value of 1 indicates, that the material is on the edge of failure (plastic deformation or brittle rupture).', 
            type=VECTOR , componentLabels=['Failure Index', 'Failure Number', 'Equivalent Stress'])

    #  2. Iterate over the stresses_at_int_points
    print('The calculation is running ...')
    for v in stresses_at_int_points.values:
        # 3-7.
        sectName = getSectionName(v.elementLabel, instance1)
        sect = odb.sections[sectName]
        # 8. Grab the Material of the section
        mat_name = sect.material
        # 9. 
        if mat_name in mat_dict:
            # 10.
            T = mat_dict[mat_name][0]
            C = mat_dict[mat_name][1]
            # 11.
            elData.append(calc_fail_ind(v.data, T, C))
        else:
            # 12.
            elData.append([float('NaN'), 0, 0])
   

    # 11. Add the data to the FieldOutput Object
    print('Trying to add the data ...')
    RIFT.addData(position=INTEGRATION_POINT, instance=instance1, labels=elLabels, data=elData)

    # update the odb in the GUI
    odb.save()
    odb.close()
    odb = openOdb(odb_name, readOnly=False)
    print('The calculation is finished.')

def getSectionName(label, instance):
    for secAsObj in instance.sectionAssignments:
        for elem in secAsObj.region.elements:
            if (elem.label == label):
                return secAsObj.sectionName


def calc_fail_ind(data, T=100., C=300.):
    ChristensenInst = Christensen_class(data, T, C)
    return [ChristensenInst.calc_main(), ChristensenInst.Fn, ChristensenInst.calc_main() * T]
    

# def addMaterial(matName, T, C):
#     if Mat_dict not in globals():
#         Mat_dict = {}
#     if isinstance(Mat_dict, dict):
#         Mat_dict[matName] = [T, C]
#     else:
#         Mat_dict = {matName, [T, C]}


def open_Odb(odbName):
    openOdb(odbName, readOnly=False)


# Auxiliary function to set the name of the field variable
def setFieldVarName(frame_obj):
    fieldVarName = "Christensen"
    i = 1
    while fieldVarName in frame_obj.fieldOutputs:
        fieldVarName = 'Christensen' + str(i)
        i += 1

    return fieldVarName


# def printChr(odb_name='kein ODB Name uebergeben', instance_name='kein Instance name uebergeben', material='kein Material uebergeben', step0=False, step1=False, step2=False, step3=False, step4=False, step5=False, step6=False, step7=False, step8=False, step9=False):
    
#     print('User Input:')
#     print('ODB', odb_name, type(odb_name))
#     print('Instance', instance_name, type(instance_name))
#     print('Material', material, type(material))
#     steplist = []
#     counter= 0
#     for step in step0, step1, step2, step3, step4, step5, step6, step7, step8, step9:
#         print(step)
#         counter +=1
#         if step:
#             steplist.append(counter)

#     print('Steps', steplist, type(steplist))



def outerMethod(odb_name='kein ODB Name uebergeben', instance_name='kein Instance name uebergeben', material_entries='kein Material uebergeben', step0=False, step1=False, step2=False, step3=False, step4=False, step5=False, step6=False, step7=False, step8=False, step9=False):
    print('User Input:')
    print('ODB', odb_name, type(odb_name))
    print('Instance', instance_name, type(instance_name))
    
    # Handling of the steps, (1) Change the single booleans in a list of numbers for the True booleans
    counter = 0 # (1)
    steplist = []
    for step in step0, step1, step2, step3, step4, step5, step6, step7, step8, step9:    
        if step:
            steplist.append(counter)
        counter +=1
    steps = session.odbs[odb_name].steps.keys()
    steplist_names = []
    counter = 0
    for step in steps:
        if counter in steplist:
            steplist_names.append(step)
        counter +=1

    print('Steps', steplist, type(steplist))
    print('Steps mit Namen', steplist_names, type(steplist_names))

    
    # Make a dictionary out of the materials
    mat_dict = {}
    material_names = session.odbs[odb_name].materials.keys()
    if len(material_entries) != len(material_names):
        raise ValueError('If you do not want to calculate the utility for a material, you have to put in 0 as the Tensile and Compressive Strength in the Table')
    else:
        for i in range(len(material_names)):
            if material_entries[i][0] != 0 or material_entries[i][1] != 0:
                if material_entries[i][0] < 0 or material_entries[i][1] < 0:
                    raise ValueError('Both the Tensile as well as the Compressive Strength cannot be lower than zero.')
                elif material_entries[i][0] > material_entries[i][1]:
                    raise ValueError('The Tensile Strength cannot be larger than the Compressive Strength.')
                else:
                    mat_dict[material_names[i]] = [float(material_entries[i][0]), float(material_entries[i][0])]
    
    print('Materialdict', mat_dict, type(mat_dict), type(mat_dict[material_names[0]]))

    instance1 = session.odbs[odb_name].rootAssembly.instances[instance_name]
    lastFrame = session.odbs[odb_name].steps[steplist_names[-1]].frames[-1] 
    amountElements = len(instance1.elements)

    stress = lastFrame.fieldOutputs['S']
    stresses_at_int_points = stress.getSubset(position=INTEGRATION_POINT, region=instance1)
    amountIntPoints = len(stresses_at_int_points.values)


    if amountElements == amountIntPoints:
        print('The function create_christensen_field_variable_multiple_materials is beeing used')
        for step in steplist_names:
            create_Christensen_field_variable_multiple_materials(odb_name=odb_name, instance_name=instance_name, step_name=step, mat_dict=mat_dict)
    else:
        print('The function create_christensen_field_variable_multiple_materials_also _for_quadratic_elements is beeing used')
        for step in steplist_names:
            create_Christensen_field_variable_multiple_materials_also_for_quadratic_elements(odb_name=odb_name, instance_name=instance_name, step_name=step, mat_dict=mat_dict)