# We consider a Component Graph to be a networkx Graph that has a node per component in RSCAD and also has
#  an edge to represent a connection bus or wire between the components.
#  This means that the BUS and wire components are not considered components in that sense.
#  Each Edge has the "_type" property that indicates what kind of connection it is. Currently, we allow the values:
#  - ABC
#  - A
#  - B
#  - C
#  - DATA
# For components, any non-default value is encoded as a key-value pair on the networkx node. Furthermore,
#  attributes required for rendering / layout can be included with a "_" prefix.
