# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA


from pyapi_rts.shared import Stretchable
from pyapi_rts.shared.condition_tree import ConditionTreeNode


class ExtRectangle:
    """
    A rectangle around a RSCAD component with a given position, width and height.
    """

    def __init__(self):
        """
        Initializes the ExtRectangle object.

        :param x: X position, defaults to 0
        :type x: int, optional
        :param y: Y position, defaults to 0
        :type y: int, optional
        :param width: Width, defaults to 0
        :type width: int, optional
        :param height: Height, defaults to 0
        :type height: int, optional
        """
        super().__init__()
        #: Condition tree for the graphics instructions.
        self.graphics: list[ConditionTreeNode] = None
        #: Condition tree for the connection points.
        self.connection_points: list[ConditionTreeNode] = None
        #: Stretchable type.
        self.stretchable: Stretchable = Stretchable.NO
        # Name of the rectangle.
        self.name = "RECT"
        #: Component is linked to one or more other components.
        self.linked: bool = False

    def write_lines(self) -> list[str]:
        """
        Writes the ExtRectangle object to a list of strings.

        :return: Lines of strings.
        :rtype: list[str]
        """
        lines = []
        lines.append("RECT")
        lines.append("END")
        return lines

    def component_init(self) -> list[str]:
        """
        Returns the component initialization code in Python.

        :return: The component initialization code.
        :rtype: list[str]
        """
        output = []
        stretchable = "Stretchable." + self.stretchable.name
        output.extend(
            [
                f"self.stretchable = {stretchable}",
                f"self.linked = {str(self.linked)}",
            ]
        )
        return output

    def rectangle_functions(self) -> list[str]:
        """
        Returns the rectangle functions in Python.

        :return: The rectangle functions as Python code.
        :rtype: list[str]
        """
        bbox = self._generate_bbox_tree()
        conn_points = self._generate_connection_points()
        return bbox + [""] + conn_points

    def _generate_connection_points(self) -> list[str]:
        out = ["result = {}"]
        if self.connection_points is not None:
            for x in self.connection_points:
                out += x.to_code()

        out += ["return result"]

        return [
            "def connection_points_from_dict(self, dictionary) -> dict[str, ConnectionPoint]:",
        ] + [f"    {i}" for i in out]

    def _generate_bbox_tree(self) -> list[str]:
        out = ["bboxes: list[BoundingBox] = []"]
        if self.graphics is not None:
            for x in self.graphics:
                out += x.to_code()

        out += ["if len(bboxes) == 0:"]
        out += ["    return (0, 0, 0, 0)"]
        out += ["int_bboxes = []"]
        out += ["for bbox in bboxes:"]
        out += [
            "    int_bboxes.append(bbox.evaluate(dictionary, self.rotation, self.mirror))"
        ]
        out += ["result = self._calc_bounding_box(int_bboxes)"]
        out += ["if absolute:"]
        out += ["    return (result[0] + self.x, result[1] + self.y, result[2] + self.x, result[3] + self.y)"]
        out += ["return result"]

        return [
            "def bounding_box_from_dict(self, dictionary: dict, absolute: bool = False) -> tuple[int, int, int, int]:",
        ] + [f"    {i}" for i in out]
