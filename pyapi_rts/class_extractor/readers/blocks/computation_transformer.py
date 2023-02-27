# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from lark import Token, Transformer, Tree

ONE_ARG_FUNCTIONS = {}


class ComputationTransformer(Transformer):
    """
    Transformer for the computation Lark grammar.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.computation = None

    def start(self, children):
        """
        Transforms the root of the tree.
        """
        self.computation = children[0]
        return self.computation

    def line(self, children) -> tuple[str, type, str]:
        """
        Transforms the line to Pyhton code.
        """
        if len(children) == 1:
            return None

        if len(children) == 2:
            _type = "int"
            variable_name = children[0].value
            return (variable_name, _type, str(children[1]).strip())

        variable_name = children[1].value
        _type = {"INTEGER": "int", "STRING": "str", "REAL": "float"}[children[0].value]
        return (variable_name, _type, str(children[2]).strip())

    def variable(self, args):
        """
        Transforms a variable.
        """
        # TODO: Handle @ and . notation
        if len(args) == 1:
            return "$" + args[0].value
        else:
            return "€" + args[1].value  # $ at start, this is an internal variable

    def statement(self, children):
        """
        Transforms a statement.
        """
        if len(children) == 0:
            return ""
        if isinstance(children[0], str):
            return children[0]
        if isinstance(children[0], int) or isinstance(children[0], float):
            return children[0]
        if isinstance(children[0], Tree):
            if isinstance(children[0].children[0], Token):
                return children[0].children[0].value
            else:
                return children[0].children[0]
        else:
            return children[0].value

    def addition(self, children):
        """
        Transforms an addition.
        """
        return " + ".join(list(map((lambda x: str(x)), children)))

    def subtraction(self, children):
        """
        Transforms a subtraction.
        """
        return " - ".join(list(map((lambda x: str(x)), children)))

    def multiplication(self, children):
        """
        Transforms a multiplication.
        """
        return " * ".join(list(map((lambda x: str(x)), children)))

    def division(self, children):
        """
        Transforms a division.
        """
        return " / ".join(list(map((lambda x: str(x)), children)))

    def sqrt(self, children):
        """
        Transforms a square root.
        """
        return f"sqrt({children[0]})"

    def sin(self, children):
        """
        Transforms a sine.
        """
        return f"sin({children[0]})"

    def cos(self, children):
        """
        Transforms a cosine.
        """
        return f"cos({children[0]})"

    def tan(self, children):
        """
        Transforms a tangent.
        """
        return f"tan({children[0]})"

    def condition(self, children):
        """
        Transforms a condition.
        """
        condition = children[0]
        if_res = children[1]
        else_res = children[2]
        return f"{if_res} if {condition} else {else_res}"

    def boolean_var(self, children):
        """
        Transforms a boolean variable.
        """
        if len(children) == 1:
            return children[0]
        else:
            return "(0 if " + children[1] + " else 1)"  # "!" operator applied

    def boolean_exp(self, childern):
        """
        Transforms a boolean expression.
        """
        if len(childern) == 1:
            return childern[0]
        elif len(childern) == 0:
            return "True"

        operator_dict = {
            "=": "==",
            "!=": "!=",
            "==": "==",
            ">": ">",
            "<": "<",
            ">=": ">=",
            "<=": "<=",
            "||": "or",
            "&": "and",
            "|": "or",
            "&&": "and",
        }

        left = childern[0]
        operator = (
            operator_dict[childern[1].value]
            if childern[1].value in operator_dict
            else childern[1].value
        )
        right = childern[2]
        return f"({left} {operator} {right})"

    def number(self, children):
        """
        Transforms a number.
        """
        if "0x" in children[0].value:
            return float(int(children[0].value, 16))
        return float(children[0].value)

    def statement_br(self, children):
        """
        Transforms a statement in brackets.
        """
        if len(children) == 1:
            return children[0]
        else:
            return "(" + children[1] + ")"

    def concat(self, childeren):
        """
        Transforms a concat operation.
        """
        return " + ".join(
            map(
                (
                    lambda x: str(x)
                    if ("$" in str(x) or '"' in str(x) or isinstance(x, float))
                    else "$" + str(x)
                ),
                childeren,
            )
        )

    def shift(self, children):
        """
        Transforms a left / right shift.
        """
        return f"(int)({children[0]}) {children[1].value} (int)({children[2]})"

    def string(self, children):
        """
        Transforms a string.
        """
        if len(children) >= 1:
            if children[0].value.count('"') == 2:
                return children[0].value
            return '"' + children[0].value + '"'
        return ""

    def internal_function(self, children):
        """
        Transforms an internal function.
        """
        # TODO: Issue #25
        return 1.0

    def hex_to_int(self, children):
        """
        Transforms a hexadecimal number to an integer.
        """
        return f"int({children[0]}, 16)"

    def pick_wye_delta(self, children):
        """
        Transforms a pick wye-delta.
        """
        return 1.0  # TODO: Figure out what this does

    def lead_lag(self, children):
        """
        Transforms a lead-lag.
        """
        return 1.0  # TODO: Figure out what this does

    def p_q_calc(self, children):
        """
        Transforms a p-q-calc.
        """
        return 1.0  # TODO: Figure out what this does

    def p_q_calc_i(self, children):
        """
        Transforms a p-q-i-calc.
        """
        return 1.0  # TODO: Figure out what this does

    def filt_data(self, children):
        """
        Transforms a filter data.
        """
        return children[0]  # TODO: Figure out what this does

    def calc_l(self, children):
        """
        Transforms a calc l.
        """
        return 1.0  # TODO: Figure out what this does

    def pick_model(self, children):
        """
        Transforms a pick_model function.
        """
        return 1.0  # TODO: Figure out what this does

    def function_args(self, children):
        """
        Transforms a function with one argument.
        """
        if not children[0] in ONE_ARG_FUNCTIONS.keys():
            print(f"{children[0]}: {len(children) - 1}")
        ONE_ARG_FUNCTIONS[children[0]] = 1
        return 1.0

    def pow(self, children):
        """
        Transforms a power.
        """
        return f"({children[0]}**{children[1]})"

    def strlen(self, children):
        """
        Transforms a string length.
        """
        return f"len({children[0]})"

    def calc_nm_cond(self, children):
        """
        Transforms a number calculation
        """
        if len(children) == 1 and isinstance(children[0], int):
            if children[0] % 3 == 0:
                return children[0] // 3
            else:
                return children[0]
        return 1.0  # TODO: Find actual behaviour

    def fixedimpedance(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def types_lf(self, children):
        """
        Transforms a types_lf.
        """
        return 1.0

    def requiv(self, children):
        """
        Transforms a requiv.
        """
        return 1.0

    def xequiv(self, children):
        """
        Transforms a xequiv.
        """
        return 1.0

    def pickmodel(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def acos(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def rnet_calc_pi_yz(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def rcal(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def loadf(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def lcal(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def bcal(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def llcomp(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def pickvwgd(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def picknode(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def pickval(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def pcalci(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def pickv(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def pickval2(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def qcalci(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0

    def groupname(self, children):
        """
        Transforms a fixed impedance.
        """
        return 1.0
