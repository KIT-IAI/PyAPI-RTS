====================
.dfx File Format
====================

The .dfx file format is a format used by RSCAD FX 1.0 and later versions to store an energy network.
It is a plain-text based format that used indentations to define the structure of the file as a tree, with key-value pairs at the leaves.

The nodes of this tree come in two formats, **Type A** and **Type B**.
**Type A** nodes consist of a title line ending in a colon, followed by the indented content of the node.
**Type B** nodes start and end with a line '{title}-START:' and '{title}-END:' respectively. The content of the node is not indented.

.. code-block::
    :caption: Example of a Type A node.

    GRAPHICS:
        CANVAS_WIDTH: 1481
        CANVAS_HEIGHT: 568
        CURRENT_SUBSYSTEM_IDX: 0
        DEFAULT_VIEW_MODE: 3
        DEFAULT_ZOOM: 100
        DEFAULT_TOP_LEFT_POINT: 0,0

.. code-block::
    :caption: Example of a Type B node.

    PARAMETERS-START:
    LW1: 0.5
    SCOL: ORANGE
    PARAMETERS-END:

Structure of the .dfx file
==========================
A .dfx file consists of multiple sections making up the tree.

#. The first line, starting with 'DRAFT', followed by the format version.
#. GRAPHICS section, which contains information about the state of the view in RSCAD at time of storage.
#. DATA section with metadata about the model.
#. COMPONENT-ENUMERATION with information used by RSCAD for auto-enumeration.
#. SUBSYSTEM section with an enumeration of the subsystems in the model.


Components
----------
Components are represented by a Type A 'COMPONENT-TYPE' node.
The first line of the node contains the position and rotation of the component in multiple integer values, not in a key-value pair like all other information in the file.
This is followed by a Type B 'PARAMETER' block with the values of the parameters of the component.
The last block is a Type A 'ENUMERATION' block with the values of the enumeration parameters of the component.

Enumeration
-----------
Enumeration blocks contain four lines in the following format:

+----+---------------------------------+----------------------------------------+
|Line|Description                      |Format                                  |
+====+=================================+========================================+
|1   |Enumeration is active            |true/false                              |
+----+---------------------------------+----------------------------------------+
|2   |Enumeration index                |int                                     |
+----+---------------------------------+----------------------------------------+
|3   |Enumeration type                 |Integer/Hex/                            |
|    |                                 |uppercase/lowercase                     |
+----+---------------------------------+----------------------------------------+
|4   |Enumeration string               |string                                  |
+----+---------------------------------+----------------------------------------+

Subsystems, Hierarchies and Groups
----------------------------------
Every model contains one or multiple Subsystems with a canvas on which components are placed.
In the Subsystem section, the subsystems are enumerated.
The Subsystems themselves are SUBSYSTEM Type B nodes.
In them, first the information about the canvas is defined and then the components are listed.

Subsystems can contain further canvases in Hierarchy components.
Those are defined in the list of components like any other component, but are nested in a HIERARCHY Type B block.
This block contains the Hierarchy component itself and the list of components that are nested in it.

.. code-block:: 
    :caption: Example of a Hierarchy node.

    HIERARCHY-START:
    COMPONENT_TYPE=HIERARCHY
        208 432 0 0 39
        PARAMETERS-START:
        Name	:box#
        x1	:-32
        y1	:-32
        x2	:32
        y2	:32
        PARAMETERS-END:
        ENUMERATION:
            true
            0
            Integer
            #
    RUNTIME-OVERLAY-START: view VIEW-TYPE: DRAFT-VIEW VIEW-ID: test
    RUNTIME-OVERLAY-END:
    COMPONENT_TYPE=BUS
        240 144 0 0 7
        PARAMETERS-START:
        LW1	:3.0
        SCOL	:ORANGE
        DOCUMENT	:NO
        x1	:-32
        y1	:-0
        x2	:32
        y2	:0
        PARAMETERS-END:
        ENUMERATION:
            true
            0
            Integer
            #

Groups
------

A group is a collection of components that can only be selected together in RSCAD.
In .dfx files, groups contain the components in them in a a GROUP Type B node.
The first component in the list is a GROUP component with only the 'COMPONENT-TYPE' line and the position line.

.. code-block:: 
    :caption: Example of a Group block.
    
    GROUP-START:
    COMPONENT_TYPE=GROUP
        1136 464 0 0 0
    ...
    GROUP-END:
    
Components are added to groups by adding them to the corresponding group component with the add_component() method.
Components in groups are only returned by the get_components() method if 'with_groups' is True or 'recursive' is set to True.
The getConnectedTo() method and the connection graph contain the components in groups.
However, the modify_component() and and remove_component() methods need to have 'recursive' set to True to modify the component in a group from the hierarchy/subsystem.