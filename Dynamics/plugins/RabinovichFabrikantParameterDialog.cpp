/*
 * DO NOT EDIT THIS FILE.
 *
 * THIS FILE HAS BEEN AUTOMATICALLY GENERATED.
 * ANY CHANGES MADE TO THE CODE WILL BE LOST.
 *
 * TO MODIFY THE PARAMETER VALUES OR DYNAMICAL
 * EQUATIONS EDIT THE XML FILE (dynamics.xml).
 * 
 */
 
#include "RabinovichFabrikantParameterDialog.h"
#include "GLMotif/WidgetFactory.h"
#include "IntegrationStepSize.h"
#include "VruiStreamManip.h"

GLMotif::PopupWindow* RabinovichFabrikantParameterDialog::createDialog()
{
  WidgetFactory factory;
  GLMotif::PopupWindow* parameterDialogPopup=factory.createPopupWindow("ParameterDialogPopup", "RabinovichFabrikant Parameters");

  GLMotif::RowColumn* parameterDialog=factory.createRowColumn("ParameterDialog", 3);
  factory.setLayout(parameterDialog);

  factory.createLabel("GammaParameterLabel", "gamma");

  currentGammaValue=factory.createTextField("CurrentGammaValue", 10);
  currentGammaValue->setString("0.87");

  gammaParameterSlider=factory.createSlider("GammaParameterSlider", 15.0);
  gammaParameterSlider->setValueRange(0.0, 5.0, 0.01);
  gammaParameterSlider->setValue(0.87);
  gammaParameterSlider->getValueChangedCallbacks().add(this, &RabinovichFabrikantParameterDialog::sliderCallback);

  factory.createLabel("AlphaParameterLabel", "alpha");

  currentAlphaValue=factory.createTextField("CurrentAlphaValue", 10);
  currentAlphaValue->setString("1.1");

  alphaParameterSlider=factory.createSlider("AlphaParameterSlider", 15.0);
  alphaParameterSlider->setValueRange(0.0, 5.0, 0.01);
  alphaParameterSlider->setValue(1.1);
  alphaParameterSlider->getValueChangedCallbacks().add(this, &RabinovichFabrikantParameterDialog::sliderCallback);


  factory.createLabel("StepSizeLabel", "step size");
  stepSizeValue=factory.createTextField("StepSizeValue", 10);
  double step_size = IntegrationStepSize::instance()->getSavedValue("Rabinovich Fabrikant");
  if (step_size > 0.0) stepSizeValue->setString(toString(step_size).c_str());
  else stepSizeValue->setString("0.01");
  stepSizeSlider=factory.createSlider("StepSizeSlider", 15.0);
  stepSizeSlider->setValueRange(0.0001, 0.05, 0.0001);
  if (step_size > 0.0) stepSizeSlider->setValue(step_size);
  else stepSizeSlider->setValue(0.01);
  stepSizeSlider->getValueChangedCallbacks().add(this, &RabinovichFabrikantParameterDialog::sliderCallback);


  factory.createLabel("EvaluationLabel", "Evaluation Method");
  GLMotif::ToggleButton* exactEvalToggle=factory.createCheckBox("ExactEvalToggle", "Exact", true);
  GLMotif::ToggleButton* gridEvalToggle=factory.createCheckBox("GridEvalToggle", "Interpolated Grid");
  // assign line style toggle callbacks
  exactEvalToggle->getValueChangedCallbacks().add(this, &RabinovichFabrikantParameterDialog::evalTogglesCallback);
  gridEvalToggle->getValueChangedCallbacks().add(this, &RabinovichFabrikantParameterDialog::evalTogglesCallback);

  factory.createLabel("xSpacingLabel", "x-Grid Spacing");
  currentXValue=factory.createTextField("xTextField", 12);
  currentXValue->setString("1.0");
  currentXValue->setCharWidth(5);
  currentXValue->setPrecision(5);
  xSpacingSlider=factory.createSlider("XSpacingSlider", 15.0);
  xSpacingSlider->setValueRange(.001, 2.0, 0.001);
  xSpacingSlider->setValue(1.0);
  xSpacingSlider->getValueChangedCallbacks().add(this, &RabinovichFabrikantParameterDialog::sliderCallback);

  factory.createLabel("ySpacingLabel", "y-Grid Spacing");
  currentYValue=factory.createTextField("yTextField", 12);
  currentYValue->setString("1.0");
  currentYValue->setCharWidth(5);
  currentYValue->setPrecision(5);  ySpacingSlider=factory.createSlider("YSpacingSlider", 15.0);
  ySpacingSlider->setValueRange(.001, 2.0, 0.001);
  ySpacingSlider->setValue(1.0);
  ySpacingSlider->getValueChangedCallbacks().add(this, &RabinovichFabrikantParameterDialog::sliderCallback);

  factory.createLabel("zSpacingLabel", "z-Grid Spacing");
  currentZValue=factory.createTextField("zTextField", 12);
  currentZValue->setString("1.0");
  currentZValue->setCharWidth(5);
  currentZValue->setPrecision(5);
  zSpacingSlider=factory.createSlider("ZSpacingSlider", 15.0);
  zSpacingSlider->setValueRange(.001, 2.0, 0.001);
  zSpacingSlider->setValue(1.0);
  zSpacingSlider->getValueChangedCallbacks().add(this, &RabinovichFabrikantParameterDialog::sliderCallback);

  // add toggles to array for radio-button behavior
  evalToggles.push_back(exactEvalToggle);
  evalToggles.push_back(gridEvalToggle);

  parameterDialog->manageChild();
  return parameterDialogPopup;
}

void RabinovichFabrikantParameterDialog::sliderCallback(GLMotif::Slider::ValueChangedCallbackData* cbData)
{
  double value = cbData->value;

  char buff[10];
  snprintf(buff, sizeof(buff), "%3.2f", value);

  if (strcmp(cbData->slider->getName(), "GammaParameterSlider")==0)
    {
      currentGammaValue->setString(buff);
      model->setValue("gamma", value);
    }
  else if (strcmp(cbData->slider->getName(), "AlphaParameterSlider")==0)
    {
      currentAlphaValue->setString(buff);
      model->setValue("alpha", value);
    }
  else if (strcmp(cbData->slider->getName(), "StepSizeSlider")==0)
  {
    snprintf(buff, sizeof(buff), "%6.4f", value);
    stepSizeValue->setString(buff);
    IntegrationStepSize::instance()->setValue(value);
    IntegrationStepSize::instance()->saveValue("Rabinovich Fabrikant", value);
  }

  else if (strcmp(cbData->slider->getName(), "XSpacingSlider")==0)
    {
      snprintf(buff, sizeof(buff), "%3.3f", value);
      currentXValue->setString(buff);
      model->setSpacing(0, value);
    }
  else if (strcmp(cbData->slider->getName(), "YSpacingSlider")==0)
    {
      snprintf(buff, sizeof(buff), "%3.3f", value);
      currentYValue->setString(buff);
      model->setSpacing(1, value);
    }
  else if (strcmp(cbData->slider->getName(), "ZSpacingSlider")==0)
    {
      snprintf(buff, sizeof(buff), "%3.3f", value);
      currentZValue->setString(buff);
      model->setSpacing(2, value);
    }
}

void RabinovichFabrikantParameterDialog::evalTogglesCallback(GLMotif::ToggleButton::ValueChangedCallbackData* cbData)
{
   std::string name=cbData->toggle->getName();

   if (name == "ExactEvalToggle")
   {
      model->setSimulate(false);
   }
   else if (name == "GridEvalToggle")
   {
      model->setSimulate(true);
   }

   // fake radio-button behavior
   for (ToggleArray::iterator button=evalToggles.begin(); button != evalToggles.end(); ++button)
      if (strcmp((*button)->getName(), name.c_str()) != 0 and (*button)->getToggle())
         (*button)->setToggle(false);
      else if (strcmp((*button)->getName(), name.c_str()) == 0)
         (*button)->setToggle(true);

}

