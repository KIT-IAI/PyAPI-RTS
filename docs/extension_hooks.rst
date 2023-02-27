.. _hooks:

Extension Hooks
===============

.. warning:: 
    **Extension Hooks** are distinct from the **Component Extensions**.
    Extension hooks are a way to extend the functionality of the API, for example the graph generation, and are called during the runtime.
    **Component Extensions** on the other hand extend new functionality to the components and are added to the classes during the **Class Extractor** rum  and used by the user during runtime.

Introduction
------------

Some component behavior and interactions between them are defined not at all or not in an easily readable way in the :ref: `Component Builder Format<component_builder_format>` files. The behavior needs to be implemented in the API manually.
**Extension hooks**  enable the addition of new functionality to the API in a structured way, for example adding new connections to the connection graph.

list of available Hooks
-----------------------

+--------------------+------------------------------+----------------------------------------------------+-------------------------------------------------------------------+
| Name               | Arguments                    | Returns                                            | Function                                                          |
+--------------------+------------------------------+----------------------------------------------------+-------------------------------------------------------------------+
|| Graph connections || components: list[Component] || list[tuple[str, str]]                             || Adds new connections between components on the connection graph. |
||                   || pos_dict                    || *Graph connection between nodes with these UUIDs* ||                                                                  |
||                   || link_dict                   ||                                                   ||                                                                  |
+--------------------+------------------------------+----------------------------------------------------+-------------------------------------------------------------------+
|| Link connections  || components: list[Component] || list[tuple[str, str]]                             || Adds new entries to link_dict                                    |
||                   ||                             || *New link_dict entries in form (name, UUID)*      ||                                                                  |
+--------------------+------------------------------+----------------------------------------------------+-------------------------------------------------------------------+


Adding new Hooks
----------------

A hook is a Python class extending the :class:`~.ComponentHook` class.

The hooks are class methods, so no state should be stored within the hook class.

Not all hook methods need to be implemented by a hook class.

Hooks need to be added to the :code:`pyapi_rts/class_extractor/hooks` directory and are copied during the Class Extractor run.

Testing
^^^^^^^

As hooks are used as extension of the API functionality they can be tested with regular unit tests in the :code:`tests` directory.
The functionality implemented by hooks represents logic from RSCAD and is not optional, unlike Component Extensions.
Nevertheless, it is advised to make clear that a test relies on a specific hook to make debugging easier.


Using Hooks vs. extending API
-----------------------------

When should a hook be used as opposed to extending the core API?

A hook provides a simple entry point for extending specific functionality and groups them together in one file.
This makes it particularly useful for more functionality that represents edge cases like connections that only apply to a few components in a specific arrangement.
In contrast, extending the API itself is useful every time a change can be used for a larger set of components or for changes that are read directly from the *Component Builder* files.

As an example, the TLineHook class (:class:`~.TLineHook`) is used to attach Tline components to the Tline Calculation Box. This connection is not specified in the Component Builder files and needs to be implemented manually, while only affecting a few specific arrangements of components.
