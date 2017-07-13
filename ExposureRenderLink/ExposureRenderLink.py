import subprocess
import os
import json
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from collections import OrderedDict

#
# ExposureRenderLink
#

class ExposureRenderLink(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  Uses fork of ExposureRender that can be configured to load data via command line.
  https://github.com/AlexanderKoehn/exposure-render.release110
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Exposure Render Link"
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Alexander Koehn (Fraunhofer MEVIS)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This module allows to control an ExposureRender instance.
    Sends volume and LUT settings via HTTP and receives rendered image.
    """
    self.parent.acknowledgementText = """
    ExposureRender by Thomas Kroes. https://github.com/ThomasKroes/exposure-render.release110
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# ExposureRenderLinkWidget
#

class ExposureRenderLinkWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input volume to send over." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    self.lutSelector = slicer.qMRMLNodeComboBox()
    self.lutSelector.nodeTypes = ["vtkMRMLVolumePropertyNode"]
    self.lutSelector.selectNodeUponCreation = True
    self.lutSelector.addEnabled = False
    self.lutSelector.removeEnabled = False
    self.lutSelector.noneEnabled = False
    self.lutSelector.showHidden = False
    self.lutSelector.showChildNodeTypes = False
    self.lutSelector.setMRMLScene( slicer.mrmlScene )
    self.lutSelector.setToolTip( "Pick the LUT to use." )
    parametersFormLayout.addRow("Input LUT: ", self.lutSelector)

    # ExposureRender Exe
    self.exposureRenderPathWidget = qt.QLineEdit()
    parametersFormLayout.addRow("ExposureRender Path", self.exposureRenderPathWidget)
    
    self.dataSharePathWidget = qt.QLineEdit()
    self.dataSharePathWidget.text = "F:\DemoData\Slicer"
    parametersFormLayout.addRow("Data Share Path", self.dataSharePathWidget)

    #
    # Use HTTP Connection
    #
    self.useHTTPConnection = qt.QCheckBox()
    self.useHTTPConnection.checked = 0
    self.useHTTPConnection.setToolTip("If checked, use HTTP connection.")
    parametersFormLayout.addRow("Use HTTP",self.useHTTPConnection)

    self.exposureRenderHostWidget = qt.QLineEdit()
    self.exposureRenderHostWidget.setToolTip("Enter IP:Port of ExposureRender Host")
    parametersFormLayout.addRow("Host", self.exposureRenderHostWidget)

    #
    # Button to send volume and start ExposureRender
    #
    self.applyButton = qt.QPushButton("Send")
    self.applyButton.toolTip = "Send to ExposureRender."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.useHTTPConnection.connect('clicked(bool)', self.onUseHTTPConnection)
    self.applyButton.connect('clicked(bool)', self.onSendButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onUseHTTPConnection(self):
    if self.useHTTPConnection.checked:
      self.exposureRenderPathWidget.enabled = False
      self.exposureRenderHostWidget.enabled = True
    else:
      self.exposureRenderPathWidget.enabled = True
      self.exposureRenderHostWidget.enabled = False

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode()

  def onSendButton(self):
    logic = ExposureRenderLinkLogic()
    if self.useHTTPConnection.checked:
      exposureHost = self.exposureRenderHostWidget.text
      logic.runHTTP(self.inputSelector.currentNode(), self.lutSelector.currentNode(), exposureHost)
    else:
      exposureExecutable = self.exposureRenderPathWidget.text
      logic.runCLI(self.inputSelector.currentNode(),  self.lutSelector.currentNode(), exposureExecutable, self.dataSharePathWidget.text)

#
# ExposureRenderLinkLogic
#

class ExposureRenderLinkLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self, volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputData(self, inputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    return True

  def getCameraDataAsXML(self, ext):
    xml = """<!DOCTYPE Camera>
<Presets>
  <Preset Name="volume">
    <Film>
      <Width Value="400"/>
      <Height Value="500"/>
      <Exposure Value="0.75"/>
    </Film>
    <Aperture>
      <Size Value="0"/>
    </Aperture>
    <Projection>
      <FieldOfView Value="{fov}"/>
    </Projection>
    <Focus>
      <FocalDistance Value="{focalDistance}"/>
    </Focus>
    <From X="{fromX}" Y="{fromY}" Z="{fromZ}"/>
    <Target X="{targetX}" Y="{targetY}" Z="{targetZ}"/>
    <Up X="{upX}" Y="{upY}" Z="{upZ}"/>
  </Preset>
</Presets>
"""
    camera = slicer.util.getNode('Default Scene Camera')
    pos =  [0,0,0]
    up = [0,0,0]
    target = [0,0,0] 
    camera.GetPosition(pos)
    camera.GetViewUp(up)
    camera.GetFocalPoint(target)
    focalDistance = camera.GetCamera().GetDistance()
    fov = camera.GetViewAngle()
    return xml.format(
      fov=fov,
      focalDistance=focalDistance,
      fromX=pos[0] / ext[1],
      fromY=pos[1] / ext[3],
      fromZ=pos[2] / ext[5],
      targetX=target[0] / ext[1],
      targetY=target[1] / ext[3],
      targetZ=target[2] / ext[5],
      upX=up[0],
      upY=up[1],
      upZ=up[2]
    )

  def getLUTDataAsXML(self, inputLUT, intensityRange):
    wasModifying = inputLUT.StartModify()
    
    # print slicer.util.getNodes('*Display*')
    vr = slicer.util.getNode('VolumeRendering')
    ambient = vr.GetAmbient()
    diffuse = vr.GetDiffuse()
    specular = vr.GetSpecular()
    specularPower = vr.GetPower() # aka 1-Roughness
    xml = """<!DOCTYPE Appearance>
<Presets>
<Preset Name="volume">
<Nodes>
{nodes}
</Nodes>
<DensityScale Value="{densityScale}"/>
<ShadingType Value="{shadingType}"/>
<GradientFactor Value="{gradientFactor}"/>
</Preset>
</Presets>"""
    node_xml_template = """<Node>
<NormalizedIntensity Value="{normalizedIntensity}"/>
<Opacity Value="{opacity}"/>
<Diffuse G="{diffuseG}" R="{diffuseR}" B="{diffuseB}"/>
<Specular G="{specularG}" R="{specularR}" B="{specularB}"/>
<Emission G="{emissionG}" R="{emissionR}" B="{emissionB}"/>
<Roughness Value="{roughness}"/>
</Node>
"""
    densityScale = 100
    shadingType = 2
    gradientFactor = 80
    positions = set()
    opacity_positions = set()
    info = [0,0,0,0,0,0]
    colorTF = inputLUT.GetColor()
    for i in range(colorTF.GetSize()):
      colorTF.GetNodeValue(i, info)
      positions.add(info[0])
    info = [0,0,0,0]
    opacityTF = inputLUT.GetScalarOpacity()
    for i in range(opacityTF.GetSize()):
      opacityTF.GetNodeValue(i, info)
      positions.add(info[0])
    color = [0,0,0]
    opacity = [0,0,0]
    nodes = OrderedDict()
    minIntensity, maxIntensity = intensityRange
    deltaIntensity = maxIntensity - minIntensity
    for x in sorted(positions):
      colorTF.GetColor(x, color)
      opacity = opacityTF.GetValue(x)
      normalizedIntensity = (x - minIntensity) / deltaIntensity
      if normalizedIntensity < 0:
        normalizedIntensity = 0
      elif normalizedIntensity > 1:
        normalizedIntensity = 1
        if 1 in nodes: break
      node = {
        'normalizedIntensity': normalizedIntensity,
        'opacity': opacity,
        'diffuseR': int(color[0] * 255),
        'diffuseG': int(color[1] * 255),
        'diffuseB': int(color[2] * 255),
        'specularR': int(specular * 255),
        'specularG': int(specular * 255),
        'specularB': int(specular * 255),
        'emissionR': 0,
        'emissionG': 0,
        'emissionB': 0,
        'roughness': int((1.0 - specularPower) * 100)
      }
      nodes[normalizedIntensity] = node_xml_template.format(**node)
    return xml.format(
      nodes="".join(nodes.values()),
      densityScale=densityScale,
      shadingType=shadingType,
      gradientFactor=gradientFactor
    )
    
  def runHTTP(self, inputVolume, inputLUT, host):
    print 'ToDo', host
  
  def runCLI(self, inputVolume, inputLUT, exposurePath, dataSharePath):
    """
    """
    if not self.isValidInputData(inputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False
    
    logging.info('Processing started')

    imageData = inputVolume.GetImageData()
    intensityRange = [0, 0]
    imageData.GetScalarRange(intensityRange)
    ext = imageData.GetExtent()
    
    lut_xml = self.getLUTDataAsXML(inputLUT, intensityRange)
    filename = os.path.join(dataSharePath, 'AppearancePresets.xml')
    with open(filename, 'w') as fp:
      fp.write(lut_xml)

    filename = os.path.join(dataSharePath, 'CameraPresets.xml')
    with open(filename, 'w') as fp:
      fp.write(self.getCameraDataAsXML(ext))
    
    return
    writer = vtk.vtkMetaImageWriter()
    filename = os.path.join(dataSharePath, 'volume.mhd')
    writer.SetFileName(filename)
        
    if vtk.VTK_MAJOR_VERSION <= 5:
        writer.SetInputConnection(imageData.GetProducerPort())
    else:
        writer.SetInputData(imageData)
    writer.Write()

    logging.info('Call ExposureRender ' + exposurePath)
    args = [exposurePath+'/ExposureRender.exe', dataSharePath]
    subprocess.Popen(args, cwd=exposurePath)
    logging.info('Processing completed')
    return True


class ExposureRenderLinkTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ExposureRenderLink1()

  def test_ExposureRenderLink1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = ExposureRenderLinkLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
