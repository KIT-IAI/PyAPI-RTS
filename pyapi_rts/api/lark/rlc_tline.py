# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import os

from pyapi_rts.api.lark.tli_transformer import TliFile, TliSection


class RLCTLine:
    """A TliFile wrapper that simplifies data entry for metric RLC Options in ohms."""

    def __init__(self, name: str, tli_file: TliFile = None) -> None:
        self.name = name
        if tli_file is None:
            self._tli_file = TliFile()
            self._tli_file.sections = [
                TliSection("Line Summary"),
                TliSection("Line Constants Ground Data"),
                TliSection("RLC Options"),
            ]
            self._tli_file.sections[0].dictionary = {
                "Line Length": 15.0,
                "Steady State Frequency": 50.0,
            }
            self._tli_file.sections[1].dictionary = {
                "GroundResistivity": 100.0,
            }
            self._tli_file.sections[2].dictionary = {
                "Data Entry Format": 0,
                "Positive Sequence Series Resistance": 0.0297,
                "Positive Sequence Series Ind Reactance": 0.2559,
                "Positive Sequence Series Cap Reactance": 0.227,
                "Zero Sequence Series Resistance": 0.0891,
                "Zero Sequence Series Ind Reactance": 0.8957,
                "Zero Sequence Series Cap Reactance": 0.23,
                "Number of Phases": 3,
                "Transposed": 0,
                "Mutual Resistance": 0.162,
                "Mutual Reactance": 0.781,
            }
        else:
            self._tli_file = tli_file

    @classmethod
    def from_file(cls, file_path: str) -> "RLCTLine":
        """
        Creates an RLCTline from a file. Raises ValueError if the file contains the wrong data.

        :param file_path: The path to the file.
        :type file_path: str
        :return: The RLCTline created from the file.
        :rtype: RLCTline
        """
        tli_file = TliFile()
        tli_file.read_file(file_path)

        rlc_index = -1
        for i, section in enumerate(tli_file.sections):
            if section.title_key == "RLC Options":
                rlc_index = i

        if rlc_index < 0:
            raise ValueError(
                "The read .tli file does not contain an 'RLC Options' section."
            )

        if tli_file.sections[rlc_index].get("Data Entry Format") != "0":
            raise ValueError("The read .tli file does not use the 'ohms' input format.")

        file_name = os.path.basename(file_path)
        name = os.path.splitext(file_name)[0]
        return RLCTLine(name, tli_file)

    def write_file(self, directory: str) -> bool:
        """
        Writes the .tli file to the directory. Uses the object's name as file name.

        :param directory: The directory to write the .tli file to.
        :type directory: str
        :return: True if the file was written, False otherwise.
        :rtype: bool
        """
        return self._tli_file.write_file(os.path.join(directory, f"{self.name}.tli"))

    @property
    def length(self) -> float:
        """Line Length

        :return: Line Length in km
        :rtype: float
        """
        return float(self._tli_file.get("Line Summary/Line Length"))

    @length.setter
    def length(self, value: float):
        self._tli_file.sections[0].dictionary["Line Length"] = value

    @property
    def frequency(self) -> float:
        """Steady State Frequency

        :return: Steady State Frequency in Hz
        :rtype: float
        """
        return float(self._tli_file.get("Line Summary/Steady State Frequency"))

    @frequency.setter
    def frequency(self, value: float):
        self._tli_file.sections[0].dictionary["Steady State Frequency"] = value

    @property
    def ground_resistivity(self) -> float:
        """Ground Resistivity

        :return: Ground Resistivity in Ohm*m
        :rtype: float
        """
        return float(self._tli_file.get("Line Constants Ground Data/GroundResistivity"))

    @ground_resistivity.setter
    def ground_resistivity(self, value: float):
        self._tli_file.sections[1].dictionary["GroundResistivity"] = value

    @property
    def r1(self) -> float:
        """Positive Sequence Series Resistance

        :return: Positive Sequence Series Resistance in Ohm/km
        :rtype: float
        """
        return float(
            self._tli_file.get("RLC Options/Positive Sequence Series Resistance")
        )

    @r1.setter
    def r1(self, value: float):
        self._tli_file.sections[2].dictionary[
            "Positive Sequence Series Resistance"
        ] = value

    @property
    def r0(self) -> float:
        """Zero Sequence Series Resistance

        :return: Zero Sequence Series Resistance in Ohm/km
        :rtype: float
        """
        return float(self._tli_file.get("RLC Options/Zero Sequence Series Resistance"))

    @r0.setter
    def r0(self, value: float):
        self._tli_file.sections[2].dictionary["Zero Sequence Series Resistance"] = value

    @property
    def xind1(self) -> float:
        """Positive Sequence Series Ind Reactance

        :return: Positive Sequence Series Ind Reactance in Ohm/km
        :rtype: float
        """
        return float(
            self._tli_file.get("RLC Options/Positive Sequence Series Ind Reactance")
        )

    @xind1.setter
    def xind1(self, value: float):
        self._tli_file.sections[2].dictionary[
            "Positive Sequence Series Ind Reactance"
        ] = value

    @property
    def xind0(self) -> float:
        """Zero Sequence Series Ind Reactance

        :return: Zero Sequence Series Ind Reactance in Ohm/km
        :rtype: float
        """
        return float(
            self._tli_file.get("RLC Options/Zero Sequence Series Ind Reactance")
        )

    @xind0.setter
    def xind0(self, value: float):
        self._tli_file.sections[2].dictionary[
            "Zero Sequence Series Ind Reactance"
        ] = value

    @property
    def xcap1(self) -> float:
        """Positive Sequence Series Cap Reactance

        :return: Positive Sequence Series Cap Reactance in MOhm*km
        :rtype: float
        """
        return float(
            self._tli_file.get("RLC Options/Positive Sequence Series Cap Reactance")
        )

    @xcap1.setter
    def xcap1(self, value: float):
        self._tli_file.sections[2].dictionary[
            "Positive Sequence Series Cap Reactance"
        ] = value

    @property
    def xcap0(self) -> float:
        """Zero Sequence Series Cap Reactance

        :return: Zero Sequence Series Cap Reactance in MOhm*km
        :rtype: float
        """
        return float(
            self._tli_file.get("RLC Options/Zero Sequence Series Cap Reactance")
        )

    @xcap0.setter
    def xcap0(self, value: float):
        self._tli_file.sections[2].dictionary[
            "Zero Sequence Series Cap Reactance"
        ] = value

    @property
    def num_phases(self) -> int:
        """Number of Phases

        :return: Number of Phases
        :rtype: int
        """
        return int(self._tli_file.get("RLC Options/Number of Phases"))

    @num_phases.setter
    def num_phases(self, value: int):
        if value not in (1, 3, 6):
            raise ValueError("Only 1, 3 or 6 phases allowed")
        self._tli_file.sections[2].dictionary["Number of Phases"] = value

    @property
    def transposed(self) -> bool:
        """Ideally Transposed

        :return: True if lines are ideally transposed
        :rtype: bool
        """
        return int(self._tli_file.get("RLC Options/Transposed")) == 1

    @transposed.setter
    def transposed(self, value: bool):
        self._tli_file.sections[2].dictionary["Transposed"] = 1 if value else 0

    @property
    def mutual_resistance(self) -> float:
        """Mutual Resistance

        :return: Mutual Resistance in Ohm/km
        :rtype: float
        """
        return float(self._tli_file.get("RLC Options/Mutual Resistance"))

    @mutual_resistance.setter
    def mutual_resistance(self, value: float):
        self._tli_file.sections[2].dictionary["Mutual Resistance"] = value

    @property
    def mutual_reactance(self) -> float:
        """Mutual Resistance

        :return: Mutual Reactance in Ohm/km
        :rtype: float
        """
        return float(self._tli_file.get("RLC Options/Mutual Reactance"))

    @mutual_reactance.setter
    def mutual_reactance(self, value: float):
        self._tli_file.sections[2].dictionary["Mutual Reactance"] = value
