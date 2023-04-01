.. _connection_graph:

Connection Graph
================

Introduction
------------

The **Connection Graph** is generated for each *Component Box* in the model.
It represents the connection between the components using the components as nodes.

Using an additional **Link Dictionary**, the connection graphs themselves can be merged into a graph of the whole model or just identify the connections to other *Component Boxes*.

When are two components connected?
----------------------------------

Whether two components are connected differs between the graph itself , the get_connected_to() method and the get_connected_at_point() method.

+---------------------------+----------------------------------------+-------------------------------+-----------------------------------------------+----------------+
| **Type**                  | **Advantages**                         | **Disadvantages**             | **Rules**                                     | Hook available |
+---------------------------+----------------------------------------+-------------------------------+-----------------------------------------------+----------------+
|| Graph                    || - Internal                            || - Not across Component Boxes || At least connection point of the two         || Yes           |
||                          || - Accurate to RSCAD draft mode        || - Only UUIDs are returned    || components overlap.                          ||               |
||                          || - Lazily evaluated and cached         ||                              ||                                              ||               |
+---------------------------+----------------------------------------+-------------------------------+-----------------------------------------------+----------------+
|| get_connected_to()       || - Easy to use                         || - Inflexible                 || Connected on graph or by name                || No            |
||                          || - Uses (cached) graph when available  ||                              ||                                              ||               |
||                          || - Mostly accurate to RSCAD simulation ||                              ||                                              ||               |
+---------------------------+----------------------------------------+-------------------------------+-----------------------------------------------+----------------+
|| get_connected_at_point() || - Useful for following signal from    || - Doesn't use caching        || Connected between the connection points only || No            |
||                          || specific connection point             ||                              || via 'connecting components', i.e. bus etc.   ||               |
||                          || - Simple search for i.e. manager      ||                              ||                                              ||               |
+---------------------------+----------------------------------------+-------------------------------+-----------------------------------------------+----------------+

Most of the time, only one of these options is suited for a specific use case.

Generation and updates
----------------------

The connection graph is generated on first use to avoid long delays when the model is loaded.
It is updated whenever a component is added, removed or modified in a way that changes the connection points.

Every time the graph is generated or updated, the **Position Dictionary** and **Link Dictionary** are also updated.

Cloned and referenced components
--------------------------------

To improve performance, the :code:`get_components()` method in the `ComponentBox` class has a *clone* parameter.
If this is set to True, the returned components are clones of the original components.
If this is set to False, the returned components are references to the original components.

Changing referenced components can cause the connection graph to be invalid.
This can not be detected by pyapi_rts and should be avoided.
 

Types of connections
====================

- grid-based connections 
    - e.g. via BUS or WIRE
- grid-based connections over multiple hierarchies
    - e.g. BUSLABEL connected to HIERARCHY via BUS
    - characterized by node type `NAME_CONNECTED`
- label based connections 
    - i.e. wirelabel and signal names of components
- linked node connections 
    - connect over one or multiple hierarchies without grid connection
    - characterized by node type `NAME_CONNECTED_LINKED`
    - used in rtds_sharc_node and rtds_sharc_sld_BUSLABEL
- cross-rack connections
    - line, cable and cross-rack transformer
    - signal import/export