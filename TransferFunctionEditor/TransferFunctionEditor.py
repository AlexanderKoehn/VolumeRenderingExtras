import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# TransferFunctionEditor
#

class TransferFunctionEditor(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "TransferFunctionEditor" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# TransferFunctionEditorWidget
#

class TransferFunctionEditorWidget(ScriptedLoadableModuleWidget):
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
    
    self.webView = qt.QWebView()
    self.webView.settings().setAttribute(qt.QWebSettings.DeveloperExtrasEnabled, True)

    if False:

      html = """
      <a id="reslice" href="reslicing">Run reslicing test</a>
      <p>
      <a href="chart">Run chart test</a>
      """
      self.webView.setHtml(html)

      self.webView.page().setLinkDelegationPolicy(qt.QWebPage.DelegateAllLinks)
      self.webView.connect('linkClicked(QUrl)', self.webViewCallback)
    else:
      url = qt.QUrl('http://afruehstueck.github.io/TFonly.html')
      self.webView.setUrl(url)

    self.webView.show()

    frame = self.webView.page().mainFrame().evaluateJavaScript("alert('loaded')")

    # Add vertical spacer
    self.layout.addStretch(1)


  def cleanup(self):
    pass

  def webViewCallback(self,qurl):
    url = qurl.toString()
    print(url)
    tf = f.evaluateJavaScript('tf_panel.getTF()')
    print(tf)
    if url == 'reslicing':
      self.reslicing()
    if url == 'chart':
      self.chartTest()
    pass

  notes = '''
  Python 2.7.10 (default, Sep 10 2015, 22:17:38) 
[GCC 4.2.1 Compatible Apple LLVM 5.1 (clang-503.0.40)] on darwin

>>> slicer.modules.TransferFunctionEditorWidget.webView
QWebView (QWebView at: 0x7fc23450cf90)
>>> slicer.modules.TransferFunctionEditorWidget.webView.page()
QWebPage (QWebPage at: 0x7fc23450d2f0)
>>> p = slicer.modules.TransferFunctionEditorWidget.webView.page()
>>> f = p.mainFrame()
>>> f.evaluateJavaScript("alert('hoot')")
reslicing
>>> page().mainFrame().evaluateJavaScript
Traceback (most recent call last):
  File "<console>", line 1, in <module>
NameError: name 'page' is not defined
>>> slicer.modules.TransferFunctionEditorWidget.page().mainFrame()
Traceback (most recent call last):
  File "<console>", line 1, in <module>
AttributeError: TransferFunctionEditorWidget instance has no attribute 'page'
>>> slicer.modules.TransferFunctionEditorWidget.webView.page().mainFrame()
QWebFrame (QWebFrame at: 0x7fc2345bcec0)
>>> slicer.modules.TransferFunctionEditorWidget.webView.page().mainFrame()f = 
  File "<console>", line 1
    slicer.modules.TransferFunctionEditorWidget.webView.page().mainFrame()f =
                                                                          ^
SyntaxError: invalid syntax
>>> f = slicer.modules.TransferFunctionEditorWidget.webView.page().mainFrame()
>>> f.evaluateJavaScript('tf_panel.getTF()')
>>> f.evaluateJavaScript('tf_panel.getTF()')
>>> 
>>> f = slicer.modules.TransferFunctionEditorWidget.webView.page().mainFrame()
>>> f.evaluateJavaScript('tf_panel.getTF()')
((0.3499, {u'a': 0.0, u'r': 0.0, u'b': 0.0, u'g': 0.0}), (0.35, {u'a': 0.35, u'r': 68.0, u'b': 84.0, u'g': 1.0}), (0.41, {u'a': 0.41, u'r': 65.0, u'b': 135.0, u'g': 68.0}), (0.47, {u'a': 0.47, u'r': 42.0, u'b': 142.0, u'g': 120.0}), (0.53, {u'a': 0.53, u'r': 34.0, u'b': 132.0, u'g': 168.0}), (0.59, {u'a': 0.59, u'r': 124.0, u'b': 80.0, u'g': 210.0}), (0.6499999999999999, {u'a': 0.6499999999999999, u'r': 253.0, u'b': 37.0, u'g': 231.0}), (0.6500999999999999, {u'a': 0.0, u'r': 0.0, u'b': 0.0, u'g': 0.0}))
>>> tf = f.evaluateJavaScript('tf_panel.getTF()')
>>> import json
>>> json.loads(tf)
Traceback (most recent call last):
  File "<console>", line 1, in <module>
  File "/Users/pieper/slicer4/latest/Slicer-superbuild/python-install/lib/python2.7/json/__init__.py", line 338, in loads
    return _default_decoder.decode(s)
  File "/Users/pieper/slicer4/latest/Slicer-superbuild/python-install/lib/python2.7/json/decoder.py", line 366, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
TypeError: expected string or buffer
>>> tf
((0.3499, {u'a': 0.0, u'r': 0.0, u'b': 0.0, u'g': 0.0}), (0.35, {u'a': 0.35, u'r': 68.0, u'b': 84.0, u'g': 1.0}), (0.41, {u'a': 0.41, u'r': 65.0, u'b': 135.0, u'g': 68.0}), (0.47, {u'a': 0.47, u'r': 42.0, u'b': 142.0, u'g': 120.0}), (0.53, {u'a': 0.53, u'r': 34.0, u'b': 132.0, u'g': 168.0}), (0.59, {u'a': 0.59, u'r': 124.0, u'b': 80.0, u'g': 210.0}), (0.6499999999999999, {u'a': 0.6499999999999999, u'r': 253.0, u'b': 37.0, u'g': 231.0}), (0.6500999999999999, {u'a': 0.0, u'r': 0.0, u'b': 0.0, u'g': 0.0}))
>>> tf.__class__()
()
>>> tt[0]
Traceback (most recent call last):
  File "<console>", line 1, in <module>
NameError: name 'tt' is not defined
>>> tf[0]
(0.3499, {u'a': 0.0, u'r': 0.0, u'b': 0.0, u'g': 0.0})
>>> tf[0][0]
0.3499
>>> tf[0][1]
{u'a': 0.0, u'r': 0.0, u'b': 0.0, u'g': 0.0}
>>> tf[0][1].a
Traceback (most recent call last):
  File "<console>", line 1, in <module>
AttributeError: 'dict' object has no attribute 'a'
>>> tf[0][1]['a']
0.0
>>> 
>>> 
>>> 
>>> vp = slicer.util.getNode('VolumeProperty')
>>> vp
(vtkMRMLVolumePropertyNode)0x139dda1d0
>>> print(vp)
vtkMRMLVolumePropertyNode (0x7fc235c2f330)
  ID: vtkMRMLVolumePropertyNode1
  Debug: Off
  Modified Time: 1135484
  Name: VolumeProperty
  Description: (none)
  SingletonTag: (none)
  HideFromEditors: 0
  Selectable: 1
  Selected: 0
  Indent:      0
  Node references:
    storage [storageNodeRef]: (none)
    transform [transformNodeRef]: (none)
  TransformNodeID: (none)
  Debug: Off
  Modified Time: 1109514
  Reference Count: 1
  Registered Events: (none)
  Name = (none)
  RestoreSelectionState = 0
  VolumeProperty:     Debug: Off
    Modified Time: 1135494
    Reference Count: 2
    Registered Events: 
      Registered Observers:
        vtkObserver (0x7fc234399e80)
          Event: 3
          EventName: StartEvent
          Command: 0x7fc235c2fe70
          Priority: 0
          Tag: 2
        vtkObserver (0x7fc23439a090)
          Event: 2
          EventName: DeleteEvent
          Command: 0x7fc234399ff0
          Priority: 0
          Tag: 3
        vtkObserver (0x7fc235c19890)
          Event: 33
          EventName: ModifiedEvent
          Command: 0x7fc234399ff0
          Priority: 0
          Tag: 4
        vtkObserver (0x7fc235c19ca0)
          Event: 2
          EventName: DeleteEvent
          Command: 0x7fc235c19c00
          Priority: 0
          Tag: 5
        vtkObserver (0x7fc235c19d00)
          Event: 4
          EventName: EndEvent
          Command: 0x7fc235c19c00
          Priority: 0
          Tag: 6
        vtkObserver (0x7fc2347ded30)
          Event: 2
          EventName: DeleteEvent
          Command: 0x7fc235c19d70
          Priority: 0
          Tag: 7
        vtkObserver (0x7fc2347ded90)
          Event: 41
          EventName: StartInteractionEvent
          Command: 0x7fc235c19d70
          Priority: 0
          Tag: 8
        vtkObserver (0x7fc2347df1e0)
          Event: 2
          EventName: DeleteEvent
          Command: 0x7fc2347df140
          Priority: 0
          Tag: 9
        vtkObserver (0x7fc2347df240)
          Event: 42
          EventName: InteractionEvent
          Command: 0x7fc2347df140
          Priority: 0
          Tag: 10
        vtkObserver (0x7fc23440d860)
          Event: 2
          EventName: DeleteEvent
          Command: 0x7fc2347df3b0
          Priority: 0
          Tag: 11
        vtkObserver (0x7fc23440d8c0)
          Event: 43
          EventName: EndInteractionEvent
          Command: 0x7fc2347df3b0
          Priority: 0
          Tag: 12
        vtkObserver (0x7fc235d6e170)
          Event: 2
          EventName: DeleteEvent
          Command: 0x7fc235d6e100
          Priority: 0
          Tag: 13
        vtkObserver (0x7fc235d6e1a0)
          Event: 33
          EventName: ModifiedEvent
          Command: 0x7fc235d6e100
          Priority: 0
          Tag: 14
        vtkObserver (0x7fc235d6eb50)
          Event: 2
          EventName: DeleteEvent
          Command: 0x7fc235d6eab0
          Priority: 0
          Tag: 15
        vtkObserver (0x7fc235d6ef00)
          Event: 33
          EventName: ModifiedEvent
          Command: 0x7fc235d6eab0
          Priority: 0
          Tag: 16
        vtkObserver (0x7fc235c2ffa0)
          Event: 2
          EventName: DeleteEvent
          Command: 0x7fc235c2fe70
          Priority: 0
          Tag: 1
    Independent Components: On
    Interpolation Type: Linear
    Properties for material 0
    Color Channels: 3
    RGB Color Transfer Function: 0x7fc23440d8f0
    Scalar Opacity Transfer Function: 0x7fc2347b4260
    Gradient Opacity Transfer Function: 0x7fc235c68da0
    DisableGradientOpacity: Off
    ComponentWeight: 1
    Shade: 1
        Ambient: 0.3
        Diffuse: 0.6
        Specular: 0.5
        SpecularPower: 40
    Properties for material 1
    Color Channels: 1
    Gray Color Transfer Function: 0
    Scalar Opacity Transfer Function: 0
    Gradient Opacity Transfer Function: 0
    DisableGradientOpacity: Off
    ComponentWeight: 1
    Shade: 0
        Ambient: 0.1
        Diffuse: 0.7
        Specular: 0.2
        SpecularPower: 10
    Properties for material 2
    Color Channels: 1
    Gray Color Transfer Function: 0
    Scalar Opacity Transfer Function: 0
    Gradient Opacity Transfer Function: 0
    DisableGradientOpacity: Off
    ComponentWeight: 1
    Shade: 0
        Ambient: 0.1
        Diffuse: 0.7
        Specular: 0.2
        SpecularPower: 10
    Properties for material 3
    Color Channels: 1
    Gray Color Transfer Function: 0
    Scalar Opacity Transfer Function: 0
    Gradient Opacity Transfer Function: 0
    DisableGradientOpacity: Off
    ComponentWeight: 1
    Shade: 0
        Ambient: 0.1
        Diffuse: 0.7
        Specular: 0.2
        SpecularPower: 10


>>> vp.GetColor()
(vtkColorTransferFunction)0x139dda170
>>> colortf = vp.GetColor()
>>> print(colortf)
vtkColorTransferFunction (0x7fc23440d8f0)
  Debug: Off
  Modified Time: 1134291
  Reference Count: 6
  Registered Events: 
    Registered Observers:
      vtkObserver (0x7fc235cc7a30)
        Event: 3
        EventName: StartEvent
        Command: 0x7fc23440dda0
        Priority: 0
        Tag: 2
      vtkObserver (0x7fc235cc7e40)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc235cc7da0
        Priority: 0
        Tag: 3
      vtkObserver (0x7fc2347f2720)
        Event: 33
        EventName: ModifiedEvent
        Command: 0x7fc235cc7da0
        Priority: 0
        Tag: 4
      vtkObserver (0x7fc2347f2b30)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc2347f2a90
        Priority: 0
        Tag: 5
      vtkObserver (0x7fc2347f2b90)
        Event: 4
        EventName: EndEvent
        Command: 0x7fc2347f2a90
        Priority: 0
        Tag: 6
      vtkObserver (0x7fc2347f2da0)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc2347f2d00
        Priority: 0
        Tag: 7
      vtkObserver (0x7fc2347f2e00)
        Event: 41
        EventName: StartInteractionEvent
        Command: 0x7fc2347f2d00
        Priority: 0
        Tag: 8
      vtkObserver (0x7fc2347e0b30)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc2347e0a90
        Priority: 0
        Tag: 9
      vtkObserver (0x7fc2347e0b90)
        Event: 42
        EventName: InteractionEvent
        Command: 0x7fc2347e0a90
        Priority: 0
        Tag: 10
      vtkObserver (0x7fc2347b41d0)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc2347b4130
        Priority: 0
        Tag: 11
      vtkObserver (0x7fc2347b4230)
        Event: 43
        EventName: EndInteractionEvent
        Command: 0x7fc2347b4130
        Priority: 0
        Tag: 12
      vtkObserver (0x7fc235d70080)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc235d70010
        Priority: 0
        Tag: 13
      vtkObserver (0x7fc235d705a0)
        Event: 43
        EventName: EndInteractionEvent
        Command: 0x7fc235d70010
        Priority: 0
        Tag: 14
      vtkObserver (0x7fc235d709b0)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc235d70940
        Priority: 0
        Tag: 15
      vtkObserver (0x7fc235d70d30)
        Event: 4
        EventName: EndEvent
        Command: 0x7fc235d70940
        Priority: 0
        Tag: 16
      vtkObserver (0x7fc235d71dc0)
        Event: 33
        EventName: ModifiedEvent
        Command: 0x7fc23588be60
        Priority: 0
        Tag: 17
      vtkObserver (0x7fc235d71df0)
        Event: 3
        EventName: StartEvent
        Command: 0x7fc23588c930
        Priority: 0
        Tag: 18
      vtkObserver (0x7fc235d71e20)
        Event: 33
        EventName: ModifiedEvent
        Command: 0x7fc23588c930
        Priority: 0
        Tag: 19
      vtkObserver (0x7fc235d71e50)
        Event: 4
        EventName: EndEvent
        Command: 0x7fc23588c930
        Priority: 0
        Tag: 20
      vtkObserver (0x7fc235d71cd0)
        Event: 33
        EventName: ModifiedEvent
        Command: 0x7fc23588e8c0
        Priority: 0
        Tag: 21
      vtkObserver (0x7fc235d71eb0)
        Event: 3
        EventName: StartEvent
        Command: 0x7fc23588f4a0
        Priority: 0
        Tag: 22
      vtkObserver (0x7fc235d71ee0)
        Event: 33
        EventName: ModifiedEvent
        Command: 0x7fc23588f4a0
        Priority: 0
        Tag: 23
      vtkObserver (0x7fc235d71f10)
        Event: 4
        EventName: EndEvent
        Command: 0x7fc23588f4a0
        Priority: 0
        Tag: 24
      vtkObserver (0x7fc23440de70)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc23440dda0
        Priority: 0
        Tag: 1
  Alpha: 1
  VectorMode: Component
  VectorComponent: 0
  VectorSize: -1
  IndexedLookup: OFF
  AnnotatedValues: 0 entries.
  Size: 7
  Clamping: On
  Color Space: RGB
  Scale: Linear
  Range: 0 to 0.995081
  AllowDuplicateScalars: 0
  NanColor: 0.5, 0, 0
  BelowRangeColor: (0, 0, 0)
  UseBelowRangeColor: OFF
  ABoveRangeColor: (1, 1, 1)
  UseAboveRangeColor: OFF
    0 X: 0 R: 0 G: 0 B: 0 Sharpness: 0 Midpoint: 0.5
    1 X: 2.22507e-308 R: 0 G: 0 B: 0 Sharpness: 0 Midpoint: 0.5
    2 X: 0.249746 R: 0.25098 G: 0.25098 B: 0.25098 Sharpness: 0 Midpoint: 0.5
    3 X: 0.499492 R: 0.501961 G: 0.501961 B: 0.501961 Sharpness: 0 Midpoint: 0.5
    4 X: 0.749238 R: 0.752941 G: 0.752941 B: 0.752941 Sharpness: 0 Midpoint: 0.5
    5 X: 0.995081 R: 1 G: 1 B: 1 Sharpness: 0 Midpoint: 0.5
    6 X: 0.995081 R: 1 G: 1 B: 1 Sharpness: 0 Midpoint: 0.5


>>> colortf.AddRGBPoint()
Traceback (most recent call last):
  File "<console>", line 1, in <module>
TypeError: no overloads of AddRGBPoint() take 0 arguments
>>> so = vp.GetScalarOpacity()
>>> print(so)
vtkPiecewiseFunction (0x7fc2347b4260)
  Debug: Off
  Modified Time: 1134253
  Reference Count: 4
  Registered Events: 
    Registered Observers:
      vtkObserver (0x7fc2347b4b70)
        Event: 3
        EventName: StartEvent
        Command: 0x7fc2347b4a40
        Priority: 0
        Tag: 2
      vtkObserver (0x7fc2347b4f80)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc2347b4ee0
        Priority: 0
        Tag: 3
      vtkObserver (0x7fc2347b4fe0)
        Event: 33
        EventName: ModifiedEvent
        Command: 0x7fc2347b4ee0
        Priority: 0
        Tag: 4
      vtkObserver (0x7fc2347b53f0)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc2347b5350
        Priority: 0
        Tag: 5
      vtkObserver (0x7fc2347b5450)
        Event: 4
        EventName: EndEvent
        Command: 0x7fc2347b5350
        Priority: 0
        Tag: 6
      vtkObserver (0x7fc2347b5860)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc2347b57c0
        Priority: 0
        Tag: 7
      vtkObserver (0x7fc2347b58c0)
        Event: 41
        EventName: StartInteractionEvent
        Command: 0x7fc2347b57c0
        Priority: 0
        Tag: 8
      vtkObserver (0x7fc2347b5d10)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc2347b5c70
        Priority: 0
        Tag: 9
      vtkObserver (0x7fc2347b5d70)
        Event: 42
        EventName: InteractionEvent
        Command: 0x7fc2347b5c70
        Priority: 0
        Tag: 10
      vtkObserver (0x7fc235c68d10)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc2347b60e0
        Priority: 0
        Tag: 11
      vtkObserver (0x7fc235c68d70)
        Event: 43
        EventName: EndInteractionEvent
        Command: 0x7fc2347b60e0
        Priority: 0
        Tag: 12
      vtkObserver (0x7fc235d6f640)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc235d6f600
        Priority: 0
        Tag: 13
      vtkObserver (0x7fc235d6f670)
        Event: 43
        EventName: EndInteractionEvent
        Command: 0x7fc235d6f600
        Priority: 0
        Tag: 14
      vtkObserver (0x7fc235d6fdf0)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc235d6fd80
        Priority: 0
        Tag: 15
      vtkObserver (0x7fc235d6fe20)
        Event: 4
        EventName: EndEvent
        Command: 0x7fc235d6fd80
        Priority: 0
        Tag: 16
      vtkObserver (0x7fc235d71d00)
        Event: 33
        EventName: ModifiedEvent
        Command: 0x7fc23588be60
        Priority: 0
        Tag: 17
      vtkObserver (0x7fc235d71d30)
        Event: 3
        EventName: StartEvent
        Command: 0x7fc23588c930
        Priority: 0
        Tag: 18
      vtkObserver (0x7fc235d71d60)
        Event: 33
        EventName: ModifiedEvent
        Command: 0x7fc23588c930
        Priority: 0
        Tag: 19
      vtkObserver (0x7fc235d71d90)
        Event: 4
        EventName: EndEvent
        Command: 0x7fc23588c930
        Priority: 0
        Tag: 20
      vtkObserver (0x7fc2347b4b10)
        Event: 2
        EventName: DeleteEvent
        Command: 0x7fc2347b4a40
        Priority: 0
        Tag: 1
  Information: 0x7fc2347b42e0
  Data Released: False
  Global Release Data: Off
  UpdateTime: 0
  Field Data:
    Debug: Off
    Modified Time: 1134251
    Reference Count: 1
    Registered Events: (none)
    Number Of Arrays: 0
    Number Of Components: 0
    Number Of Tuples: 0
  Clamping: 1
  Range: [0,0.995081]
  Function Points: 4
    0 X: 0 Y: 0 Sharpness: 0 Midpoint: 0.5
    1 X: 2.22507e-308 Y: 0 Sharpness: 0 Midpoint: 0.5
    2 X: 0.995081 Y: 1 Sharpness: 0 Midpoint: 0.5
    3 X: 0.995081 Y: 1 Sharpness: 0 Midpoint: 0.5
  AllowDuplicateScalars: 0


>>> 
>>> so
(vtkPiecewiseFunction)0x139dda350
>>> so.RemoveAllPoints()
>>> so.AddPoint(0, 0)
0
>>> so.AddPoint(1, 0.2)

  '''
#
# TransferFunctionEditorLogic
#

class TransferFunctionEditorLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
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

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('TransferFunctionEditorTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class TransferFunctionEditorTest(ScriptedLoadableModuleTest):
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
    self.test_TransferFunctionEditor1()

  def test_TransferFunctionEditor1(self):
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
    logic = TransferFunctionEditorLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
