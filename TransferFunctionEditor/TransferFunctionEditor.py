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
    self.parent.title = "Transfer Function Editor" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Volume Rendering"]
    self.parent.dependencies = []
    self.parent.contributors = ["Anna Fruehstueck", "Steve Pieper"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is a JavaScript-based Transfer Function Editor Module
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
	
	#found this method of connecting Python to JS
	#http://pysnippet.blogspot.com/2010/01/calling-python-from-javascript-in-pyqts.html
	#but couldn't (yet) make it work
	# class StupidClass():
		# """Simple class with one slot and one read-only property."""
		# @qt.pyqtSlot(str)
		# def showMessage(self, msg):
			# """Open a message box and display the specified message."""
			# qt.QMessageBox.information(None, "Info", msg)
		

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
		self.webView.resize( 1000, 280 )
		self.webView.setWindowTitle( 'Transfer Function Editor' )
		self.webView.settings().setAttribute(qt.QWebSettings.DeveloperExtrasEnabled, True)
		
		#load HTML from local path
		file_path = os.path.abspath( os.path.join( os.path.dirname( __file__ ), "Resources/web/TF.html" ) )
		local_url = qt.QUrl.fromLocalFile( file_path )
		self.webView.setUrl( local_url )
		
		#myObj = StupidClass()
		#self.webView.page().mainFrame().addToJavaScriptWindowObject("pyObj", myObj)

		''' #COMMENT
		histogram is still missing because of missing data input
		calculate data for histogram with
		var histogram = Statistics.calcHistogram( data ); //(in ui.cs, expects data array and optional options)
		tf_panel.setHistogram( histogram )
		histogram object should contain { numBins: number, bins: array[numBins], maxBinValue: number }
		'''
		self.webView.show()
		self.webView.page().setLinkDelegationPolicy( qt.QWebPage.DelegateAllLinks )
		#connect web view to click events within webpage
		self.webView.connect( 'linkClicked(QUrl)', self.webViewCallback )
		#frame = self.webView.page().mainFrame().evaluateJavaScript("console.log('loaded')")

		# Add vertical spacer
		self.layout.addStretch(1)
	def cleanup(self):
		pass
	def webViewCallback(self,qurl):
		#url = qurl.toString()
		#print(url)
		#if url == 'updateTF':
		self.updateTF()
		pass
	def updateTF(self):
		vp = slicer.util.getNode('VolumeProperty')
		colorTF = vp.GetColor()
		opacityTF = vp.GetScalarOpacity()
		
		colorRange = colorTF.GetRange()
		cR = colorRange[ 1 ] - colorRange[ 0 ]
		opacityRange = opacityTF.GetRange()
		cO = opacityRange[ 1 ] - opacityRange[ 0 ]
		
		colorTF.RemoveAllPoints() #probably shouldn't remove all of them at each update
		opacityTF.RemoveAllPoints()
		
		tf_values = self.webView.page().mainFrame().evaluateJavaScript( 'tf_panel.getTF()' )
		colorTF.SetColorSpaceToRGB()
		
		colorTF.AddRGBPoint( colorRange[ 0 ], 0, 0, 0 ) #add points for 0 and 1
		colorTF.AddRGBPoint( colorRange[ 1 ], 0, 0, 0 )
		
		opacityTF.AddPoint( opacityRange[ 0 ], 0 ) #add points for 0 and 1
		opacityTF.AddPoint( opacityRange[ 1 ], 0 )
		
		for( x, color ) in tf_values:
			x = max( 0, min( x, 1 ) ) #prevent x from going out of range
			
			xC = colorRange[ 0 ] + ( cR * x ) #'denormalize' range
			xO = opacityRange[ 0 ] + ( cO * x ) #'denormalize' range
			r = color[ 'r' ] / 255 #normalize RGB
			g = color[ 'g' ] / 255
			b = color[ 'b' ] / 255
			a = color[ 'a' ]
			colorTF.AddRGBPoint( xC, r, g, b )
			opacityTF.AddPoint( xO, a )		
		pass
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
