import os, sys
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import csv
from slicer.util import VTKObservationMixin
import platform
import time
import urllib
import shutil
from CommonUtilities import *

#
# ShapeAnalysisModule
#

class ShapeAnalysisModule(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Shape Analysis Module"
    self.parent.categories = ["SPHARM"]
    self.parent.dependencies = []
    self.parent.contributors = ["Laura Pascal (Kitware Inc.), Beatriz Paniagua (Kitware Inc.), Hina Shah (Kitware Inc.)"]
    self.parent.helpText = """
      SPHARM-PDM is a tool that computes point-based models using a parametric
      boundary description for the computing of Shape Analysis.
    """
    self.parent.acknowledgementText = """
      This work was supported by NIH NIBIB R01EB021391
      (Shape Analysis Toolbox for Medical Image Computing Projects).
    """

#
# ShapeAnalysisModuleWidget
#

class ShapeAnalysisModuleWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    #
    #   Global variables
    #
    self.Logic = ShapeAnalysisModuleLogic()
    self.progressbars_layout = None

    #
    #  Interface
    #
    loader = qt.QUiLoader()
    self.moduleName = 'ShapeAnalysisModule'
    scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
    scriptedModulesPath = os.path.dirname(scriptedModulesPath)
    path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.moduleName)
    qfile = qt.QFile(path)
    qfile.open(qt.QFile.ReadOnly)
    widget = loader.load(qfile, self.parent)
    self.layout = self.parent.layout()
    self.widget = widget
    self.layout.addWidget(widget)

    # Global variables of the Interface
    #   Group Project IO
    self.CollapsibleButton_GroupProjectIO = self.getWidget('CollapsibleButton_GroupProjectIO')
    self.GroupProjectInputDirectory = self.getWidget('DirectoryButton_GroupProjectInputDirectory')
    self.GroupProjectOutputDirectory = self.getWidget('DirectoryButton_GroupProjectOutputDirectory')
    self.Debug = self.getWidget('checkBox_Debug')
    #   Post Processed Segmentation
    self.CollapsibleButton_SegPostProcess = self.getWidget('CollapsibleButton_SegPostProcess')
    self.OverwriteSegPostProcess = self.getWidget('checkBox_OverwriteSegPostProcess')
    self.label_RescaleSegPostProcess = self.getWidget('label_RescaleSegPostProcess')
    self.RescaleSegPostProcess = self.getWidget('checkBox_RescaleSegPostProcess')
    self.sx = self.getWidget('SliderWidget_sx')
    self.sy = self.getWidget('SliderWidget_sy')
    self.sz = self.getWidget('SliderWidget_sz')
    self.label_sx = self.getWidget('label_sx')
    self.label_sy = self.getWidget('label_sy')
    self.label_sz = self.getWidget('label_sz')
    self.LabelState = self.getWidget('checkBox_LabelState')
    self.label_ValueLabelNumber = self.getWidget('label_ValueLabelNumber')
    self.ValueLabelNumber = self.getWidget('SliderWidget_ValueLabelNumber')
    #   Generate Mesh Parameters
    self.CollapsibleButton_GenParaMesh = self.getWidget('CollapsibleButton_GenParaMesh')
    self.OverwriteGenParaMesh = self.getWidget('checkBox_OverwriteGenParaMesh')
    self.NumberofIterations = self.getWidget('SliderWidget_NumberofIterations')
    #   Parameters to SPHARM Mesh
    self.CollapsibleButton_ParaToSPHARMMesh = self.getWidget('CollapsibleButton_ParaToSPHARMMesh')
    self.OverwriteParaToSPHARMMesh = self.getWidget('checkBox_OverwriteParaToSPHARMMesh')
    self.SubdivLevelValue = self.getWidget('SliderWidget_SubdivLevelValue')
    self.SPHARMDegreeValue = self.getWidget('SliderWidget_SPHARMDegreeValue')
    self.thetaIterationValue = self.getWidget('spinBox_thetaIterationValue')
    self.phiIterationValue = self.getWidget('spinBox_phiIterationValue')
    self.medialMesh = self.getWidget('checkBox_medialMesh')
    #   Advanced Post Processed Segmentation
    self.CollapsibleButton_AdvancedPostProcessedSegmentation = self.getWidget('CollapsibleButton_AdvancedPostProcessedSegmentation')
    self.GaussianFiltering = self.getWidget('checkBox_GaussianFiltering')
    self.label_VarianceX = self.getWidget('label_VarianceX')
    self.VarianceX = self.getWidget('SliderWidget_VarianceX')
    self.label_VarianceY = self.getWidget('label_VarianceY')
    self.VarianceY = self.getWidget('SliderWidget_VarianceY')
    self.label_VarianceZ = self.getWidget('label_VarianceZ')
    self.VarianceZ = self.getWidget('SliderWidget_VarianceZ')
    #   Advanced Parameters to SPHARM Mesh
    self.CollapsibleButton_AdvancedParametersToSPHARMMesh = self.getWidget('CollapsibleButton_AdvancedParametersToSPHARMMesh')
    self.useRegTemplate = self.getWidget('checkBox_useRegTemplate')
    self.label_regTemplate = self.getWidget('label_regTemplate')
    self.regTemplate = self.getWidget('PathLineEdit_regTemplate')
    self.useFlipTemplate = self.getWidget('checkBox_useFlipTemplate')
    self.label_flipTemplate = self.getWidget('label_flipTemplate')
    self.flipTemplate = self.getWidget('PathLineEdit_flipTemplate')
    self.choiceOfFlip = self.getWidget('comboBox_choiceOfFlip')
    self.sameFlipForAll = self.getWidget('checkBox_sameFlipForAll')
    self.tableWidget_ChoiceOfFlip = self.getWidget('tableWidget_ChoiceOfFlip')
    #   Visualization
    self.CollapsibleButton_Visualization = self.getWidget('CollapsibleButton_Visualization')
    self.visualizationInSPV = self.getWidget('pushButton_visualizationInSPV')
    self.CheckableComboBox_visualization = self.getWidget('CheckableComboBox_visualization')
    self.tableWidget_visualization = self.getWidget('tableWidget_visualization')
    #   Apply CLIs
    self.ApplyButton = self.getWidget('applyButton')
    self.progress_layout = self.getWidget('progress_layout')

    # Connections
    #   Group Project IO
    self.CollapsibleButton_GroupProjectIO.connect('clicked()',
                                                   lambda: self.onSelectedCollapsibleButtonOpen(
                                                     self.CollapsibleButton_GroupProjectIO))
    self.GroupProjectInputDirectory.connect('directoryChanged(const QString &)', self.onInputDirectoryChanged)
    self.GroupProjectOutputDirectory.connect('directoryChanged(const QString &)', self.onOutputDirectoryChanged)
    self.Debug.connect('clicked(bool)', self.onDebug)

    #   Post Processed Segmentation
    self.CollapsibleButton_SegPostProcess.connect('clicked()',
                                                  lambda: self.onSelectedCollapsibleButtonOpen(
                                                    self.CollapsibleButton_SegPostProcess))
    self.OverwriteSegPostProcess.connect('clicked(bool)', self.onOverwriteFilesSegPostProcess)
    self.RescaleSegPostProcess.connect('stateChanged(int)', self.onSelectSpacing)
    self.sx.connect('valueChanged(double)', self.onSxValueChanged)
    self.sy.connect('valueChanged(double)', self.onSyValueChanged)
    self.sz.connect('valueChanged(double)', self.onSzValueChanged)
    self.LabelState.connect('clicked(bool)', self.onSelectValueLabelNumber)
    self.ValueLabelNumber.connect('valueChanged(double)', self.onLabelNumberValueChanged)

    #   Generate Mesh Parameters
    self.CollapsibleButton_GenParaMesh.connect('clicked()',
                                                  lambda: self.onSelectedCollapsibleButtonOpen(
                                                    self.CollapsibleButton_GenParaMesh))
    self.OverwriteGenParaMesh.connect('clicked(bool)', self.onOverwriteFilesGenParaMesh)
    self.NumberofIterations.connect('valueChanged(double)', self.onNumberofIterationsValueChanged)

    #   Parameters to SPHARM Mesh
    self.CollapsibleButton_ParaToSPHARMMesh.connect('clicked()',
                                                  lambda: self.onSelectedCollapsibleButtonOpen(
                                                    self.CollapsibleButton_ParaToSPHARMMesh))
    self.OverwriteParaToSPHARMMesh.connect('clicked(bool)', self.onOverwriteFilesParaToSPHARMMesh)
    self.SubdivLevelValue.connect('valueChanged(double)', self.onSubdivLevelValueChanged)
    self.SPHARMDegreeValue.connect('valueChanged(double)', self.onSPHARMDegreeValueChanged)
    self.thetaIterationValue.connect('valueChanged(int)', self.onThetaIterationValueChanged)
    self.phiIterationValue.connect('valueChanged(int)', self.onPhiIterationValueChanged)
    self.medialMesh.connect('clicked(bool)', self.onMedialMeshValueChanged)

    #   Advanced Post Processed Segmentation
    self.CollapsibleButton_AdvancedPostProcessedSegmentation.connect('clicked()',
                                                  lambda: self.onSelectedCollapsibleButtonOpen(
                                                    self.CollapsibleButton_AdvancedPostProcessedSegmentation))
    self.GaussianFiltering.connect('clicked(bool)', self.onSelectGaussianVariance)
    self.VarianceX.connect('valueChanged(double)', self.onVarianceXValueChanged)
    self.VarianceY.connect('valueChanged(double)', self.onVarianceYValueChanged)
    self.VarianceZ.connect('valueChanged(double)', self.onVarianceZValueChanged)

    #   Advanced Parameters to SPHARM Mesh
    self.CollapsibleButton_AdvancedParametersToSPHARMMesh.connect('clicked()',
                                                  lambda: self.onSelectedCollapsibleButtonOpen(
                                                    self.CollapsibleButton_AdvancedParametersToSPHARMMesh))
    self.useRegTemplate.connect('clicked(bool)', self.onEnableRegTemplate)
    self.regTemplate.connect('currentPathChanged(const QString)', self.onRegTemplateValueChanged)
    self.useFlipTemplate.connect('clicked(bool)', self.onEnableFlipTemplate)
    self.flipTemplate.connect('currentPathChanged(const QString)', self.onFlipTemplateValueChanged)
    self.choiceOfFlip.connect('currentIndexChanged(int)', self.onChoiceOfFlipValueChanged)
    self.sameFlipForAll.connect('clicked(bool)', self.onEnableFlipChoices)

    #   Visualization
    self.CollapsibleButton_Visualization.connect('clicked()',
                                                  lambda: self.onSelectedCollapsibleButtonOpen(
                                                    self.CollapsibleButton_Visualization))
    self.CheckableComboBox_visualization.connect('checkedIndexesChanged()', self.onCheckableComboBoxValueChanged)
    self.visualizationInSPV.connect('clicked(bool)', self.onSPHARMMeshesVisualizationInSPV)

    #   Apply CLIs
    self.ApplyButton.connect('clicked(bool)', self.onApplyButton)

    slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, self.onCloseScene)

    # Widget Configuration
    #     Table for the Flip Options
    self.tableWidget_ChoiceOfFlip.setColumnCount(2)
    self.tableWidget_ChoiceOfFlip.setHorizontalHeaderLabels([' Input Files ', ' Choice of Flip '])
    self.tableWidget_ChoiceOfFlip.setColumnWidth(0, 400)
    horizontalHeader = self.tableWidget_ChoiceOfFlip.horizontalHeader()
    horizontalHeader.setStretchLastSection(False)
    horizontalHeader.setResizeMode(0, qt.QHeaderView.Stretch)
    horizontalHeader.setResizeMode(1, qt.QHeaderView.ResizeToContents)
    self.tableWidget_ChoiceOfFlip.verticalHeader().setVisible(False)

    #     Progress Bar
    self.progress_layout.addWidget(self.Logic.ProgressBar)

    #     Table for the visualization in SPV
    self.tableWidget_visualization.setColumnCount(2)
    self.tableWidget_visualization.setHorizontalHeaderLabels([' VTK Files ', ' Visualization '])
    self.tableWidget_visualization.setColumnWidth(0, 400)
    horizontalHeader = self.tableWidget_visualization.horizontalHeader()
    horizontalHeader.setStretchLastSection(False)
    horizontalHeader.setResizeMode(0, qt.QHeaderView.Stretch)
    horizontalHeader.setResizeMode(1, qt.QHeaderView.ResizeToContents)
    self.tableWidget_visualization.verticalHeader().setVisible(False)

    #     Configuration of the parameters of the widget
    self.Logic.parameters.setTableForChoiceOfFlip(self.tableWidget_ChoiceOfFlip)


  def enter(self):
    if not hasattr(slicer.modules, 'shapepopulationviewer') and not hasattr(slicer.modules, 'launcher'):
      messageBox = ctk.ctkMessageBox()
      messageBox.setWindowTitle(' /!\ WARNING /!\ ')
      messageBox.setIcon(messageBox.Warning)
      messageBox.setText("Shape Population Viewer is not installed!")
      messageBox.setInformativeText("To install Shape Population Viewer in order to display the SPHARM meshes outputs generated by Shape Analysis Module, you can:\n"
                                    "Solution 1: \n"
                                    "    - Install it via the Extensions Managers\n"
                                    "    - Restart 3DSlicer\n"
                                    "Solution 2: \n"
                                    "    - Download it on https://www.nitrc.org/projects/shapepopviewer/\n"
                                    "    - Add the folder where you stored it in Edit/Application Settings/Modules/Add\n"
                                    "    - Restart 3DSlicer")
      messageBox.setStandardButtons(messageBox.Ok)
      messageBox.exec_()
    else:
      self.CollapsibleButton_Visualization.enabled = True

  def onCloseScene(self, obj, event):
    #   Group Project IO
    self.CollapsibleButton_GroupProjectIO.setChecked(True)
    self.Logic.InputCases = []
    self.GroupProjectInputDirectory.directory = slicer.app.slicerHome
    self.GroupProjectOutputDirectory.directory = slicer.app.slicerHome
    self.Debug.setChecked(False)

    #   Post Processed Segmentation
    self.CollapsibleButton_SegPostProcess.setChecked(False)
    self.OverwriteSegPostProcess.setChecked(False)
    self.RescaleSegPostProcess.setChecked(True)
    self.sx.setValue(0.5)
    self.sy.setValue(0.5)
    self.sz.setValue(0.5)
    self.LabelState.setChecked(False)
    self.ValueLabelNumber.setValue(0)

    #   Generate Mesh Parameters
    self.CollapsibleButton_GenParaMesh.setChecked(False)
    self.OverwriteGenParaMesh.setChecked(False)
    self.NumberofIterations.setValue(1000)

    #   Parameters to SPHARM Mesh
    self.CollapsibleButton_ParaToSPHARMMesh.setChecked(False)
    self.OverwriteParaToSPHARMMesh.setChecked(False)
    self.SubdivLevelValue.setValue(10)
    self.SPHARMDegreeValue.setValue(15)
    self.thetaIterationValue.setValue(100)
    self.phiIterationValue.setValue(100)
    self.medialMesh.setChecked(False)

    #   Advanced Post Processed Segmentation
    self.CollapsibleButton_AdvancedPostProcessedSegmentation.setChecked(False)
    self.GaussianFiltering.setChecked(False)
    self.VarianceX.setValue(10)
    self.VarianceY.setValue(10)
    self.VarianceZ.setValue(10)

    #   Advanced Parameters to SPHARM Mesh
    self.CollapsibleButton_AdvancedParametersToSPHARMMesh.setChecked(False)
    self.useRegTemplate.setChecked(False)
    self.regTemplate.setCurrentPath(" ")
    self.useFlipTemplate.setChecked(False)
    self.flipTemplate.setCurrentPath(" ")
    self.choiceOfFlip.setCurrentIndex(0)
    self.choiceOfFlip.enabled = True
    self.sameFlipForAll.setChecked(True)
    self.tableWidget_ChoiceOfFlip.enabled = False
    self.tableWidget_ChoiceOfFlip.clear()
    self.tableWidget_ChoiceOfFlip.setColumnCount(2)
    self.tableWidget_ChoiceOfFlip.setHorizontalHeaderLabels([' Input Files ', ' Choice of Flip '])
    self.tableWidget_ChoiceOfFlip.setColumnWidth(0, 400)
    horizontalHeader = self.tableWidget_ChoiceOfFlip.horizontalHeader()
    horizontalHeader.setStretchLastSection(False)
    horizontalHeader.setResizeMode(0, qt.QHeaderView.Stretch)
    horizontalHeader.setResizeMode(1, qt.QHeaderView.ResizeToContents)
    self.tableWidget_ChoiceOfFlip.verticalHeader().setVisible(False)

    #   Visualization
    self.CollapsibleButton_Visualization.setChecked(False)
    self.CheckableComboBox_visualization.model().clear()
    self.tableWidget_visualization.clear()
    self.tableWidget_visualization.setColumnCount(2)
    self.tableWidget_visualization.setHorizontalHeaderLabels([' VTK Files ', ' Visualization '])
    self.tableWidget_visualization.setColumnWidth(0, 400)
    horizontalHeader = self.tableWidget_visualization.horizontalHeader()
    horizontalHeader.setStretchLastSection(False)
    horizontalHeader.setResizeMode(0, qt.QHeaderView.Stretch)
    horizontalHeader.setResizeMode(1, qt.QHeaderView.ResizeToContents)
    self.tableWidget_visualization.verticalHeader().setVisible(False)

    # Apply
    if self.ApplyButton.text == "Cancel":
      self.ApplyButton.click()
    self.Logic.ProgressBar.hide()
    if self.progressbars_layout:
      self.CLIProgressBars.hide()

  # Functions to recover the widget in the .ui file
  def getWidget(self, objectName):
    return self.findWidget(self.widget, objectName)

  def findWidget(self, widget, objectName):
    if widget.objectName == objectName:
      return widget
    else:
      for w in widget.children():
        resulting_widget = self.findWidget(w, objectName)
        if resulting_widget:
          return resulting_widget
    return None

  # Only one tab can be displayed at the same time:
  #   When one tab is opened all the other tabs are closed
  def onSelectedCollapsibleButtonOpen(self, selectedCollapsibleButton):
    if selectedCollapsibleButton.isChecked():
      collapsibleButtonList = [self.CollapsibleButton_GroupProjectIO,
                               self.CollapsibleButton_SegPostProcess,
                               self.CollapsibleButton_GenParaMesh,
                               self.CollapsibleButton_ParaToSPHARMMesh,
                               self.CollapsibleButton_AdvancedPostProcessedSegmentation,
                               self.CollapsibleButton_AdvancedParametersToSPHARMMesh,
                               self.CollapsibleButton_Visualization]
      for collapsibleButton in collapsibleButtonList:
        collapsibleButton.setChecked(False)
      selectedCollapsibleButton.setChecked(True)

  #
  #   Group Project IO
  #
  def onInputDirectoryChanged(self):
    inputDirectory = self.GroupProjectInputDirectory.directory.encode('utf-8')

    # Update of the input directory path
    self.Logic.parameters.setInputDirectory(inputDirectory)

    #  Possible extensions
    exts = [".gipl", ".gipl.gz", ".mgh", ".mgh,gz", ".nii", ".nii.gz",".nrrd", ".vtk", ".vtp", ".hdr", ".mhd"]

    # Search cases and add the filename to a list
    self.Logic.InputCases = []
    for file in os.listdir(inputDirectory):
      for ext in exts:
        if file.endswith(ext):
          self.Logic.InputCases.append(file)
          if file.endswith(".nii") or file.endswith(".nii.gz"):
            self.RescaleSegPostProcess.setCheckState(qt.Qt.Unchecked)
            self.label_RescaleSegPostProcess.enabled = False
            self.RescaleSegPostProcess.enabled = False

  # Update of the output directory path
  def onOutputDirectoryChanged(self):
    outputDirectory = self.GroupProjectOutputDirectory.directory.encode('utf-8')
    self.Logic.parameters.setOutputDirectory(outputDirectory)

  # Update of the debug parameter
  def onDebug(self):
    self.Logic.parameters.setDebug(self.Debug.checkState())

  #
  #   Post Processed Segmentation
  #
  def onOverwriteFilesSegPostProcess(self):
    # Update of the overwrite boolean for the Post Processed Segmentation step
    self.Logic.parameters.setOverwriteSegPostProcess(self.OverwriteSegPostProcess.checkState())

    if self.OverwriteSegPostProcess.checkState():
      #   Message for the user
      messageBox = ctk.ctkMessageBox()
      messageBox.setWindowTitle(' /!\ WARNING /!\ ')
      messageBox.setIcon(messageBox.Warning)
      messageBox.setText("<p align='center'>Applying the overwrite option to Post Processed Segmentation step will also apply to the next steps</p>")
      messageBox.setStandardButtons(messageBox.Ok)
      messageBox.exec_()
      #   Check the overwrite option for the next steps
      self.OverwriteGenParaMesh.setCheckState(qt.Qt.Checked)
      self.Logic.parameters.setOverwriteGenParaMesh(self.OverwriteGenParaMesh.checkState())
      self.OverwriteParaToSPHARMMesh.setCheckState(qt.Qt.Checked)
      self.Logic.parameters.setOverwriteParaToSPHARMMesh(self.OverwriteParaToSPHARMMesh.checkState())

  def onSelectSpacing(self):
    # Update of the rescale boolean for the Post Processed Segmentation step
    self.Logic.parameters.setRescaleSegPostProcess(self.RescaleSegPostProcess.checkState())

    # Enable/Disable the spacing x,y, and z parameters in the UI
    self.label_sx.enabled = self.RescaleSegPostProcess.checkState()
    self.label_sy.enabled = self.RescaleSegPostProcess.checkState()
    self.label_sz.enabled = self.RescaleSegPostProcess.checkState()
    self.sx.enabled = self.RescaleSegPostProcess.checkState()
    self.sy.enabled = self.RescaleSegPostProcess.checkState()
    self.sz.enabled = self.RescaleSegPostProcess.checkState()

  # Update of the spacing x parameter for the Post Processed Segmentation step
  def onSxValueChanged(self):
    self.Logic.parameters.setSx(self.sx.value)

  # Update of the spacing y parameter for the Post Processed Segmentation step
  def onSyValueChanged(self):
    self.Logic.parameters.setSy(self.sy.value)

  # Update of the spacing z parameter for the Post Processed Segmentation step
  def onSzValueChanged(self):
    self.Logic.parameters.setSz(self.sz.value)

  # Enable/Disable the label number value in the UI
  def onSelectValueLabelNumber(self):
    self.label_ValueLabelNumber.enabled = self.LabelState.checkState()
    self.ValueLabelNumber.enabled = self.LabelState.checkState()

  # Update of the label parameter for the Post Processed Segmentation step
  def onLabelNumberValueChanged(self):
    self.Logic.parameters.setLabelNumber(self.ValueLabelNumber.value)

  #
  #   Generate Mesh Parameters
  #
  def onOverwriteFilesGenParaMesh(self):
    # If the overwrite option for GenParaMesh is unchecked
    if not self.OverwriteGenParaMesh.checkState():
      #   If the overwrite option for the previous step is checked, the overwrite option need to be checked for this step too
      if self.OverwriteSegPostProcess.checkState():
        self.OverwriteGenParaMesh.setCheckState(qt.Qt.Checked)
        #   Message for the user
        messageBox = ctk.ctkMessageBox()
        messageBox.setWindowTitle(' /!\ WARNING /!\ ')
        messageBox.setIcon(messageBox.Warning)
        messageBox.setText("<p align='center'>The overwrite option need to be applied to this step as it is set for the previous step</p>")
        messageBox.setStandardButtons(messageBox.Ok)
        messageBox.exec_()
    # If the overwrite option for GenParaMesh is checked
    else:
      #   Message for the user
      messageBox = ctk.ctkMessageBox()
      messageBox.setWindowTitle(' /!\ WARNING /!\ ')
      messageBox.setIcon(messageBox.Warning)
      messageBox.setText("<p align='center'>Applying the overwrite option to Generate Mesh Parameters step will also apply to the next steps</p>")
      messageBox.setStandardButtons(messageBox.Ok)
      messageBox.exec_()
      #   Check the overwrite option for the next step
      self.OverwriteParaToSPHARMMesh.setCheckState(qt.Qt.Checked)
      self.Logic.parameters.setOverwriteParaToSPHARMMesh(self.OverwriteParaToSPHARMMesh.checkState())

    # Update of the overwrite boolean for the Generate Mesh Parameters step
    self.Logic.parameters.setOverwriteGenParaMesh(self.OverwriteGenParaMesh.checkState())


  # Update of the iterations parameter for the Generate Mesh Parameters step
  def onNumberofIterationsValueChanged(self):
    self.Logic.parameters.setNumberofIterations(self.NumberofIterations.value)

  #
  #   Parameters to SPHARM Mesh
  #
  def onOverwriteFilesParaToSPHARMMesh(self):
    # If the overwrite option for ParaToSPHARMMesh is unchecked
    if not self.OverwriteParaToSPHARMMesh.checkState():
      #   If the overwrite option for a previous step is checked, the overwrite option need to be checked for this step too
      if self.OverwriteSegPostProcess.checkState() or self.OverwriteGenParaMesh.checkState():
        self.OverwriteParaToSPHARMMesh.setCheckState(qt.Qt.Checked)
        #   Message for the user
        messageBox = ctk.ctkMessageBox()
        messageBox.setWindowTitle(' /!\ WARNING /!\ ')
        messageBox.setIcon(messageBox.Warning)
        messageBox.setText("<p align='center'>The overwrite option need to be applied to this step as it is set for the previous step</p>")
        messageBox.setStandardButtons(messageBox.Ok)
        messageBox.exec_()

    # Update of the overwrite boolean for the Parameters to SPHARM Mesh step
    self.Logic.parameters.setOverwriteParaToSPHARMMesh(self.OverwriteParaToSPHARMMesh.checkState())

  # Update of the sub-division parameter for the Parameters to SPHARM Mesh step
  def onSubdivLevelValueChanged(self):
    self.Logic.parameters.setSubdivLevelValue(self.SubdivLevelValue.value)

  # Update of the SPHARM degree parameter for the Parameters to SPHARM Mesh step
  def onSPHARMDegreeValueChanged(self):
    self.Logic.parameters.setSPHARMDegreeValue(self.SPHARMDegreeValue.value)

  # Update of the theta iteration parameter for the Parameters to SPHARM Mesh step
  def onThetaIterationValueChanged(self):
    self.Logic.parameters.setThetaIterationValue(self.thetaIterationValue.value)

  # Update of the phi iteration parameter for the Parameters to SPHARM Mesh step
  def onPhiIterationValueChanged(self):
    self.Logic.parameters.setPhiIterationValue(self.phiIterationValue.value)

  # Update of the medial mesh boolean for the Parameters to SPHARM Mesh step
  def onMedialMeshValueChanged(self):
    self.Logic.parameters.setMedialMesh(self.medialMesh.checkState())

  #
  #   Advanced Post Processed Segmentation
  #
  def onSelectGaussianVariance(self):
    # Update of the gaussian variance boolean for the Post Processed Segmentation step
    self.Logic.parameters.setGaussianFiltering(self.GaussianFiltering.checkState())

    # Enable/Disable the gaussian variance parameters in the UI
    self.label_VarianceX.enabled = self.GaussianFiltering.checkState()
    self.VarianceX.enabled = self.GaussianFiltering.checkState()
    self.label_VarianceY.enabled = self.GaussianFiltering.checkState()
    self.VarianceY.enabled = self.GaussianFiltering.checkState()
    self.label_VarianceZ.enabled = self.GaussianFiltering.checkState()
    self.VarianceZ.enabled = self.GaussianFiltering.checkState()

  # Update of the variance x parameter for the Post Processed Segmentation step
  def onVarianceXValueChanged(self):
    self.Logic.parameters.setVarianceX(self.VarianceX.value)

  # Update of the variance y parameter for the Post Processed Segmentation step
  def onVarianceYValueChanged(self):
    self.Logic.parameters.setVarianceY(self.VarianceY.value)

  # Update of the variance z parameter for the Post Processed Segmentation step
  def onVarianceZValueChanged(self):
    self.Logic.parameters.setVarianceZ(self.VarianceZ.value)

  #
  #   Advanced Parameters to SPHARM Mesh
  #
  def onEnableRegTemplate(self):
    # Update of the registration template boolean for the Parameters to SPHARM Mesh step
    self.Logic.parameters.setUseRegTemplate(self.useRegTemplate.checkState())

    # Enable/Disable the registration template path in the UI
    self.label_regTemplate.enabled = self.useRegTemplate.checkState()
    self.regTemplate.enabled = self.useRegTemplate.checkState()

  # Update of the registration template path for the Parameters to SPHARM Mesh step
  def onRegTemplateValueChanged(self):
    self.Logic.parameters.setRegTemplate(self.regTemplate.currentPath)

  def onEnableFlipTemplate(self):
    # Update of the flip template boolean for the Parameters to SPHARM Mesh step
    self.Logic.parameters.setUseFlipTemplate(self.useFlipTemplate.checkState())

    # Enable/Disable the flip template path in the UI
    self.label_flipTemplate.enabled = self.useFlipTemplate.checkState()
    self.flipTemplate.enabled = self.useFlipTemplate.checkState()

  # Update of the flip template path for the Parameters to SPHARM Mesh step
  def onFlipTemplateValueChanged(self):
    self.Logic.parameters.setFlipTemplate(self.flipTemplate.currentPath)

  # Update of the flip parameter for the Parameters to SPHARM Mesh step
  def onChoiceOfFlipValueChanged(self):
    self.Logic.parameters.setChoiceOfFlip(self.choiceOfFlip.currentIndex)

  def onEnableFlipChoices(self):
    # Update of the flip option boolean for the Parameters to SPHARM Mesh step
    self.Logic.parameters.setSameFlipForAll(self.sameFlipForAll.checkState())

    self.choiceOfFlip.enabled = self.sameFlipForAll.checkState()
    self.tableWidget_ChoiceOfFlip.enabled = not self.sameFlipForAll.checkState()
    if not self.sameFlipForAll.checkState():
      self.fillTableForFlipOptions()

  #
  #   Apply CLIs
  #
  def onApplyButton(self):
    # Run workflow
    if not self.Logic.Node.IsBusy():

      # Check the registration template file
      if self.useRegTemplate.checkState():
        if not os.path.exists(self.regTemplate.currentPath) or not self.regTemplate.currentPath.endswith(".vtk"):
          slicer.util.errorDisplay("Invalid registration template file in Advanced Parameters to SPHARM Mesh Tab")
          return

      # Check the flip template file
      if self.useFlipTemplate.checkState():
        if not os.path.exists(self.flipTemplate.currentPath) or not self.flipTemplate.currentPath.endswith(".coef"):
          slicer.util.errorDisplay("Invalid flip template file in Advanced Parameters to SPHARM Mesh Tab")
          return

      # Empty the output folders if the overwrite options  are checked
      self.Logic.cleanOutputFolders()

      # Change the apply buttons
      logging.info('Widget: Running ShapeAnalysisModule')
      self.ApplyButton.setText("Cancel")

      self.Logic.addObserver(self.Logic.Node, slicer.vtkMRMLCommandLineModuleNode().StatusModifiedEvent,
                             self.onLogicModified)

      self.Logic.Node.SetStatus(self.Logic.Node.Scheduled)
      self.Logic.allCaseStartTime = time.time()

      self.Logic.ShapeAnalysisCases()

    # Cancel Workflow
    else:
      logging.info("Widget: Cancelling ShapeAnalysisModule")
      self.ApplyButton.setEnabled(False)
      self.Logic.Cancel()

  def onLogicModified(self, logic_node, event):
    status = logic_node.GetStatusString()
    logging.info('-- %s : ShapeAnalysisModule', status)

    # if not busy (completed, error, cancelled)
    if not logic_node.IsBusy():
      self.Logic.removeObserver(logic_node, slicer.vtkMRMLCommandLineModuleNode().StatusModifiedEvent,
                                self.onLogicModified)
      # Create Error Message
      if status == 'Completed with errors' or status == 'Cancelled':
        logging.error(self.Logic.ErrorMessage)
        qt.QMessageBox.critical(slicer.util.mainWindow(),
                                'ShapeAnalysisModule',
                                self.Logic.ErrorMessage)

      elif status == 'Completed':
        self.configurationVisualization()

      #  Empty lists
      self.Logic.pipeline = {}
      self.Logic.completed = {}

      # Change the apply buttons
      self.ApplyButton.setEnabled(True)
      self.ApplyButton.setText("Run ShapeAnalysisModule")

    # if running, create some progress bars for each cases
    elif status == 'Running':
      self.Logic.ProgressBar.show()
      if self.progressbars_layout:
        self.CLIProgressBars.hide()
      self.CLIProgressBars = ctk.ctkCollapsibleGroupBox()
      self.CLIProgressBars.setTitle('Detail')
      self.progress_layout.addWidget(self.CLIProgressBars)
      self.progressbars_layout = qt.QVBoxLayout(self.CLIProgressBars)
      for i in range(len(self.Logic.pipeline)):
        self.progressbars_layout.addWidget(self.Logic.pipeline[i].ProgressBar)

  # Function to update the checkable comboBox and the table's checkBoxes in the visualization tab according of the check of one checkBox in the checkable comboBox
  def onCheckableComboBoxValueChanged(self):
    currentText = self.CheckableComboBox_visualization.currentText
    currentIndex = self.CheckableComboBox_visualization.currentIndex
    currentItem = self.CheckableComboBox_visualization.model().item(currentIndex, 0)

    # ******* Update the CheckableComboBox ******* #
    #     Check/Uncheck the "Case i: case_name [..]" checkboxes in the checkacle comboBox
    if currentText == "All Models":
      self.checkedItems("SPHARM", currentItem.checkState())

    elif currentText == "All SPHARM Models":
      self.checkedItems("SPHARM Models", currentItem.checkState())

    elif currentText == "All SPHARM Ellipse Aligned Models":
      self.checkedItems("SPHARM Ellipse Aligned Models", currentItem.checkState())

    elif currentText == "All SPHARM Medial Meshes":
      self.checkedItems("SPHARM Medial Meshes", currentItem.checkState())

    elif currentText == "All SPHARM Procrustes Aligned Models":
      self.checkedItems("SPHARM Procrustes Aligned Models", currentItem.checkState())

    #     Check/Uncheck the "All [..]" checkboxes in the checkacle comboBox
    self.checkedAllItems()

    self.CheckableComboBox_visualization.blockSignals(False)

    # ******* Update the checkboxes in the table ******* #
    for row in range(0, self.tableWidget_visualization.rowCount):
      actionOnCheckBox = False
      label = self.tableWidget_visualization.cellWidget(row, 0)
      outputBasename = label.text
      if currentText == "All Models":
        actionOnCheckBox = True

      elif currentText == "All SPHARM Models":
        if not outputBasename.find("SPHARM") == -1 and outputBasename.find("SPHARM_ellalign") == -1 and outputBasename.find("SPHARMMedialMesh") == -1 and outputBasename.find("SPHARM_procalign") == -1:
          actionOnCheckBox = True

      elif currentText == "All SPHARM Ellipse Aligned Models":
        if not outputBasename.find("SPHARM_ellalign") == -1:
          actionOnCheckBox = True

      elif currentText == "All SPHARM Medial Meshes":
        if not outputBasename.find("SPHARMMedialMesh") == -1:
          actionOnCheckBox = True

      elif currentText == "All SPHARM Procrustes Aligned Models":
        if not outputBasename.find("SPHARM_procalign") == -1:
          actionOnCheckBox = True

      else:
        for inputFilename in self.Logic.InputCases:
          inputBasename = inputFilename.split('/')[-1].split('.')[0]
          if not currentText.find(inputBasename) == -1:
            if not currentText.find("SPHARM Models") == -1:
              if not outputBasename.find(inputBasename) == -1 and not outputBasename.find("SPHARM") == -1 and outputBasename.find("SPHARM_ellalign") == -1 and outputBasename.find("SPHARMMedialMesh") == -1 and outputBasename.find("SPHARM_procalign") == -1:
                actionOnCheckBox = True
            elif not currentText.find("SPHARM Ellipse Aligned Models") == -1:
              if not outputBasename.find(inputBasename) == -1 and not outputBasename.find("SPHARM_ellalign") == -1:
                actionOnCheckBox = True
            elif not currentText.find("SPHARM Medial Meshes") == -1:
              if not outputBasename.find(inputBasename) == -1 and not outputBasename.find("SPHARMMedialMesh") == -1:
                actionOnCheckBox = True
            elif not currentText.find("SPHARM Procrustes Aligned Models") == -1:
              if not outputBasename.find(inputBasename) == -1 and not outputBasename.find("SPHARM_procalign") == -1:
                actionOnCheckBox = True

      # check/uncheck the checkBox at (row,1)
      if actionOnCheckBox:
          widget = self.tableWidget_visualization.cellWidget(row, 1)
          tuple = widget.children()
          checkBox = tuple[1]
          checkBox.blockSignals(True)
          item = self.CheckableComboBox_visualization.model().item(currentIndex, 0)
          if item.checkState():
            checkBox.setChecked(True)
          else:
            checkBox.setChecked(False)
          checkBox.blockSignals(False)

  # Function to update the checkboxes in the checkbable comboBox in the visualization tab according of the check of a checBox in the visualization tab
  def onCheckBoxTableValueChanged(self):
    self.CheckableComboBox_visualization.blockSignals(True)
    list = self.CheckableComboBox_visualization.model()
    table = self.tableWidget_visualization

    allSPHARMMesdialMeshesIndex = self.CheckableComboBox_visualization.findText("All SPHARM Medial Meshes") # If == -1 "All SPHARM Medial Meshes" checkBox doesn't exist
    allSPHARMProcrustesAlignedModelsIndex = self.CheckableComboBox_visualization.findText("All SPHARM Procrustes Aligned Models") # If == -1 "All SPHARM Procrustes Aligned Models" checkBox doesn't exist

    for i in range(len(self.Logic.InputCases)):
      allCaseSPHARMModelsChecked = True
      allCaseSPHARMEllalignModelsChecked = True
      allCaseSPHARMMedialMeshesChecked = True
      allCaseSPHARMProcrustesAlignedModelsChecked = True

      inputBasename = self.Logic.InputCases[i].split('/')[-1].split('.')[0]
      for row in range(0,table.rowCount):
        label = table.cellWidget(row, 0)
        outputBasename = label.text
        if not outputBasename.find(inputBasename) == -1:
          widget = table.cellWidget(row, 1)
          tuple = widget.children()
          checkBox = tuple[1]
          if not checkBox.checkState():
            if not outputBasename.find("SPHARM") == -1 and outputBasename.find("SPHARM_ellalign") == -1 and outputBasename.find("SPHARMMedialMesh") == -1 and outputBasename.find("SPHARM_procalign") == -1:
              allCaseSPHARMModelsChecked = False

            if not outputBasename.find("SPHARM_ellalign") == -1:
              allCaseSPHARMEllalignModelsChecked = False

            if not allSPHARMMesdialMeshesIndex == -1:
              if not outputBasename.find("SPHARMMedialMesh") == -1:
                allCaseSPHARMMedialMeshesChecked = False

            if not allSPHARMProcrustesAlignedModelsIndex == -1:
              if not outputBasename.find("SPHARM_procalign") == -1:
                allCaseSPHARMProcrustesAlignedModelsChecked = False

      # Check/uncheck checbox case according of the checkbox in the table
      text = "Case " + str(i) + ": " + inputBasename + " - SPHARM Models"
      self.checkedCaseItem(text, allCaseSPHARMModelsChecked)

      text = "Case " + str(i) + ": " + inputBasename + " - SPHARM Ellipse Aligned Models"
      self.checkedCaseItem(text, allCaseSPHARMEllalignModelsChecked)

      if not allSPHARMMesdialMeshesIndex == -1:
        text = "Case " + str(i) + ": " + inputBasename + " - SPHARM Medial Meshes"
        self.checkedCaseItem(text, allCaseSPHARMMedialMeshesChecked)

      if not allSPHARMProcrustesAlignedModelsIndex == -1:
        text = "Case " + str(i) + ": " + inputBasename + " - SPHARM Procrustes Aligned Models"
        self.checkedCaseItem(text, allCaseSPHARMProcrustesAlignedModelsChecked)

    # Check/Uncheck the "All [..]" checkboxes in the checkacle comboBox
    self.checkedAllItems()

    self.CheckableComboBox_visualization.blockSignals(False)

  # Visualization of the SPHARM Mesh outputs in Shape Population Viewer
  def onSPHARMMeshesVisualizationInSPV(self):
    # Creation of a CSV file to load the vtk files in ShapePopulationViewer
    filePathCSV = slicer.app.temporaryPath + '/' + 'PreviewForVisualizationInSPV.csv'
    self.Logic.creationCSVFileForSPV(self.tableWidget_visualization, filePathCSV)

    # Creation of the parameters of SPV
    parameters = {}
    parameters["CSVFile"] = filePathCSV

    #   If a binary of SPV has been installed
    if hasattr(slicer.modules, 'shapepopulationviewer'):
      SPV = slicer.modules.shapepopulationviewer
    #   If SPV has been installed via the Extension Manager
    elif hasattr(slicer.modules, 'launcher'):
      SPV = slicer.modules.launcher
    # Launch SPV
    slicer.cli.run(SPV, None, parameters, wait_for_completion=True)

    # Deletion of the CSV files in the Slicer temporary directory
    if os.path.exists(filePathCSV):
      os.remove(filePathCSV)

  # Function to fill the flip options table for all the SPHARM mesh outputs
  #    - Column 0: filename of the input files
  #    - Column 1: comboBox with the flip corresponding to the output file
  def fillTableForFlipOptions(self):
    table = self.tableWidget_ChoiceOfFlip
    row = 0

    for basename in self.Logic.InputCases:
      table.setRowCount(row + 1)
      # Column 0:
      filename = basename.split('/')[-1].split('.')[0]
      labelVTKFile = qt.QLabel(filename)
      labelVTKFile.setAlignment(0x84)
      table.setCellWidget(row, 0, labelVTKFile)

      # Column 1:
      widget = qt.QWidget()
      layout = qt.QHBoxLayout(widget)
      comboBox = qt.QComboBox()
      comboBox.addItems(['No Flip',
                         'Flip Along Axis of x and y',
                         'Flip Along Axis of y and z',
                         'Flip Along Axis of x and z',
                         'Flip Along Axis of x',
                         'Flip Along Axis of y',
                         'Flip Along Axis of x, y and z',
                         'Flip Along Axis of z',
                         'All'])
      comboBox.setCurrentIndex(self.choiceOfFlip.currentIndex)
      layout.addWidget(comboBox)
      layout.setAlignment(0x84)
      layout.setContentsMargins(0, 0, 0, 0)
      widget.setLayout(layout)
      table.setCellWidget(row, 1, widget)

      row = row + 1

  # Function to configure the checkable comboBox and the table of the visualization tab
  def configurationVisualization(self):
    # Configuration of the checkable comboBox
    checkableComboBox = self.CheckableComboBox_visualization
    #   clean the checkable comboBox
    list = checkableComboBox.model()
    list.clear()
    #   add items according of the SPHARM Mesh computed by ParaToSPHARMMesh
    checkableComboBox.blockSignals(True)
    checkableComboBox.addItem("All Models")
    checkableComboBox.addItem("All SPHARM Models")
    checkableComboBox.addItem("All SPHARM Ellipse Aligned Models")
    if self.medialMesh.checkState():
      checkableComboBox.addItem("All SPHARM Medial Meshes")
    if self.useRegTemplate.checkState():
      checkableComboBox.addItem("All SPHARM Procrustes Aligned Models")
    # Fill the checkable comboBox
    for i in range(len(self.Logic.InputCases)):
      checkableComboBox.addItem("Case " + str(i) + ": " + self.Logic.InputCases[i].split('/')[-1].split('.')[0] + " - SPHARM Models")
      checkableComboBox.addItem("Case " + str(i) + ": " + self.Logic.InputCases[i].split('/')[-1].split('.')[0] + " - SPHARM Ellipse Aligned Models")
      if self.medialMesh.checkState():
        checkableComboBox.addItem("Case " + str(i) + ": " + self.Logic.InputCases[i].split('/')[-1].split('.')[0] + " - SPHARM Medial Meshes")
      if self.useRegTemplate.checkState():
        checkableComboBox.addItem("Case " + str(i) + ": " + self.Logic.InputCases[i].split('/')[-1].split('.')[0] + " - SPHARM Procrustes Aligned Models")
    checkableComboBox.blockSignals(False)

    # Configuration of the table
    #   column 0: filename of the SPHARM Meshes generated by ParaToSPHARMMesh
    #   column 1: checkbox that allows to the user to select what output he wants to display in Shape Population Viewer
    table = self.tableWidget_visualization
    outputDirectory = self.GroupProjectOutputDirectory.directory.encode('utf-8')
    SPHARMMeshOutputDirectory = outputDirectory + "/Step3_ParaToSPHARMMesh/"
    row = 0

    for filename in os.listdir(SPHARMMeshOutputDirectory):
      if filename.endswith(".vtk") and not filename.endswith("_para.vtk") and not filename.endswith("SPHARMMedialAxis.vtk"):
        table.setRowCount(row + 1)
        # Column 0:
        labelVTKFile = qt.QLabel(os.path.splitext(filename)[0])
        labelVTKFile.setAlignment(0x84)
        table.setCellWidget(row, 0, labelVTKFile)

        # Column 1:
        widget = qt.QWidget()
        layout = qt.QHBoxLayout(widget)
        checkBox = qt.QCheckBox()
        layout.addWidget(checkBox)
        layout.setAlignment(0x84)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        table.setCellWidget(row, 1, widget)
        checkBox.connect('stateChanged(int)', self.onCheckBoxTableValueChanged)

        row = row + 1

  # Functions to update the checkable comboBox in the visualization tab
  #     Check/Uncheck checkBoxes with the label 'text'
  def checkedItems(self, text, checkState):
    list = self.CheckableComboBox_visualization.model()
    for i in range(1, list.rowCount()):
      item = list.item(i, 0)
      if not item.text().find(text) == -1:
        item.setCheckState(checkState)

  # Check/Uncheck "All [..]" checkBoxes in the checkable comboBox
  def checkedAllItems(self):
    list = self.CheckableComboBox_visualization.model()

    allIndex = self.CheckableComboBox_visualization.findText("All Models")
    allItem = list.item(allIndex, 0)
    allSPHARMIndex = self.CheckableComboBox_visualization.findText("All SPHARM Models")
    allSPHARMItem = list.item(allSPHARMIndex, 0)
    allSPHARMEllalignIndex = self.CheckableComboBox_visualization.findText("All SPHARM Ellipse Aligned Models")
    allSPHARMEllalignItem = list.item(allSPHARMEllalignIndex, 0)
    allSPHARMMesdialMeshesIndex = self.CheckableComboBox_visualization.findText("All SPHARM Medial Meshes")
    if not allSPHARMMesdialMeshesIndex == -1:
      allSPHARMMesdialMeshesItem = list.item(allSPHARMMesdialMeshesIndex, 0)
    allSPHARMProcrustesAlignedModelsIndex = self.CheckableComboBox_visualization.findText("All SPHARM Procrustes Aligned Models")
    if not allSPHARMProcrustesAlignedModelsIndex == -1:
      allSPHARMProcrustesAlignedModelsItem = list.item(allSPHARMProcrustesAlignedModelsIndex, 0)

    # Check/Uncheck "All SPHARM Models" checkBox
    self.checkedAllItem("- SPHARM Models", allSPHARMItem)
    # Check/Uncheck "All SPHARM Ellipse Aligned Models" checkBox
    self.checkedAllItem("- SPHARM Ellipse Aligned Models", allSPHARMEllalignItem)
    # Check/Uncheck "All SPHARM Medial Mesh" checkBox
    if not allSPHARMMesdialMeshesIndex == -1:
      self.checkedAllItem("- SPHARM Medial Meshes", allSPHARMMesdialMeshesItem)
    # Check/Uncheck "All SPHARM Procrustes Aligned Models" checkBox
    if not allSPHARMProcrustesAlignedModelsIndex == -1:
      self.checkedAllItem("- SPHARM Procrustes Aligned Models", allSPHARMProcrustesAlignedModelsItem)

    # Check/Uncheck "All Models" checkBox
    if allSPHARMEllalignItem.checkState() and allSPHARMItem.checkState():
      if allSPHARMMesdialMeshesIndex == -1 and allSPHARMProcrustesAlignedModelsIndex == -1:
        allItem.setCheckState(qt.Qt.Checked)
        return
      elif not allSPHARMMesdialMeshesIndex == -1 and not allSPHARMProcrustesAlignedModelsIndex == -1:
        if allSPHARMMesdialMeshesItem.checkState() and allSPHARMProcrustesAlignedModelsItem.checkState():
          allItem.setCheckState(qt.Qt.Checked)
          return
      elif not allSPHARMMesdialMeshesIndex == -1 and allSPHARMProcrustesAlignedModelsIndex == -1:
        if allSPHARMMesdialMeshesItem.checkState():
          allItem.setCheckState(qt.Qt.Checked)
          return
      elif allSPHARMMesdialMeshesIndex == -1 and not allSPHARMProcrustesAlignedModelsIndex == -1:
        if allSPHARMProcrustesAlignedModelsItem.checkState():
          allItem.setCheckState(qt.Qt.Checked)
          return

    allItem.setCheckState(qt.Qt.Unchecked)

  # Check/Uncheck "Case i: case_name - SPHARM [..]" checkBox in the checkable comboBox
  def checkedCaseItem(self, text, doCheck):
    list = self.CheckableComboBox_visualization.model()
    item = list.findItems(text)[0]
    if doCheck:
      item.setCheckState(qt.Qt.Checked)
    else:
      item.setCheckState(qt.Qt.Unchecked)

  # Check/Uncheck "All [..]" (except "All Models") checkBox in the checkable comboBox
  def checkedAllItem(self, text, item):
    if self.areAllCasesChecked(text):
      item.setCheckState(qt.Qt.Checked)
    else:
      item.setCheckState(qt.Qt.Unchecked)

  # Specify if all the "Case i: case_name - SPHARM [..]" checkBoxes of one type of Model are checked
  def areAllCasesChecked(self, text):
    list = self.CheckableComboBox_visualization.model()
    isChecked = True
    for i in range(3, list.rowCount()):
      item = list.item(i, 0)
      if not item.text().find(text) == -1:
        if not item.checkState():
          isChecked = False
    return isChecked

  def clearFlipOptionsTable(self):
    table = self.tableWidget_ChoiceOfFlip
    table.clear()
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels([' Files ', ' Choice of Flip '])
    table.setColumnWidth(0, 400)
    horizontalHeader = table.horizontalHeader()
    horizontalHeader.setStretchLastSection(False)
    horizontalHeader.setResizeMode(0, qt.QHeaderView.Stretch)
    horizontalHeader.setResizeMode(1, qt.QHeaderView.ResizeToContents)
    table.verticalHeader().setVisible(False)

#
# ShapeAnalysisModuleParameters
#
class ShapeAnalysisModuleParameters(object):
  def __init__(self):
    #   Group Project IO
    self.inputDirectory = " "
    self.outputDirectory = " "
    self.debug = False

    #   Post Processed Segmentation
    self.OverwriteSegPostProcess = False
    self.RescaleSegPostProcess = True
    self.sx = 0.5
    self.sy = 0.5
    self.sz = 0.5

    self.labelNumber = 0

    #   Generate Mesh Parameters
    self.OverwriteGenParaMesh = False
    self.NumberofIterations = 1000

    #   Parameters to SPHARM Mesh
    self.OverwriteParaToSPHARMMesh = False
    self.SubdivLevelValue = 10
    self.SPHARMDegreeValue = 15
    self.thetaIterationValue = 100
    self.phiIterationValue = 100
    self.medialMesh = False

    self.tableWidget_ChoiceOfFlip = None

    #   Advanced Post Processed Segmentation
    self.GaussianFiltering = False
    self.VarianceX = 10
    self.VarianceY = 10
    self.VarianceZ = 10

    #   Advanced Parameters to SPHARM Mesh
    self.useRegTemplate = False
    self.regTemplate = " "
    self.useFlipTemplate = False
    self.flipTemplate = " "
    self.choiceOfFlip = 0
    self.sameFlipForAll = True

  def setInputDirectory(self, path):
    self.inputDirectory = path

  def setOutputDirectory(self, path):
    self.outputDirectory = path

  def setDebug(self, bool):
    self.debug = bool

  def setOverwriteSegPostProcess(self, bool):
    self.OverwriteSegPostProcess = bool

  def setRescaleSegPostProcess(self, bool):
    self.RescaleSegPostProcess = bool

  def setSx(self, value):
    self.sx = value

  def setSy(self, value):
    self.sy = value

  def setSz(self, value):
    self.sz = value

  def setLabelNumber(self, value):
    self.labelNumber = value

  def setOverwriteGenParaMesh(self, bool):
    self.OverwriteGenParaMesh = bool

  def setNumberofIterations(self, value):
    self.NumberofIterations = value

  def setOverwriteParaToSPHARMMesh(self, bool):
    self.OverwriteParaToSPHARMMesh = bool

  def setSubdivLevelValue(self, value):
    self.SubdivLevelValue = value

  def setSPHARMDegreeValue(self, value):
    self.SPHARMDegreeValue = value

  def setThetaIterationValue(self, value):
    self.thetaIterationValue = value

  def setPhiIterationValue(self, value):
    self.phiIterationValue = value

  def setMedialMesh(self, bool):
    self.medialMesh = bool

  def setTableForChoiceOfFlip(self, table):
    self.tableWidget_ChoiceOfFlip = table

  def setGaussianFiltering(self, bool):
    self.GaussianFiltering = bool

  def setVarianceX(self, value):
    self.VarianceX = value

  def setVarianceY(self, value):
    self.VarianceY = value

  def setVarianceZ(self, value):
    self.VarianceZ = value

  def setUseRegTemplate(self, bool):
    self.useRegTemplate = bool

  def setRegTemplate(self, path):
    self.regTemplate = path

  def setUseFlipTemplate(self, bool):
    self.useFlipTemplate = bool

  def setFlipTemplate(self, path):
    self.flipTemplate = path

  def setChoiceOfFlip(self, value):
    self.choiceOfFlip = value

  def setSameFlipForAll(self, bool):
    self.sameFlipForAll = bool

#
# ShapeAnalysisModuleLogic
#
class ShapeAnalysisModuleLogic(LogicMixin):
  """
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def __init__(self):
    LogicMixin.__init__(self)
    self.parameters = ShapeAnalysisModuleParameters()

  def ShapeAnalysisCases(self):
    # No cases
    if not len(self.InputCases) > 0:
      inputDirectory = self.parameters.inputDirectory
      self.ErrorMessage = "No cases found in " + inputDirectory
      self.Node.SetStatus(self.Node.CompletedWithErrors)
      return -1

    # Create pipelines
    else:
      logging.info('%d case(s) found', len(self.InputCases))
      # Init
      for i in range(len(self.InputCases)):
        self.completed[i] = False
        self.pipeline[i] = ShapeAnalysisModulePipeline(i, self.InputCases[i], self.parameters)

        self.addObserver(self.pipeline[i].Node, slicer.vtkMRMLCommandLineModuleNode().StatusModifiedEvent,
                       self.onPipelineModified)

      # Logic ready
      self.Node.SetStatus(self.Node.Running)
      # Launch Workflow
      self.startPipeline(0)
      return 0

  # Empty the output folders if the overwrite option is checked
  def cleanOutputFolders(self):
    outputDirectory = self.parameters.outputDirectory

    if self.parameters.OverwriteSegPostProcess:
      PostProcessDirectory = outputDirectory + "/Step1_SegPostProcess"
      if os.path.exists(PostProcessDirectory):
        for filename in os.listdir(PostProcessDirectory):
          os.remove(os.path.join(PostProcessDirectory, filename))

    if self.parameters.OverwriteGenParaMesh:
      GenParaMeshOutputDirectory = outputDirectory + "/Step2_GenParaMesh"
      if os.path.exists(GenParaMeshOutputDirectory):
        for filename in os.listdir(GenParaMeshOutputDirectory):
          os.remove(os.path.join(GenParaMeshOutputDirectory, filename))

    if self.parameters.OverwriteParaToSPHARMMesh:
      SPHARMMeshOutputDirectory = outputDirectory + "/Step3_ParaToSPHARMMesh"
      if os.path.exists(SPHARMMeshOutputDirectory):
        for filename in os.listdir(SPHARMMeshOutputDirectory):
          os.remove(os.path.join(SPHARMMeshOutputDirectory, filename))

  # Function to create a CSV file containing all the SPHARM mesh output files
  # that the user wants to display in ShapePopultaionViewer
  def creationCSVFileForSPV(self, table, filepathCSV):
    # Creation of a CSV file with a header 'VTK Files'
    file = open(filepathCSV, 'w')
    cw = csv.writer(file, delimiter=',')
    cw.writerow(['VTK Files'])

    # Add the filepath of the vtk file checked in the table
    outputDirectory = self.parameters.outputDirectory
    SPHARMMeshOutputDirectory = outputDirectory + "/Step3_ParaToSPHARMMesh/"

    # Add the path of the vtk files if the users selected it
    for row in range(0, table.rowCount):
      # check the checkBox
      widget = table.cellWidget(row, 1)
      tuple = widget.children()
      checkBox = tuple[1]
      if checkBox.isChecked():
        # Recovery of the vtk filename
        qlabel = table.cellWidget(row, 0)
        vtkBasename = qlabel.text
        VTKfilepath = SPHARMMeshOutputDirectory + vtkBasename + ".vtk"
        if os.path.exists(VTKfilepath):
          cw.writerow([VTKfilepath])
    file.close()



#
# ShapeAnalysisModulePipeline
#
class ShapeAnalysisModulePipeline(PipelineMixin):
  def __init__(self, pipelineID, CaseInput, interface):

    PipelineMixin.__init__(self, pipelineID, CaseInput, interface)

    self.interface = interface

  def setupSkipCLIs(self):

    self.skip_meshToLabelMap = False
    self.skip_segPostProcess = False
    self.skip_genParaMesh = False
    self.skip_paraToSPHARMMesh = False
    outputDirectory = self.interface.outputDirectory

    # Skip MeshToLabelMap?
    if not self.inputExtension == "vtk" and not self.inputExtension == "vtp":
      self.skip_meshToLabelMap = True
    else:
      LabelMapDirectory = outputDirectory + "/LabelMap"
      LabelMapOutputFilepath = LabelMapDirectory + "/" + self.inputFilename + ".nrrd"
      if os.path.exists(LabelMapOutputFilepath):
        self.inputExtension = "nrrd"
        self.skip_meshToLabelMap = True

    # If MeshToLabelMap is not skipped, do not skip the next CLIs: SegPostProcess, GenParaMesh and ParaToSPHARMMesh
    if self.skip_meshToLabelMap == False:
      return

    # Skip SegPostProcess ?
    if not self.interface.OverwriteSegPostProcess:
      PostProcessDirectory = outputDirectory + "/Step1_SegPostProcess"
      PostProcessOutputFilepath = PostProcessDirectory + "/" + self.inputFilename + "_pp." + self.inputExtension
      if os.path.exists(PostProcessOutputFilepath):
        self.skip_segPostProcess = True

    # If SegPostProcess is not skip, do not skip the next CLIs: GenParaMesh and ParaToSPHARMMesh
    if self.skip_segPostProcess == False:
      return

    # Skip GenParaMesh ?
    if not self.interface.OverwriteGenParaMesh:
      GenParaMeshOutputDirectory = outputDirectory + "/Step2_GenParaMesh"
      ParaOutputFilepath = GenParaMeshOutputDirectory + "/" + self.inputFilename + "_pp_para.vtk"
      SurfOutputFilepath = GenParaMeshOutputDirectory + "/" + self.inputFilename + "_pp_surf.vtk"
      if os.path.exists(ParaOutputFilepath) and os.path.exists(SurfOutputFilepath):
        self.skip_genParaMesh = True

    # If GenParaMesh is not skipped, do not skip the next CLI: ParaToSPHARMMesh
    if self.skip_genParaMesh == False:
      return

    # Skip ParaToSPHARMMesh ?
    if not self.interface.OverwriteParaToSPHARMMesh:
      SPHARMMeshOutputDirectory = outputDirectory + "/Step3_ParaToSPHARMMesh"
      SPHARMMeshFilepath = SPHARMMeshOutputDirectory + "/" + self.inputFilename + "_pp_surf"
      SPHARMMeshDirectory = os.path.dirname(SPHARMMeshFilepath)
      SPHARMMeshBasename = os.path.basename(SPHARMMeshFilepath)
      if os.path.exists(SPHARMMeshDirectory):
        for file in os.listdir(SPHARMMeshDirectory):
          if not file.find(SPHARMMeshBasename) == -1:
              self.skip_paraToSPHARMMesh = True

  def setup(self):
    # Initialization of global variables
    self.setupGlobalVariables()
    self.setupSkipCLIs()

    inputDirectory = self.interface.inputDirectory
    outputDirectory = self.interface.outputDirectory

    ## Mesh To Label Map: Transform model in label map
    cli_nodes = list() # list of the nodes used in the Mesh to Label Map step
    cli_filepaths = list() # list of the node filepaths used in the Mesh to Label Map step
    LabelMapDirectory = outputDirectory + "/LabelMap"
    LabelMapOutputFilepath = LabelMapDirectory + "/" + self.inputFilename + ".nrrd"
    if not self.skip_meshToLabelMap:
      # Setup of the parameters of the CLI
      self.ID += 1

      cli_parameters = {}

      inputFilepath = inputDirectory + '/' + self.CaseInput
      model_input_node = MRMLUtility.loadMRMLNode(inputFilepath, 'ModelFile')

      cli_parameters["mesh"] = model_input_node

      meshtolabelmap_output_node = MRMLUtility.addnewMRMLNode("output_MeshToLabelMap", slicer.vtkMRMLLabelMapVolumeNode())
      cli_parameters["labelMap"] = meshtolabelmap_output_node

      cli_parameters["spacingVec"] = "0.1,0.1,0.1"

      self.inputExtension = "nrrd"

      self.setupModule(slicer.modules.meshtolabelmap, cli_parameters)

      # Setup of the nodes created by the CLI
      #    Creation of a folder in the output folder : LabelMap
      if not os.path.exists(LabelMapDirectory):
        os.makedirs(LabelMapDirectory)

      cli_nodes.append(model_input_node)
      cli_nodes.append(meshtolabelmap_output_node)
      cli_filepaths.append(inputFilepath)
      cli_filepaths.append(LabelMapOutputFilepath)

      self.setupNode(0, cli_nodes, cli_filepaths, [False, True], [True, True])
    else:
      if os.path.exists(LabelMapOutputFilepath):
        # Setup of the nodes which will be used by the next CLI
        meshtolabelmap_output_node = MRMLUtility.loadMRMLNode(LabelMapOutputFilepath, 'LabelMapVolumeFile')

        cli_nodes.append(meshtolabelmap_output_node)
        cli_filepaths.append(LabelMapOutputFilepath)

        self.setupNode(0, cli_nodes, cli_filepaths, [False], [True])

    ## Post Processed Segmentation
    cli_nodes = list() # list of the nodes used in the Post Processed Segmentation step
    cli_filepaths = list() # list of the node filepaths used in the Post Processed Segmentation step
    PostProcessDirectory = outputDirectory + "/Step1_SegPostProcess"
    PostProcessOutputFilepath = PostProcessDirectory + "/" + self.inputFilename + "_pp." + self.inputExtension

    if not self.skip_segPostProcess:
      # Setup of the parameters of the CLI
      self.ID += 1

      cli_parameters = {}

      #     IF Mesh To Label Map has been skipped AND the input given was already a label map
      if self.skip_meshToLabelMap and not os.path.exists(LabelMapOutputFilepath):
        inputFilepath = inputDirectory + '/' + self.CaseInput
        labelmap_input_node = MRMLUtility.loadMRMLNode(inputFilepath, 'LabelMapVolumeFile')
      #     ELSE the input given was a model which has been transformed by MeshToLabelMap and store in the folder LabelMap
      else:
        labelmap_input_node = meshtolabelmap_output_node
        inputFilepath = LabelMapOutputFilepath


      cli_parameters["fileName"] = labelmap_input_node

      pp_output_node = MRMLUtility.addnewMRMLNode("output_PostProcess", slicer.vtkMRMLLabelMapVolumeNode())
      cli_parameters["outfileName"] = pp_output_node.GetID()

      if self.interface.RescaleSegPostProcess:
        cli_parameters["scaleOn"] = True
        cli_parameters["spacing_vect"] = str(self.interface.sx) + "," + str(self.interface.sy) + "," + str(self.interface.sz)
      cli_parameters["label"] = self.interface.labelNumber
      if self.interface.debug:
        cli_parameters["debug"] = True

      #    Advanced parameters
      if self.interface.GaussianFiltering:
        cli_parameters["gaussianOn"] = True
        cli_parameters["variance_vect"] = str(self.interface.VarianceX) + "," + str(self.interface.VarianceY) + "," + str(self.interface.VarianceZ)

      self.setupModule(slicer.modules.segpostprocessclp, cli_parameters)

      # Setup of the nodes created by the CLI
      #    Creation of a folder in the output folder : Step1_SegPostProcess
      if not os.path.exists(PostProcessDirectory):
        os.makedirs(PostProcessDirectory)

      cli_nodes.append(labelmap_input_node)
      cli_nodes.append(pp_output_node)
      cli_filepaths.append(inputFilepath)
      cli_filepaths.append(PostProcessOutputFilepath)

      self.setupNode(1, cli_nodes, cli_filepaths, [False,True], [True,True])

    else:
      # Setup of the nodes which will be used by the next CLI
      pp_output_node = MRMLUtility.loadMRMLNode(PostProcessOutputFilepath, 'LabelMapVolumeFile')

      cli_nodes.append(pp_output_node)
      cli_filepaths.append(PostProcessOutputFilepath)

      self.setupNode(1, cli_nodes, cli_filepaths, [False], [True])


    ## Generate Mesh Parameters
    cli_nodes = list() # list of the nodes used in the Generate Mesh Parameters step
    cli_filepaths = list() # list of the node filepaths used in the Generate Mesh Parameters step
    GenParaMeshOutputDirectory = outputDirectory + "/Step2_GenParaMesh"
    ParaOutputFilepath = GenParaMeshOutputDirectory + "/" + self.inputFilename + "_pp_para.vtk"
    SurfOutputFilepath = GenParaMeshOutputDirectory + "/" + self.inputFilename + "_pp_surf.vtk"

    if not self.skip_genParaMesh:
      # Setup of the parameters of the CLI
      self.ID += 1

      cli_parameters = {}
      cli_parameters["infile"] = pp_output_node

      para_output_model = MRMLUtility.addnewMRMLNode("output_para", slicer.vtkMRMLModelNode())
      cli_parameters["outParaName"] = para_output_model

      surfmesh_output_model = MRMLUtility.addnewMRMLNode("output_surfmesh", slicer.vtkMRMLModelNode())
      cli_parameters["outSurfName"] = surfmesh_output_model

      cli_parameters["numIterations"] = self.interface.NumberofIterations
      if self.interface.debug:
        cli_parameters["debug"] = True

      self.setupModule(slicer.modules.genparameshclp, cli_parameters)

      # Setup of the nodes created by the CLI
      #    Creation of a folder in the output folder : Step2_GenParaMesh
      if not os.path.exists(GenParaMeshOutputDirectory):
        os.makedirs(GenParaMeshOutputDirectory)

      cli_nodes.append(para_output_model)
      cli_nodes.append(surfmesh_output_model)
      cli_filepaths.append(ParaOutputFilepath)
      cli_filepaths.append(SurfOutputFilepath)

      self.setupNode(2, cli_nodes, cli_filepaths, [True,True], [True,True])


    else:
      # Setup of the nodes which will be used by the next CLI
      para_output_model = MRMLUtility.loadMRMLNode(ParaOutputFilepath, 'ModelFile')
      surfmesh_output_model = MRMLUtility.loadMRMLNode(SurfOutputFilepath, 'ModelFile')

      cli_nodes.append(para_output_model)
      cli_nodes.append(surfmesh_output_model)
      cli_filepaths.append(ParaOutputFilepath)
      cli_filepaths.append(SurfOutputFilepath)

      self.setupNode(2, cli_nodes, cli_filepaths, [False, False], [True, True])

    ##  Parameters to SPHARM Mesh
    cli_nodes = list()  # list of the nodes used in the Parameters To SPHARM Mesh step
    cli_filepaths = list()  # list of the node filepaths used in the Parameters To SPHARM Mesh step
    SPHARMMeshOutputDirectory = outputDirectory + "/Step3_ParaToSPHARMMesh"
    if not self.skip_paraToSPHARMMesh:

      # Search of the flip to apply:
      #       1 = flip along axes of x &amp; y,
      #       2 = flip along y &amp; z,
      #       3 = flip along x &amp; z
      #       4 = flip along x,
      #       5 = flip along y,
      #       6 = flip along x &amp; y &amp; z,
      #       7 = flip along z  where y is the smallest, x is the second smallest and z is the long axis of the ellipsoid
      #       8 = All the flips
      if not self.interface.sameFlipForAll:
        # Recovery of the flip chosen by the user
        row = self.pipelineID
        widget = self.interface.tableWidget_ChoiceOfFlip.cellWidget(row, 1)
        tuple = widget.children()
        comboBox = qt.QComboBox()
        comboBox = tuple[1]
        flipIndexToApply = comboBox.currentIndex
        pass
      else:
        flipIndexToApply = self.interface.choiceOfFlip

      # Only one flip to apply
      if flipIndexToApply < 8:
        L = [1]
      # All the flips to apply
      else:
        L = range(1,8)

      for i in L:

        # Setup of the parameters of the CLI
        self.ID += 1

        cli_parameters = {}

        cli_parameters["inParaFile"] = para_output_model

        cli_parameters["inSurfFile"] = surfmesh_output_model

        #    Creation of a folder in the output folder : Step3_ParaToSPHARMMesh
        if not os.path.exists(SPHARMMeshOutputDirectory):
          os.makedirs(SPHARMMeshOutputDirectory)
        if flipIndexToApply < 8:
          SPHARMMeshFilepath = SPHARMMeshOutputDirectory + "/" + self.inputFilename + "_pp_surf"
          cli_parameters["outbase"] = SPHARMMeshFilepath
        #   For each flip creation of an output filename
        else:
          flipName = ['AlongXY', 'AlongYZ', 'AlongXZ', 'AlongX', 'AlongY', 'AlongXYZ', 'AlongZ']
          SPHARMMeshFilepath = SPHARMMeshOutputDirectory + "/" + self.inputFilename + "_flip" + flipName[i - 1] + "_pp_surf"
          cli_parameters["outbase"] = SPHARMMeshFilepath

        cli_parameters["subdivLevel"] = self.interface.SubdivLevelValue
        cli_parameters["spharmDegree"] = self.interface.SPHARMDegreeValue
        cli_parameters["thetaIteration"] = self.interface.thetaIterationValue
        cli_parameters["phiIteration"] = self.interface.phiIterationValue
        if self.interface.medialMesh:
          cli_parameters["medialMesh"] = True
        if self.interface.debug:
          cli_parameters["debug"] = True

        #   Advanced parameters
        if self.interface.useRegTemplate:
          cli_parameters["regTemplateFileOn"] = True
          regtemplate_filepath = self.interface.regTemplate
          regtemplate_model = MRMLUtility.loadMRMLNode(regtemplate_filepath, 'ModelFile')
          cli_parameters["regTemplateFile"] = regtemplate_model

          cli_nodes.append(regtemplate_model)
          cli_filepaths.append(regtemplate_filepath)

          self.setupNode(i + 2, cli_nodes, cli_filepaths, [False], [True])
        if self.interface.useFlipTemplate:
          cli_parameters["flipTemplateFileOn"] = True
          cli_parameters["flipTemplateFile"] = self.interface.flipTemplate

        if flipIndexToApply < 8 :
            cli_parameters["finalFlipIndex"] = flipIndexToApply
        else:
          cli_parameters["finalFlipIndex"] = i

        self.setupModule(slicer.modules.paratospharmmeshclp, cli_parameters)

class ShapeAnalysisModuleTest(ScriptedLoadableModuleTest, VTKObservationMixin):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def __init__(self):
    VTKObservationMixin.__init__(self)

  def setUp(self):
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    self.setUp()
    self.delayDisplay('Starting the tests')
    self.test_ShapeAnalysisModule_completedWithoutErrors()

  def test_ShapeAnalysisModule_completedWithoutErrors(self):
    self.delayDisplay('Test 1: Run Shape Analysis Module')

    #   Creation of input folder
    inputDirectoryPath =  slicer.app.temporaryPath + '/InputShapeAnalysisModule'
    if not os.path.exists(inputDirectoryPath):
      os.makedirs(inputDirectoryPath)

    #   Download the label map in the input folder
    input_downloads = (
      ('https://data.kitware.com/api/v1/file/58f4f9078d777f16d095feaf/download', 'groupA_01_hippo.nrrd'),
    )
    self.download_files(inputDirectoryPath, input_downloads)

    #   Creation of output folder
    outputDirectoryPath =  slicer.app.temporaryPath + '/OutputShapeAnalysisModule'
    if not os.path.exists(outputDirectoryPath):
      os.makedirs(outputDirectoryPath)

    # Creation of a template folder
    templateDirectoryPath =  slicer.app.temporaryPath + '/TemplateShapeAnalysisModule'
    if not os.path.exists(templateDirectoryPath):
      os.makedirs(templateDirectoryPath)
    else:
        for filename in os.listdir(templateDirectoryPath):
          os.remove(os.path.join(templateDirectoryPath, filename))
    #   Download the registration template in the template folder
    template_downloads = (
      ('https://data.kitware.com/api/v1/file/58f618e78d777f16d095fec3/download', 'registrationTemplate.vtk'),
    )
    self.download_files(templateDirectoryPath, template_downloads)


    self.moduleWidget = slicer.modules.ShapeAnalysisModuleWidget

    #
    #  Inputs of Shape Analysis Module
    #
    self.moduleWidget.GroupProjectInputDirectory.directory = inputDirectoryPath
    self.moduleWidget.GroupProjectOutputDirectory.directory = outputDirectoryPath
    self.moduleWidget.NumberofIterations.setValue(5)
    self.moduleWidget.medialMesh.click()
    self.moduleWidget.useRegTemplate.click()
    regTemplateFilePath = templateDirectoryPath + '/registrationTemplate.vtk'
    self.moduleWidget.regTemplate.setCurrentPath(regTemplateFilePath)

    self.addObserver(self.moduleWidget.Logic.Node, slicer.vtkMRMLCommandLineModuleNode().StatusModifiedEvent,
                           self.onLogicModifiedForTests)

    self.delayDisplay('Run Shape Analysis Module')
    self.moduleWidget.ApplyButton.click()

  def onLogicModifiedForTests(self, logic_node, event):
    status = logic_node.GetStatusString()
    if not logic_node.IsBusy():
      if status == 'Completed with errors' or status == 'Cancelled':
        self.removeObserver(logic_node, slicer.vtkMRMLCommandLineModuleNode().StatusModifiedEvent,
                            self.onLogicModifiedForTests)
        self.moduleWidget.ApplyButton.setText("Run ShapeAnalysisModule")

        slicer.mrmlScene.Clear(0)
        self.delayDisplay('Tests Failed!')
      elif status == 'Completed':
        self.removeObserver(logic_node, slicer.vtkMRMLCommandLineModuleNode().StatusModifiedEvent,
                            self.onLogicModifiedForTests)

        self.moduleWidget.ApplyButton.setText("Run ShapeAnalysisModule")

        # If Shape Analysis Module is completed without errors, then run some other tests on the generated outputs
        self.assertTrue(self.test_ShapeAnalysisModule_comparisonOfOutputsSegPostProcess())
        self.assertTrue(self.test_ShapeAnalysisModule_comparisonOfOutputsGenParaMesh())
        self.assertTrue(self.test_ShapeAnalysisModule_comparisonOfOutputsParaToSPHARMMesh())
        self.cleanSlicerTemporaryDirectory()
        slicer.mrmlScene.Clear(0)
        self.delayDisplay('Tests Passed!')

  def test_ShapeAnalysisModule_comparisonOfOutputsSegPostProcess(self):
    self.delayDisplay('Test 2: Comparison of the outputs generated by SegPostProcess CLI')

    # Checking the existence of the output directory Step1_SegPostProcess
    outputDirectoryPath = slicer.app.temporaryPath + '/OutputShapeAnalysisModule'
    SegPostProcessOutputDirectoryPath = outputDirectoryPath + '/Step1_SegPostProcess'
    if not os.path.exists(SegPostProcessOutputDirectoryPath):
      return False

    # Downloading output data to compare with the ones generated by Shape Analysis Module during the tests
    output_downloads = (
      ('https://data.kitware.com/api/v1/file/58f7b5c68d777f16d095ff84/download', 'groupA_01_hippo_pp_comparison.nrrd'),
    )
    self.download_files(SegPostProcessOutputDirectoryPath, output_downloads)

    #   Comparison of the SPHARM Mesh Outputs
    self.delayDisplay('Comparison of the Post Process Outputs')
    output_filenames = ['groupA_01_hippo_pp.nrrd']
    for i in range(len(output_filenames)):
      volume_filepath2 = os.path.join(SegPostProcessOutputDirectoryPath, output_filenames[i])
      #   Checking the existence of the output files in the folder Step3_ParaToSPHARMMesh
      if not os.path.exists(volume_filepath2):
        return False

      # Loading the 2 models for comparison
      volume_filepath1 = os.path.join(SegPostProcessOutputDirectoryPath, output_downloads[i][1])
      volume1 = MRMLUtility.loadMRMLNode(volume_filepath1, 'LabelMapVolumeFile')
      volume2 = MRMLUtility.loadMRMLNode(volume_filepath2, 'LabelMapVolumeFile')

      #   Comparison
      if not self.volume_comparison(volume1, volume2):
        return False

    return True

  def test_ShapeAnalysisModule_comparisonOfOutputsGenParaMesh(self):
    self.delayDisplay('Test 3: Comparison of the outputs generated by GenParaMesh CLI')

    # Checking the existence of the output directory Step2_GenParaMesh
    outputDirectoryPath = slicer.app.temporaryPath + '/OutputShapeAnalysisModule'
    GenParaMeshOutputDirectoryPath = outputDirectoryPath + '/Step2_GenParaMesh'
    if not os.path.exists(GenParaMeshOutputDirectoryPath):
      return False

    # Downloading output data to compare with the ones generated by Shape Analysis Module during the tests
    output_downloads = (
      ('https://data.kitware.com/api/v1/file/58f7b5bc8d777f16d095ff7e/download', 'groupA_01_hippo_pp_para_comparison.vtk'),
      ('https://data.kitware.com/api/v1/file/58f7b5bc8d777f16d095ff81/download', 'groupA_01_hippo_pp_surf_comparison.vtk'),
    )
    self.download_files(GenParaMeshOutputDirectoryPath, output_downloads)

    #   Comparison of the SPHARM Mesh Outputs
    self.delayDisplay('Comparison of the Parameters Mesh Outputs')
    output_filenames = ['groupA_01_hippo_pp_para.vtk', 'groupA_01_hippo_pp_surf.vtk']
    for i in range(len(output_filenames)):
      model_filepath2 = os.path.join(GenParaMeshOutputDirectoryPath, output_filenames[i])
      #   Checking the existence of the output files in the folder Step3_ParaToSPHARMMesh
      if not os.path.exists(model_filepath2):
        return False

      # Loading the 2 models for comparison
      model_filepath1 = os.path.join(GenParaMeshOutputDirectoryPath, output_downloads[i][1])
      model1 = MRMLUtility.loadMRMLNode(model_filepath1, 'ModelFile')
      model2 = MRMLUtility.loadMRMLNode(model_filepath2, 'ModelFile')

      #   Comparison
      if not self.polydata_comparison(model1, model2):
        return False

    return True

  def test_ShapeAnalysisModule_comparisonOfOutputsParaToSPHARMMesh(self):
    self.delayDisplay('Test 4: Comparison of the outputs generated by ParaToSPHARMMesh CLI')

    # Checking the existence of the output directory Step3_ParaToSPHARMMesh
    outputDirectoryPath =  slicer.app.temporaryPath + '/OutputShapeAnalysisModule'
    ParaToSPHARMMeshOutputDirectoryPath = outputDirectoryPath + '/Step3_ParaToSPHARMMesh'
    if not os.path.exists(ParaToSPHARMMeshOutputDirectoryPath):
      return False

    # Downloading output data to compare with the ones generated by Shape Analysis Module during the tests
    output_downloads = (
      ('https://data.kitware.com/api/v1/file/58f7b5e88d777f16d095ff87/download', 'groupA_01_hippo_pp_surf_SPHARM_comparison.vtk'),
      ('https://data.kitware.com/api/v1/file/58f7b5e88d777f16d095ff8a/download', 'groupA_01_hippo_pp_surf_SPHARM_ellalign_comparison.vtk'),
      ('https://data.kitware.com/api/v1/file/58f7b5e98d777f16d095ff8d/download', 'groupA_01_hippo_pp_surf_SPHARMMedialMesh_comparison.vtk'),
      ('https://data.kitware.com/api/v1/file/58f7b5e98d777f16d095ff90/download', 'groupA_01_hippo_pp_surf_SPHARM_procalign_comparison.vtk'),
    )
    self.download_files(ParaToSPHARMMeshOutputDirectoryPath, output_downloads)

    #   Comparison of the SPHARM Mesh Outputs
    self.delayDisplay('Comparison of the SPHARM Mesh Outputs')
    output_filenames = ['groupA_01_hippo_pp_surf_SPHARM.vtk', 'groupA_01_hippo_pp_surf_SPHARM_ellalign.vtk', 'groupA_01_hippo_pp_surf_SPHARMMedialMesh.vtk', 'groupA_01_hippo_pp_surf_SPHARM_procalign.vtk']
    for i in range(len(output_filenames)):
      model_filepath2 = os.path.join(ParaToSPHARMMeshOutputDirectoryPath, output_filenames[i])
      #   Checking the existence of the output files in the folder Step3_ParaToSPHARMMesh
      if not os.path.exists(model_filepath2):
        return False

      #   Loading the 2 models for comparison
      model_filepath1 = os.path.join(ParaToSPHARMMeshOutputDirectoryPath, output_downloads[i][1])
      model1 = MRMLUtility.loadMRMLNode(model_filepath1, 'ModelFile')
      model2 = MRMLUtility.loadMRMLNode(model_filepath2, 'ModelFile')

      #   Comparison
      if not self.polydata_comparison(model1, model2):
        return False

    return True

  def volume_comparison(self, volume1, volume2):
    imageData1 = volume1.GetImageData()
    imageData2 = volume2.GetImageData()

    nbPoints1 = imageData1.GetNumberOfPoints()
    nbPoints2 = imageData2.GetNumberOfPoints()
    if not nbPoints1 == nbPoints2:
      return False

    dimension1 = imageData1.GetDimensions()
    dimension2 = imageData2.GetDimensions()
    if not dimension1 == dimension2:
      return False

    for i in range(dimension1[0]):
      for j in range(dimension1[1]):
        for k in range(dimension1[2]):
          if not imageData1.GetScalarComponentAsDouble(i,j,k,0) == imageData2.GetScalarComponentAsDouble(i,j,k,0):
            return False

    return True

  def polydata_comparison(self, model1, model2):
    polydata1 = model1.GetPolyData()
    polydata2 = model2.GetPolyData()

    # Number of points
    nbPoints1 = polydata1.GetNumberOfPoints()
    nbPoints2 = polydata2.GetNumberOfPoints()
    if not nbPoints1 == nbPoints2:
      return False

    # Polydata
    data1 = polydata1.GetPoints().GetData()
    data2 = polydata2.GetPoints().GetData()

    #   Number of Components
    nbComponents1 = data1.GetNumberOfComponents()
    nbComponents2 = data2.GetNumberOfComponents()
    if not nbComponents1 == nbComponents2:
      return False

    #   Points value
    for i in range(nbPoints1):
      for j in range(nbComponents1):
        if not data1.GetTuple(i)[j] == data2.GetTuple(i)[j]:
          return False

    # Area
    nbAreas1 = polydata1.GetPointData().GetNumberOfArrays()
    nbAreas2 = polydata2.GetPointData().GetNumberOfArrays()
    if not nbAreas1 == nbAreas2:
      return False

    for l in range(nbAreas1):
      area1 = polydata1.GetPointData().GetArray(l)
      area2 = polydata2.GetPointData().GetArray(l)

      #   Name of the area
      nameArea1 = area1.GetName()
      nameArea2 = area2.GetName()
      if not nameArea1 == nameArea2:
        return False

      # Number of Components of the area
      nbComponents1 = area1.GetNumberOfComponents()
      nbComponents2 = area2.GetNumberOfComponents()
      if not nbComponents1 == nbComponents2:
        return False

      # Points value in the area
      for i in range(nbPoints1):
        for j in range(nbComponents1):
          if not data1.GetTuple(i)[j] == data2.GetTuple(i)[j]:
            return False

    return True

  def download_files(self, directoryPath, downloads):
    self.delayDisplay('Starting download')
    for url, name in downloads:
      filePath = os.path.join(directoryPath, name)
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print 'Requesting download %s from %s...\n' % (name, url)
        urllib.urlretrieve(url, filePath)
    self.delayDisplay('Finished with download')

  # Function to delete all the data needed for the tests
  def cleanSlicerTemporaryDirectory(self):
    # deletion of the SAM input folder
    inputDirectoryPath =  slicer.app.temporaryPath + '/InputShapeAnalysisModule'
    if os.path.exists(inputDirectoryPath):
      shutil.rmtree(inputDirectoryPath)

    # deletion of the SAM output folder
    outputDirectoryPath =  slicer.app.temporaryPath + '/OutputShapeAnalysisModule'
    if os.path.exists(outputDirectoryPath):
      shutil.rmtree(outputDirectoryPath)

    # deletion of the SAM template folder
    templateDirectoryPath =  slicer.app.temporaryPath + '/TemplateShapeAnalysisModule'
    if os.path.exists(templateDirectoryPath):
      shutil.rmtree(templateDirectoryPath)

