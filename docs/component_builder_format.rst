.. _component_builder_format:

Component Builder File Format
=================================

Introduction
------------
The Component Builder file format is a format used by RSCAD FX 1.0 and later to define a component type.
The format consists of a simple text file structures by indentations.
While the basic structure resembles :doc:`dfx_files` **Type A Nodes**, the format is far more complex than the simple key-value pairs used in .dfx files.

Like the CBuilder application, the file contains multiple sections defining different properties of the component type.

**This documentation only documents the parts of the Component Builder format parsed and used by the current version of pyapi_rts. Other sections are omitted.**

Structure of the Component Builder Format
-----------------------------------------

The first line of the file is the string 'Component Builder' followed by the file version used.
After that, different sections are defined by indentations, with an unindented line before describing the type of the block.

.. code-block::
    :caption: An example of a node in a Component Builder file

    PARAMETERS:
        SECTION: "CONFIGURATION"
            LW1  "Bus thickness (Single Phase)"         "" 5 REAL 3.0 0.0
            SCOL "Bus Color"                   "RED;BLACK;BLUE;GREEN;CYAN;ORANGE;MAGENTA;PINK;WHITE;BROWN;GOLD;VIOLET;YELLOW;LIGHT_GRAY" 10 TOGGLE   ORANGE
        DOCUMENT "include in print->parameters?"     "NO;YES" 10 TOGGLE 0
        SECTION: "HIDDEN PARAMETERS" false
          x1 "x1"  " " 4 INTEGER -32 0 0 false
          y1 "y1"  " " 4 INTEGER -0 0 0 false
          x2 "x2"  " " 4 INTEGER 32 0 0 false
          y2 "y2"  " " 4 INTEGER 0 0 0 false


Indentations
^^^^^^^^^^^^

Indentations are used to define sections, but are inconsistent in a lot of cases.
For this reason, some sections use custom parsers to build the block tree correctly.
There can be no guarantee that sections and other hierarchies are recognized correctly, but there are warnings for unrecognized structures.



Parameter Section
^^^^^^^^^^^^^^^^^

The *PARAMETERS:* node defines the parameters of the component type.
Parameters can be grouped into sections or be defined directly in the node.
Grouped parameters are defined in a *SECTION: "<name>"* node.

The parameters themselves are defined in a line with the following format:

<key> "<description>" "<toggle>" <?> <type> <default> <min>? <max>? <enabled_condition>?

    Notes:

    * All parts marked with <...>? are optional.

    * The *key* is the name of the parameter.
    * The *description* is a short description of the parameter.
    * The *toggle* lists the possible values of the parameter, separated by semicolons.
    * The *<?>* can be ignored after parsing.
    * The *type* is the type of the parameter.
    * The *default* is the default value of the parameter.
    * The *min* and *max* are the minimum and maximum values of the parameter.
    * The *enabled_condition* is a logical expression that determines whether the parameter is enabled or not. The language used for conditions is describled in the sections about conditions.

Example::

    x1 "x1"  " " 4 INTEGER ^32 0 0 false

The following types are supported in the <type> field:

+-----------------+-------------------------------------------------------+
| Type            | Description                                           |
+=================+=======================================================+
| REAL            | A real number                                         |
+-----------------+-------------------------------------------------------+
| CHAR            | A character                                           |
+-----------------+-------------------------------------------------------+
| NAME            | A string the enumerator is applied to                 |
+-----------------+-------------------------------------------------------+
| TOGGLE          | A value from the <toggle> list                        |
+-----------------+-------------------------------------------------------+
| INTEGER         | An integer                                            |
+-----------------+-------------------------------------------------------+
| COLOR           | A color supported by RSCAD                            |
+-----------------+-------------------------------------------------------+
| HEX             | A hexadecimal number                                  |
+-----------------+-------------------------------------------------------+
| FILE            | A file path                                           |
+-----------------+-------------------------------------------------------+

Directives Section
^^^^^^^^^^^^^^^^^^

The *DIRECTIVES:* node contains directives that are applied to the component type.
They have the format **<KEY> = <VALUE>**.

The following directives are currently supported by pyapi_rts:
STRETCHABLE

+---------------------------+-------------------------------------+
| Value                     | Description                         |
+===========================+=====================================+
| STRETCHABLE_DIAG_LINE     | Can be stretched in any direction   |
+---------------------------+-------------------------------------+
| STRETCHABLE_BOX           | Horizontal/Vertical streching       |
+---------------------------+-------------------------------------+
| STRETCHABLE_UP_DOWN_LINE  | One strechable axis                 |
+---------------------------+-------------------------------------+

Nodes Section
^^^^^^^^^^^^^

Nodes are defined in the *NODES:* section.
Nodes are the points at which the component can connect to other components.
In the Component Builder file, they are encoded in one line per node.
Conditions are supported in this section as blocks, as described in the next section.

<name> <x-position> <y-position> <mode> [PHASE=<phase>]? <linked>? <...>?

    Notes:

    * Every <>? and []? entry is optional.
    * The *<name>* is the name of the node.
    * The *<x-position>* and *<y-position>* are relative to the component's origin.
    * *<x-position>* and *<y-position>* can use parameter values with the '$key' syntax.
    * The *<mode>* is the mode of the node and is ignored after parsing.
    * The *<linked>* is the type of the node, pyapi_rts supports NAME_CONNECTED or a missing entry.
    * The *<phase>* is the phase of the node, starting with 'PHASE='.
    * The *<...>* is ignored after parsing.

.. code-block:: text
    :caption: Example

    A_1  $x 0     EXTERNAL PHASE=A_PHASE NAME_CONNECTED:LINKED


Conditions
^^^^^^^^^^

Conditions are boolean expressions using the value of parameters and logical operators.
They are supported in multiple places in the Component Builder file and can be nested in other conditions, creating complex decision trees.
This enables component to change their properties based on their parameters.

Conditions consist of the condition line and indented lines following it that are only active when the conditions evaluates to true.

Structure of the condition::

    <#IF> <expression> <operator> <expression>
        content
    <#ELSEIF> <expression> <operator> <expression>
        content
    <#ELSE>
        content
    #END

Notes:

    * The *<#ELSEIF>* and *<#ELSE>* blocks are optional.
    * The *<#END>* line is optional if another #IF condition follows.
    * The content does not need to be indented if the block ends with a #END line.
    * The *<expression>* is a parameter value or another logical expression.
    * The *<operator>* is a logical operator.
    * The *<content>* is active if the condition evaluates to true.

Supported operators on numbers:


+----------+----------------------+
| Operator | Description          |
+==========+======================+
|| ==      || Equal with toggle   |
||         || evaluated as number |
+----------+----------------------+
| =        | Equal on numbers     |
+----------+----------------------+
| !=       | Not Equal            |
+----------+----------------------+
| <=       | Smaller or equal     |
+----------+----------------------+
| <=       | Greater or equal     |
+----------+----------------------+
| >        | Greater              |
+----------+----------------------+
| <        | Smaller              |
+----------+----------------------+

**The toggle operator '==' converts the value of the parameter to its index in the list of possible values for the parameter.**



Supported operators on boolean expressions:

+------------------------+------------------------+
| Operator               | Description            |
+========================+========================+
| &&                     | And                    |
+------------------------+------------------------+
| \|\|                   | Or                     |
+------------------------+------------------------+