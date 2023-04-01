.. _examples:

Examples
========

Creation of empty model
-----------------------

.. code-block:: python
    :caption: Create and save empty model
    :linenos:

    from pyapi_rts.api.draft import Draft
    from pyapi_rts.api.subsystem import Subsystem

    if __name__ == '__main__':
        draft = Draft() 
        subsystem = Subsystem(draft, 1)
        subsystem.canvas_size_x = 1000
        subsystem.canvas_size_y = 1000
        subsystem.tab_name = "Test"
        draft.add_subsystem(subsystem)
        draft.write_file("test.dfx")
   
Basic editing of model
----------------------

.. code-block:: python
   :caption: Simple example
   :linenos:

   from pyapi_rts.api import *

   # Load a RSCAD file
   draft = Draft()
   draft.read_file(PATH / "bus_rings.dfx")

   # Get a specific component and the components connected to it
   buslabel1 = draft.subsystems[0].search_by_name("BUS1")[0]
   connected_to_bus1 = draft.subsystems[0].get_connected_to(buslabel1)

.. code-block:: python
    :caption: Load, edit and save model
    :linenos:

    import pathlib
    from pyapi_rts.api.draft import Draft
    from pyapi_rts.api.subsystem import Subsystem
    from pyapi_rts.classext2.generated.BUSComponent.BUSComponent import BUSComponent

    PATH = pathlib.Path(__file__).parent.resolve()

    if __name__ == '__main__':
        draft = Draft() 
        draft.read_file(PATH / 'test.dfx')
        bus_component : BUSComponent = draft.get_components()[0]
        bus_component.CONFIGURATION.SCOL.set_str('RED')
        draft.subsystems[0].modify_component(bus_component)
        draft.write_file(PATH / 'test_out.dfx')

.. code-block:: python
    :caption: From the thesis, p. 39 (Bus coloring)
    :linenos:

    import networkx as nx
    import random

    from pyapi_rts.api import *
    from pyapi_rts.generated.BUSComponent import BUSComponent
    from pyapi_rts.generated.rtdssharcsldBUSLABELComponent import rtdssharcsldBUSLABELComponent
    from pyapi_rts.generated.enums.ScolEnumParameter import ScolEnum

    fx = Draft()
    fx.read_file("ieee14.dfx")

    G = fx._subsystems[0].get_connection_graph()
    SG = G.subgraph([n for n, attrdict in G.nodes(data=True) if not "3P2W" in attrdict['type']])

    start_nodes = [n for n, ad in G.nodes(data=True) if ad['type'] == 'rtds_sharc_sld_BUSLABEL']
    bus_list = fx.get_components_by_type("BUS", False)

    colors = list(ScolEnum)
    colors.remove(ScolEnum.WHITEWHITE)

    for start in start_nodes:
        id_list = list(nx.dfs_postorder_nodes(SG, source=start))
        col = random.choice(colors)
        count = 0
        for bus in bus_list:
            if bus.uuid in id_list:
                bus: BUSComponent = bus
                bus.CONFIGURATION.SCOL.set_value(col)
                count += 1
                fx._subsystems[0].modify_component(bus)
        buslabel: rtdssharcsldBUSLABELComponent = fx._subsystems[0].get_by_id(
            start, False)
        buslabel.Parameters.COL.set_value(col)
        print(f"Found {count} buses, coloring with {col}")
        fx._subsystems[0].modify_component(buslabel)

    fx.write_file("ieee_out.dfx")