# Tests for Transmission Line Connections

- tline_linked: Base case 
    - 2 buses connected by a transmission line
- tline_linked_2ss: Cross rack case 
    - 2 buses connected by a transmission line across two subsystems
- tline_linked_bus_linked: Linked tlines and buses
    - BUS1 and BUS2 connected by TLINE1
    - TLINE1 is also the name of a linked bus with 2 instances
    - The connections of the transmission line and the bus should not be confused