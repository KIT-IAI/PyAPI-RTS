# LAYOUT CONSTANTS

# WEIGHT is an internal integer attribute to properly position the nodes in each column,
#  respecting the structure of neighboring columns
WEIGHT = '_weight'

# COLUMN is a grid coordinate for the x-axis where 0 is the tree root and numbers are increased by 1 per
#  step to the right
COLUMN = '_column'

# MIN_HEIGHT indicates the minimum space in grid units that this node consumes. This depends on the subtree below the
#  respective node
MIN_HEIGHT = '_min_height'

# MIN_ROW and MAX_ROW specify a grid coordinate in the y-axis where 0 is on the top, increasing by 1 downward step
# TODO check value direction of MIN_ROW, MAX_ROW
MIN_ROW = '_min_row'
MAX_ROW = '_max_row'

# A tuple of min and max y coordinate in grid coordinates
VERTICAL_POSITION = '_vertical_position'


# GRAPHVIZ CONSTANTS

# The graphviz node height attribute
GV_HEIGHT = 'height'

# The graphviz node position attribute
GV_POS = 'pos'


# RSCAD CONSTANTS

# COMPONENT_TYPE needs to contain the exact type name of the component in RSCAD that the node shall represent
COMPONENT_TYPE = '_component_type'

# EDGE_TYPE needs to contain the type of the edge this can currently be one of 'ABC', 'A', 'B', 'C', 'DATA'
EDGE_TYPE = '_edge_type'
