.. _glossary:

Glossary
========

General
-------

.. glossary::

    RSCAD FX
        Software developed by RTDS for the configuration, execution and analysis of real-time simulations.
        `Link <https://www.rtds.com/technology/graphical-user-interface/>`_.

    CBuilder
        Software for creation and editing of **Component Builder files**.
        Included in RSCAD FX distributions.

    Runtime     
        Software for execution and monitoring of real-time simulations on RTDS hardware simulators.
        Included in RSCAD FX distributions.

    TLine
        Software for creation and editing of **TLine (\*.tli) files**.
        Included in RSCAD FX distributions.

pyapi_rts
---------

.. glossary::
    Draft
        The information from a \*.dfx file.
        Can contain one or more **subsystems** and some metadata.
    
    Subsystem
        A canvas on which **components** and **component boxes** are placed.

    Component Box
        A set of components on a canvas and their connections to each other.
        The basis for **Subsystems**, **Hierarchies** and **Groups**.
        See :ref:`Connection Graph <connection_graph>` for more information.

    Hierarchy
        A component that is a **Component Box** at the same time.
        Through connections to the component, connections to components within the **Component Box** can be established.
        A hierarchy can contain other hierarchies, allowing for better readability of the model.

    Group
        Technically a **component**, but the contained components are drawn on the parent canvas.
        In RSCAD FX, grouped components can be moved together and not edited while grouped.

    Component
        A element that can be placed on a canvas.
        A component has a type, which are defined in :ref:`Component Builder files <component_builder_format>`.
     
File Types
----------
     
.. glossary:: 
    
    Component Builder
        A Component Builder file describes how a given component is drawn on the canvas, what connections and parameters it has and more.

    \*.dfx: Draft
        Contains the draft of a model, meaning the subsystems and metadata.

    \*.tli: TLine
        Describes the properties of a type of transmission line.

