import ctypes
from pathlib import Path
from shutil import copyfile
import xml.etree.ElementTree as ET

'''
    A series of simulations
        This code will run a series of successive calls to the CrowdMechanics library.
        It will save the output files to a folder outputXML/.
        We use for the names of the output files the convention "AgentDynamics output t=TIME_VALUE.xml".
        The same convention is used in our code to export the results to the ChAOS software.
'''
### Parameters
dt  = 0.1   # The "TimeStep" in Parameters.xml
Ndt = 10    # The number of successive calls to the library

outputPath = "outputXML/"
Path(outputPath).mkdir(parents=True, exist_ok=True)

# Load the library into ctypes
Clibrary = ctypes.CDLL('../../src/mechanical_layer/build/libCrowdMechanics.so')
# The file name for the dynamical quantities will be used to build the names of the output files
agentDynamicsFilename = "AgentDynamics.xml"
# Prepare the call to CrowdMechanics
files = [b"Parameters.xml",
         b"Materials.xml",
         b"Geometry.xml",
         b"Agents.xml",
         agentDynamicsFilename.encode('ascii')]
nFiles = len(files)
filesInput = (ctypes.c_char_p * nFiles)()
filesInput[:] = files


### Actual loop
for t in range(Ndt):
    print('Looping the Crowd mechanics engine - t=%.1fs...'%(t * dt))
    # Copy Agent dynamics input file
    copyfile('dynamic/' + agentDynamicsFilename, r'AgentDynamics input t=%.1f.xml'%(t * dt))
    # Call the mechanical layer
    Clibrary.CrowdMechanics(filesInput)
    # Copy Agent dynamics output file to the directory that will be read by ChAOS
    copyfile('dynamic/' + agentDynamicsFilename, outputPath + r'AgentDynamics output t=%.1f.xml'%((t +1) * dt))
    # Save the AgentInteractions file, if it exists
    try:
        copyfile('dynamic/AgentInteractions.xml', outputPath + r'AgentInteractions t=%.1f.xml'%((t + 1) * dt))
    except FileNotFoundError:
        pass
    # Prepare next run: Add dynamics tag to the input file
    # This is the step where you decide the FP and Mp that will drive the next dt seconds for each agent
    XMLtree = ET.parse('dynamic/' + agentDynamicsFilename)
    agentsTree = XMLtree.getroot()
    ''' Sample dummy code where we put the same constant values for each agent
        for agent in agentsTree:
            dynamicsItem = ET.SubElement(agent, "Dynamics")
            dynamicsItem.attrib["Fp"] = "100,100"
            dynamicsItem.attrib["Mp"] = "10"
        To be replaced...
    '''
    XMLtree.write('dynamic/' + agentDynamicsFilename)
# Done!
print('Loop terminated at t=%.1f!'%(Ndt * dt))


'''
    Bonus:
    Export to ChAOS

'''
from ...src.configuration.backup import xml_to_Chaos
### Parameters
filenameCSV = "all_trajectories.csv"
outputPathAbsolute = Path(outputPath)
xml_to_Chaos.export_dict_to_CSV(outputPathAbsolute, filenameCSV)
xml_to_Chaos.export_from_CSV_to_CHAOS(outputPathAbsolute / filenameCSV, outputPathAbsolute / "ForChaos", dt)
