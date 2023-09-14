from pyapi_rts.api.component import Component
from pyapi_rts.api.subsystem import Subsystem
from pyapi_rts.generated.HIERARCHY import HIERARCHY
from pyapi_rts.generated.enums.NoyesEnumParameter import NoyesEnum


def is_excluded(component: Component) -> bool:
    """Determine if [component] is excluded from the circuit.

    :param component: The component to check.
    :type component: Component
    :return: True if the component is excluded.
    :rtype: bool
    """
    p = component.parent
    while not isinstance(p, Subsystem) and p is not None:
        if isinstance(p, HIERARCHY):
            if p.BoxParameters.EXCLUDE.value == NoyesEnum.YES:
                return True
        p = p.parent
    return False
