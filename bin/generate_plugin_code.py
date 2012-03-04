#!/usr/bin/python
################################################################################
# generate_plugin_code: Script for generating dynamical systems code from
# simple xml schema.
# Copyright (c) 2006-2008 Jordan Van Aalsburg
#
# This file is part of the Dynamics Toolset.
#
# The Dynamics Toolset is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# The Dynamics Toolset is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with the Dynamics Toolset. If not, see <http://www.gnu.org/licenses/>.
################################################################################


def TAB(count):
    fill = ""
    for i in range(count):
        fill += "  "
    return fill


import re

def SplitCamelCase(word):

    return re.sub('([a-z])([A-Z])', '\\1 \\2', word)

def ToCamelCase(word):

    return re.sub('([a-z]) ([A-Z])', '\\1\\2', word)


class Parameter:

    def __init__(self, name, min, max, step, default):

        self.name = name
        self.min  = min
        self.max  = max
        self.step_size = step
        self.default   = default


class DynamicalSystem:

    def __init__(self, name):

        self.name = name;
        self.nice_name = None;

        self.parameters = []

        self.equations  = {}

        self.center = { }

        self.warning = """/*
 * DO NOT EDIT THIS FILE.
 *
 * THIS FILE HAS BEEN AUTOMATICALLY GENERATED.
 * ANY CHANGES MADE TO THE CODE WILL BE LOST.
 *
 * TO MODIFY THE PARAMETER VALUES OR DYNAMICAL
 * EQUATIONS EDIT THE XML FILE (dynamics.xml).
 *
 */

"""

    def generate_dynamics_header(self, out):

        self.generate_dynamic_model_code(out)

        self.generate_integrator_code(out)



    def generate_parameter_header(self, out):

        self.generate_parameter_dialog_header(out)


    def generate_dynamic_model_code(self, out):

        out.write( self.warning )
        out.write( "#ifndef %s_INCLUDED_\n" % self.name.upper() )
        out.write( "#define %s_INCLUDED_\n" % self.name.upper() )
        out.write( "\n" )
        out.write( "#include \"BaseModel.h\"\n" )
        out.write( "#include \"RungeKutta4.h\"\n" )
        out.write( "\n" )
        out.write( "#include \"%sParameterDialog.h\"\n" % self.name )
        out.write( "\n" )

        out.write( "class %s : public DynamicalModel\n" % self.name )
        out.write( "{\n" )

        # parameter declarations
        for param in self.parameters:
            out.write( TAB(1) + "Scalar %s;\n" % param.name )

        out.write( "public:\n" )

        # constructor
        args = "("
        for param in self.parameters:
            args += "Scalar " + param.name.capitalize() + ", "
        args  = args[:-2]
        args += ")"

        out.write( TAB(1) + "%s" % self.name + args + "\n")

        # initializer list
        args = " : "
        for param in self.parameters:
            args += "%s(%s)" % (param.name, param.name.capitalize()) + ", "
        args = args[:-2]
        out.write( TAB(2) + args + '\n' )
        out.write( TAB(1) + "{ }\n" )

        # destructor
        out.write( "\n" )
        out.write( TAB(1) + "virtual ~%s() { }\n" % self.name )

        out.write( '\n' )
        out.write( TAB(1) + "virtual Vector exact(const Point& p) const\n" )
        out.write( TAB(2) + "{\n" )
        out.write( TAB(3) + "return Vector(" )

        fields = self.equations['x'] + ',' + self.equations['y'] + ',' + self.equations['z']

        fields = re.sub('x', 'p[0]', fields)
        fields = re.sub('y', 'p[1]', fields)
        fields = re.sub('z', 'p[2]', fields)

        out.write( fields )
        out.write( ");\n" )

        out.write( TAB(2) + "}\n" )

        out.write( "\n" )

        out.write( "private:\n" )

        out.write( TAB(1) + "virtual void _setValue(const std::string& name, Scalar value)\n" )
        out.write( TAB(2) + "{\n" )

        count=0
        for param in self.parameters:
            if count == 0:
                out.write( TAB(3) + "if      (name == \"%s\") %s = value;\n" % (param.name, param.name) )
            else:
                out.write( TAB(3) + "else if (name == \"%s\") %s = value;\n" % (param.name, param.name) )
            count += 1
        out.write( TAB(2) + "}\n" )

        out.write( "};\n" )

        out.write( "\n" )


    def generate_integrator_code(self, out):

        out.write( "class %sIntegrator : public Integrator\n" % self.name )
        out.write( "{\n" )
        out.write( TAB(1) + "%s* dynamics;\n" % self.name )
        out.write( TAB(1) + "RungeKutta4<%s>* integrator;\n" % self.name )
        out.write( "public:\n" )
        out.write( TAB(1) + "%sIntegrator()\n" % self.name )
        out.write( TAB(2) + "{\n" )


        args = "("
        for param in self.parameters:
            args += param.default + ", "
        args = args[:-2];
        args += ")"

        out.write( TAB(3) + "dynamics = new %s" % self.name + args + ";\n" )
        #
        #
        #
        #out.write( TAB(3) + "double stepSize = %s;\n" );
        out.write( TAB(3) + "double stepSize = 0.01;\n" );
        #
        #
        #
        out.write( TAB(3) + "integrator = new RungeKutta4<%s>(*dynamics, stepSize);\n" % self.name )
        out.write( TAB(2) + "}\n" )
        out.write( "\n" )
        out.write( TAB(1) + "virtual ~%sIntegrator()\n" % self.name )
        out.write( TAB(2) + "{\n" )
        out.write( TAB(3) + "delete dynamics;\n" )
        out.write( TAB(3) + "delete integrator;\n" )
        out.write( TAB(2) + "}\n" )
        out.write( "\n" )
        out.write( TAB(1) + "inline Vector step(const Point& p)\n" )
        out.write( TAB(2) + "{\n" )
        out.write( TAB(3) + "return integrator->step(p);\n" )
        out.write( TAB(2) + "}\n" )
        out.write( "\n" )
        out.write( TAB(1) + "virtual unsigned int getModelVersion()\n" )
        out.write( TAB(2) + "{\n" )
        out.write( TAB(3) + "return dynamics->getModelVersion();\n" )
        out.write( TAB(2) + "}\n" )
        out.write( "\n" )
        out.write( TAB(1) + "virtual CaveDialog* createParameterDialog(GLMotif::PopupMenu *parent)\n" )
        out.write( TAB(2) + "{\n" )
        out.write( TAB(3) + "return new %sParameterDialog(parent, dynamics);\n" % self.name )
        out.write( TAB(2) + "}\n" )
        out.write( "\n" )
        out.write( TAB(1) + "virtual Vrui::Point center() const\n" )
        out.write( TAB(2) + "{\n")
        out.write( TAB(3) + "return Vrui::Point(%s, %s, %s);\n" % (self.center['x'],
                                                                   self.center['y'],
                                                                   self.center['z']) )
        out.write( TAB(2) + "}\n")


        out.write( "};\n" )
        out.write( "\n" )
        out.write( "#endif\n" )

    def generate_dyamics_source(self, out):

        out.write( self.warning )

        out.write( "#include \"%s.h\"\n" % self.name )
        #out.write( "extern \"C\"\n" )
        #out.write( "{\n" )
        out.write( TAB(1) + "Integrator* maker()\n" )
        out.write( TAB(1) + "{\n" )
        out.write( TAB(2) + "return new %sIntegrator;\n" % self.name)
        out.write( TAB(1) + "}\n" )
        out.write( "\n" )
        out.write( TAB(1) + "class %sProxy\n" % self.name)
        out.write( TAB(1) + "{\n" )
        out.write( TAB(2) + "public:\n" )
        out.write( TAB(3) + "%sProxy()\n" % self.name)
        out.write( TAB(3) + "{\n" )
        if not self.nice_name:
            name = SplitCamelCase(self.name)
        else:
            name = self.nice_name
        out.write( TAB(4) + "Factory[\"%s\"] = maker;\n" % name )
        out.write( TAB(3) + "}\n" )
        out.write( TAB(1) + "};\n" )
        out.write( "\n" )
        out.write( TAB(1) + "%sProxy p;\n" % self.name)
        #out.write( "}\n" )



    def generate_parameter_dialog_header(self, out):

        out.write( self.warning )
        out.write( "#ifndef %sPARAMETERDIALOG_H_\n" % self.name.upper() )
        out.write( "#define %sPARAMETERDIALOG_H_\n" % self.name.upper() )
        out.write( "\n" )
        out.write( "#include <GLMotif/GLMotif>\n" )
        out.write( "\n" )
        out.write( "#include \"BaseModel.h\"\n" )
        out.write( "#include \"CaveDialog.h\"\n" )
        out.write( "\n" )
        out.write( "class %sParameterDialog : public CaveDialog\n" % self.name )
        out.write( "{\n" )
        out.write( TAB(1) + "typedef std::vector<GLMotif::ToggleButton*> ToggleArray;\n" )
        out.write( "\n" )
        out.write( TAB(1) + "DynamicalModel* model;\n" )
        out.write( "\n" )

        for param in self.parameters:
            out.write( TAB(1) + "GLMotif::Slider *%sParameterSlider;\n" % param.name )
        out.write( "\n" )
        for param in self.parameters:
            out.write( TAB(1) + "GLMotif::TextField *current%sValue;\n" % param.name.capitalize() )
        out.write( "\n" )
        out.write( TAB(1) + "GLMotif::Slider       *stepSizeSlider;\n" )
        out.write( TAB(1) + "GLMotif::TextField    *stepSizeValue;\n" )
        out.write( "\n" )
        out.write( """
  GLMotif::Slider *xSpacingSlider;
  GLMotif::Slider *ySpacingSlider;
  GLMotif::Slider *zSpacingSlider;
  GLMotif::TextField *currentXValue;
  GLMotif::TextField *currentYValue;
  GLMotif::TextField *currentZValue;
""" )
        out.write( TAB(1) + "void sliderCallback(GLMotif::Slider::ValueChangedCallbackData* cbData);\n" )
        out.write( TAB(1) + "void evalTogglesCallback(GLMotif::ToggleButton::ValueChangedCallbackData* cbData);\n" )
        out.write( "\n" )
        out.write( TAB(1) + "ToggleArray evalToggles;\n" )
        out.write( "\n" )
        out.write( "protected:\n" )
        out.write( TAB(1) + "GLMotif::PopupWindow* createDialog();\n" )
        out.write( "\n" )
        out.write( "public:\n" )
        out.write( TAB(1) + "%sParameterDialog(GLMotif::PopupMenu *parentMenu, DynamicalModel* m)\n" % self.name )
        out.write( TAB(2) + " : CaveDialog(parentMenu), model(m)\n" )
        out.write( TAB(1) + "{\n" )
        out.write( TAB(2) + "dialogWindow=createDialog();\n" )
        out.write( TAB(1) + "}\n" )
        out.write( "\n" )
        out.write( TAB(1) + "virtual ~%sParameterDialog() { }\n" % self.name )
        out.write( "};\n" )
        out.write( "\n" )
        out.write( "#endif\n" )


    def generate_parameter_source(self, out):

        out.write( self.warning )
        out.write( "#include \"%sParameterDialog.h\"\n" % self.name )
        out.write( "#include \"GLMotif/WidgetFactory.h\"\n" )
        out.write( "#include \"IntegrationStepSize.h\"\n" )
        out.write( "#include \"VruiStreamManip.h\"\n" )

        out.write( "\n" )
        out.write( "GLMotif::PopupWindow* %sParameterDialog::createDialog()\n" % self.name )
        out.write( "{\n" )
        out.write( TAB(1) + "WidgetFactory factory;\n" )
        out.write( TAB(1) +  "GLMotif::PopupWindow* parameterDialogPopup=factory.createPopupWindow(\"ParameterDialogPopup\", \"%s Parameters\");\n" % self.name )
        out.write( "\n" )
        out.write( TAB(1) + "GLMotif::RowColumn* parameterDialog=factory.createRowColumn(\"ParameterDialog\", 3);\n" )
        out.write( TAB(1) + "factory.setLayout(parameterDialog);\n" )
        out.write( "\n" )

        for param in self.parameters:

            out.write( TAB(1) + "factory.createLabel(\"%sParameterLabel\", \"%s\");\n" % (param.name.capitalize(), param.name) )
            out.write( "\n" )
            out.write( TAB(1) + "current%sValue=factory.createTextField(\"Current%sValue\", 10);\n" % (param.name.capitalize(), param.name.capitalize()) )
            out.write( TAB(1) + "current%sValue->setString(\"%s\");\n" % (param.name.capitalize(), param.default) )
            out.write( "\n" )
            out.write( TAB(1) + "%sParameterSlider=factory.createSlider(\"%sParameterSlider\", 15.0);\n" % (param.name, param.name.capitalize()) )
            out.write( TAB(1) + "%sParameterSlider->setValueRange(%s, %s, %s);\n" % (param.name, param.min, param.max, param.step_size) )
            out.write( TAB(1) + "%sParameterSlider->setValue(%s);\n" % (param.name, param.default) )
            out.write( TAB(1) + "%sParameterSlider->getValueChangedCallbacks().add(this, &%sParameterDialog::sliderCallback);\n" % (param.name, self.name) )
            out.write( "\n" )

        out.write( "\n" )

        out.write( TAB(1) + "factory.createLabel(\"StepSizeLabel\", \"step size\");\n" )
        out.write( TAB(1) + "stepSizeValue=factory.createTextField(\"StepSizeValue\", 10);\n" )

        out.write( TAB(1) + "double step_size = IntegrationStepSize::instance()->getSavedValue(\"%s\");\n" % SplitCamelCase(self.name) )
        out.write( TAB(1) + "if (step_size > 0.0) stepSizeValue->setString(toString(step_size).c_str());\n" )
        out.write( TAB(1) + "else stepSizeValue->setString(\"0.01\");\n" )

        out.write( TAB(1) + "stepSizeSlider=factory.createSlider(\"StepSizeSlider\", 15.0);\n" )
        out.write( TAB(1) + "stepSizeSlider->setValueRange(0.0001, 0.05, 0.0001);\n" )

        out.write( TAB(1) + "if (step_size > 0.0) stepSizeSlider->setValue(step_size);\n" )
        out.write( TAB(1) + "else stepSizeSlider->setValue(0.01);\n" )

        out.write( TAB(1) + "stepSizeSlider->getValueChangedCallbacks().add(this, &%sParameterDialog::sliderCallback);\n"  % self.name )
        out.write( "\n" )
        out.write(r"""
  factory.createLabel("EvaluationLabel", "Evaluation Method");
  GLMotif::ToggleButton* exactEvalToggle=factory.createCheckBox("ExactEvalToggle", "Exact", true);
  GLMotif::ToggleButton* gridEvalToggle=factory.createCheckBox("GridEvalToggle", "Interpolated Grid");
  // assign line style toggle callbacks
  exactEvalToggle->getValueChangedCallbacks().add(this, &%(name)sParameterDialog::evalTogglesCallback);
  gridEvalToggle->getValueChangedCallbacks().add(this, &%(name)sParameterDialog::evalTogglesCallback);

  factory.createLabel("xSpacingLabel", "x-Grid Spacing");
  currentXValue=factory.createTextField("xTextField", 12);
  currentXValue->setString("1.0");
  currentXValue->setCharWidth(5);
  currentXValue->setPrecision(5);
  xSpacingSlider=factory.createSlider("XSpacingSlider", 15.0);
  xSpacingSlider->setValueRange(.001, 2.0, 0.001);
  xSpacingSlider->setValue(1.0);
  xSpacingSlider->getValueChangedCallbacks().add(this, &%(name)sParameterDialog::sliderCallback);

  factory.createLabel("ySpacingLabel", "y-Grid Spacing");
  currentYValue=factory.createTextField("yTextField", 12);
  currentYValue->setString("1.0");
  currentYValue->setCharWidth(5);
  currentYValue->setPrecision(5);  ySpacingSlider=factory.createSlider("YSpacingSlider", 15.0);
  ySpacingSlider->setValueRange(.001, 2.0, 0.001);
  ySpacingSlider->setValue(1.0);
  ySpacingSlider->getValueChangedCallbacks().add(this, &%(name)sParameterDialog::sliderCallback);

  factory.createLabel("zSpacingLabel", "z-Grid Spacing");
  currentZValue=factory.createTextField("zTextField", 12);
  currentZValue->setString("1.0");
  currentZValue->setCharWidth(5);
  currentZValue->setPrecision(5);
  zSpacingSlider=factory.createSlider("ZSpacingSlider", 15.0);
  zSpacingSlider->setValueRange(.001, 2.0, 0.001);
  zSpacingSlider->setValue(1.0);
  zSpacingSlider->getValueChangedCallbacks().add(this, &%(name)sParameterDialog::sliderCallback);

  // add toggles to array for radio-button behavior
  evalToggles.push_back(exactEvalToggle);
  evalToggles.push_back(gridEvalToggle);
"""  % {'name':self.name})
        out.write( "\n" )
        out.write( TAB(1) + "parameterDialog->manageChild();\n" )
        out.write( TAB(1) + "return parameterDialogPopup;\n" )
        out.write( "}\n" )
        out.write( "\n" )
        out.write( "void %sParameterDialog::sliderCallback(GLMotif::Slider::ValueChangedCallbackData* cbData)\n" % self.name )
        out.write( "{\n" )
        out.write( TAB(1) + "double value = cbData->value;\n" )
        out.write( "\n" )
        out.write( TAB(1) + "char buff[10];\n" )
        out.write( TAB(1) + "snprintf(buff, sizeof(buff), \"%3.2f\", value);\n" )
        out.write( "\n" )

        count = 0
        for param in self.parameters:
            if count == 0:
                out.write( TAB(1) + "if (strcmp(cbData->slider->getName(), \"%sParameterSlider\")==0)\n" % param.name.capitalize() )
            else:
                out.write( TAB(1) + "else if (strcmp(cbData->slider->getName(), \"%sParameterSlider\")==0)\n" % param.name.capitalize() )

            out.write( TAB(2) + "{\n" )
            out.write( TAB(3) + "current%sValue->setString(buff);\n" % param.name.capitalize() )
            out.write( TAB(3) + "model->setValue(\"%s\", value);\n" % param.name )
            out.write( TAB(2) + "}\n" )

            count += 1

        out.write ( TAB(1) + "else if (strcmp(cbData->slider->getName(), \"StepSizeSlider\")==0)\n" )
        out.write ( TAB(1) + "{\n" )
        out.write ( TAB(2) + "snprintf(buff, sizeof(buff), \"%6.4f\", value);\n" )
        out.write ( TAB(2) + "stepSizeValue->setString(buff);\n" )
        out.write ( TAB(2) + "IntegrationStepSize::instance()->setValue(value);\n" )
        out.write ( TAB(2) + "IntegrationStepSize::instance()->saveValue(\"%s\", value);\n" % SplitCamelCase(self.name) )
        out.write ( TAB(1) + "}\n" )
        out.write ( """
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
""")

        out.write( "}\n" )
        out.write( r"""
void %sParameterDialog::evalTogglesCallback(GLMotif::ToggleButton::ValueChangedCallbackData* cbData)
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
""" % self.name)
        out.write( "\n" )


from xml.dom import minidom
import os

class CodeGenerator:
    """ Parses xml file containing description of dynamical systems and
    generates plugin code (C++).
    """

    def __init__(self):

        self.systems = []  # list of all dynamical systems

        self.plugin_dir = "./Dynamics/plugins/"

    def generate_code(self):

        if not os.path.isdir(self.plugin_dir):
            os.mkdir(self.plugin_dir)

        for sys in self.systems:

            dynamics_h    = self.plugin_dir + sys.name + ".h"
            dynamics_cpp  = self.plugin_dir + sys.name + ".cpp"
            parameter_h   = self.plugin_dir + sys.name + "ParameterDialog.h"
            parameter_cpp = self.plugin_dir + sys.name + "ParameterDialog.cpp"

            print "  generating " + dynamics_h + "..."
            sys.generate_dynamics_header(open(dynamics_h,     'w'))

            print "  generating " + dynamics_cpp + "..."
            sys.generate_dyamics_source(open(dynamics_cpp,    'w'))

            print "  generating " + parameter_h + "..."
            sys.generate_parameter_header(open(parameter_h,   'w'))

            print "  generating " + parameter_cpp + "..."
            sys.generate_parameter_source(open(parameter_cpp, 'w'))

        print "  generating makefile fragment..."
        self.generate_makefile_fragment()

    def generate_makefile_fragment(self):

        fragment = open('etc/plugin.mk', 'w')

        for sys in self.systems:

            fragment.write( "plugins/lib%s.so: obj/Dynamics/plugins/%s.o obj/Dynamics/plugins/%sParameterDialog.o\n" % (sys.name, sys.name, sys.name) )
            fragment.write( "obj/Dynamics/plugins/%s.o: Dynamics/plugins/%s.cpp\n" % (sys.name, sys.name) )
            fragment.write( "obj/Dynamics/plugins/%sParameterDialog.o: Dynamics/plugins/%sParameterDialog.cpp\n" % (sys.name, sys.name) )
            fragment.write( "\n" )

    def print_sys_info(self):

        for sys in self.systems:

            print "SYSTEM: %s" % sys.name

            for param in sys.parameters:

                print "\t%10s (%s, %s, %s) [%s]" % (param.name,
                                                    param.min,
                                                    param.max,
                                                    param.step_size,
                                                    param.default)

            print

            for (label, eqn) in sys.equations.items():

                print "\t%s: %s" % (label, eqn)


    def parse(self, filename):
        """ Parse the XML document and initialize the systems list.
        """
        print "  parsing xml file..."

        # create the xml parser object
        doc = minidom.parse(filename)

        # for all dynamical systems
        for sys in doc.getElementsByTagName('system'):

            # create a new dynamical system
            system = DynamicalSystem(sys.getAttribute('name'))
            if sys.hasAttribute('nice_name'):
               system.nice_name = sys.getAttribute('nice_name')

            # for each parameter in the system
            for param in sys.getElementsByTagName('param'):

                # create a parameter data structure and add to current system
                system.parameters.append(Parameter(param.getAttribute('name'),
                                                   param.getAttribute('min'),
                                                   param.getAttribute('max'),
                                                   param.getAttribute('step'),
                                                   param.getAttribute('default')))

            # add equations to current system
            system.equations['x'] = sys.getElementsByTagName('x_vel')[0].firstChild.data
            system.equations['y'] = sys.getElementsByTagName('y_vel')[0].firstChild.data
            system.equations['z'] = sys.getElementsByTagName('z_vel')[0].firstChild.data

            # get center position
            ctr = sys.getElementsByTagName('center')[0]
            system.center['x'] = ctr.getAttribute('x')
            system.center['y'] = ctr.getAttribute('y')
            system.center['z'] = ctr.getAttribute('z')


            # add current system to systems list
            self.systems.append(system)


import sys

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "  USAGE:  generate_plugin_code [XML file]"
        sys.exit(1)

    xmldoc = sys.argv[1]


    generator = CodeGenerator()

    generator.parse(xmldoc)

    #generator.print_sys_info()

    generator.generate_code()


