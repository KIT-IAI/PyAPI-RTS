.. _component_extensions:

Component Extensions
====================

.. warning:: Difference to hooks
    **Component Extensions** extend the functionality of individual components. If you want to add new functionality to the whole API, you should use hooks if available.

Idea
----

**Component Extensions** enable the user to add new functionality on top of the existing, generic methods provided by the Component class and the ComponentBox class.
This functionality is specified on a per-component basis, e.g. a new method specific to BUS components.

Extension Directory Structure
-----------------------------

.. code-block:: text

    pyapi_rts/class_extractor/extensions
    |
    +---<extension_name>
        |
        +---<extension_for_BUS.py>
        |
        +---<extension_for_WIRE.py>
        |
        +---<shared_class.py>
        |
        +---<extension_name_test.py>


An extension directory can contain three types of files, subdirectories are ignored:
    * **<extension_name>.py**: The extension class for one specified component type. This file must be a valid python class extending the Component class and contain a line with a *#EXTENDS: <component_type>* statement.
    * **<shared_class>.py**: Shared code that can be used by multiple extensions. This file can contain any valid python code that does not contain an *EXTENDS* statement. 
    * **<extension_name_test.py>**: A test file that can be used to test the extension. Only one test class per extension is allowed.



Create a new Extension
----------------------

Add a new extension to the pyapi_rts/class_extractor/extensions directory.
The minimal extension must contain a **<component_extension>.py** file and a **<extension_name_test.py>** file.
The **<component_extension>.py** file must contain a line with a

.. code-block:: text

    *#EXTENDS: <component_type>*

statement.    

Imports in Extensions
---------------------

Only the methods following the *#EXTENDS:* statement are copied to the component classes.
The shared code is made available to the extension classes automatically, but it might still be useful to import them manually to get autocomoplete support during development.

If an import is required in the component extension class, the import statement has to be after the *#EXTENDS:* statement.

Testing the Extension
---------------------

During the :doc:`ClassExtractor <class_extractor_usage>` run, the **<extension_name_test.py>** file is copied to the *tests/extensions* directory. The test can be executed with *poetry run pytest*, and is executed in the *extensions_test* stage of the GitLab pipeline, but not in the *test* stage.

Including and Excluding Extensions in the ClassExtractor
--------------------------------------------------------

By default, all extensions are included in the ClassExtractor run.
If the *-e / --extensions* option is set to 'false', extensions are ignored.
If only certain extensions should be excluded, use the *--exclude-ext* option.

For more information, see the :doc:`ClassExtractor <class_extractor_usage>` documentation.