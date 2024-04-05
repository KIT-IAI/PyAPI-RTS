# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA


from pyapi_rts.shared import ParameterBoundProperty


class BoundingBox:
    """The bounding box of a component rectangle."""

    def __init__(
        self,
        x1: int | str,
        y1: int | str,
        x2: int | str,
        y2: int | str,
        norotate: bool = False,
        nomirror: bool = False,
    ) -> None:
        """Initialize the BoundingBox object.

        :param x1: Relative x-position of left border.
        :type x1: int | str
        :param y1: Relative y-position of top border.
        :type y1: int | str
        :param x2: Relative x-position of right border.
        :type x2: int | str
        :param y2: Relative y-position of bottom border.
        :type y2: int | str
        """
        # Relative x-position of left border.
        self.x1 = ParameterBoundProperty(x1, int)
        # Relative y-position of top border.
        self.y1 = ParameterBoundProperty(y1, int)
        # Relative x-position of right border.
        self.x2 = ParameterBoundProperty(x2, int)
        # Relative y-position of bottom border.
        self.y2 = ParameterBoundProperty(y2, int)
        self.norotate = norotate
        self.nomirror = nomirror

    def evaluate(
        self, dictionary: dict, rotation: int = 0, mirror: int = 0
    ) -> tuple[int, int, int, int]:
        """Evaluate the parameter bound bounding box to an integer tuple.

        :return: The integer tuple.
        :rtype: tuple[int, int, int, int]
        """

        rot = rotation % 4
        mir = mirror % 2

        bbox: list[int] = [
            self.x1.get_value(dictionary),
            self.y1.get_value(dictionary),
            self.x2.get_value(dictionary),
            self.y2.get_value(dictionary),
        ]

        if not self.nomirror and mir == 1:
            x2 = bbox[2]
            bbox[2] = -bbox[0]
            bbox[0] = -x2

        if not self.norotate:
            while rot > 0:
                last = bbox.pop()
                bbox.insert(0, -1 * last)
                bbox[2] *= -1
                rot -= 1

        return bbox

    def init_code(self) -> str:
        x1 = self.x1.get_direct_value()
        y1 = self.y1.get_direct_value()
        x2 = self.x2.get_direct_value()
        y2 = self.y2.get_direct_value()

        x1_str = str(x1) if isinstance(x1, int) else f'"{x1}"'
        y1_str = str(y1) if isinstance(y1, int) else f'"{y1}"'
        x2_str = str(x2) if isinstance(x2, int) else f'"{x2}"'
        y2_str = str(y2) if isinstance(y2, int) else f'"{y2}"'

        return (
            f"BoundingBox({x1_str}, {y1_str}, {x2_str}, {y2_str}, {self.norotate}, {self.nomirror})"
        )
