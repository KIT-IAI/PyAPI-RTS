.. _connection_graph:

Graph
=====

The **graph** represents the connections between components in the model.
It is crucial for topology-based queries and operations on the model and can be generated for each individual *Container* component or for the whole *Draft*.

The **graph** represents components with their UUIDs and provides additional information regarding the connections in its edges.

Edge attributes
---------------

``type: EdgeType``
^^^^^^^^^^^^^^^^^^

- ``GRID``
    - Default connection type. This is defined by connection points touching on the grid.
    - Usually, a BUS or WIRE component is used to connect two components.
    - These connections have additional attributes defining the connection points involved.
- ``NAME``
    - Connections defined by bus labels touching hierarchies.
    - Characterized by node type `NAME_CONNECTED`.
- ``LABEL``
    - Connections defined by wire labels and signal names of components.
- ``TLINE``
    - Connections between endpoints of a transmission line or cable.
- ``XRTRF``
    - Connections between endpoints of a cross-rack transformer.
- ``LINK``
    - Connections defined by linked bus labels or nodes.
    - Connect over one or multiple hierarchies without grid connection.
    - Characterized by node type `NAME_CONNECTED_LINKED`.
    - Used in rtds_sharc_node and rtds_sharc_sld_BUSLABEL
- ``TLINE_CALC``
    - Connections between the endpoints of a transmission line or cable and the corresponding calculation block.

``xrack: bool``
^^^^^^^^^^^^^^^

- line, cable and cross-rack transformer
- signal import/export

``<uuid>: list[str]`` (Connection points)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- List of connection points involved in the connection for the *Component* with the corresponding ``uuid``.

Performance considerations
--------------------------

The graph is generated on demand to avoid long delays when the model is loaded.
The graph is in part based on the so-called **position dictionary** that maps coordinates in a *Container* to UUIDs of *Components* and the *ConnectionPoints* at these coordinates.
This dictionary is updated whenever a component is added, removed or updated using the methods provided by the *Container*.
The connections not based on the grid are generated on demand (every time) when the graph is requested.
 

