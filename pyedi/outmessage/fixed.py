import decimal

NODECIMAL = decimal.Decimal(1)

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI


from pyedi.botslib.consts import *

from .outmessage import OutMessage


class Fixed(OutMessage):
    def _initfield(self, field_definition):
        if field_definition[BFORMAT] == "A":
            if (
                    field_definition[FORMAT] == "AR"
            ):  # if field format is alfanumeric right aligned
                value = "".rjust(field_definition[MINLENGTH])
            else:
                value = "".ljust(
                    field_definition[MINLENGTH]
                )  # add spaces (left, because A-field is right aligned)
        elif field_definition[BFORMAT] == "D":
            value = "".ljust(field_definition[MINLENGTH])  # add spaces
        elif field_definition[BFORMAT] == "T":
            value = "".ljust(field_definition[MINLENGTH])  # add spaces
        else:  # numerics
            if (
                    field_definition[BFORMAT] == "R"
            ):  # floating point: use all decimals received
                if (
                        field_definition[FORMAT] == "RL"
                ):  # if field format is numeric right aligned
                    value = "0".ljust(field_definition[MINLENGTH])
                elif (
                        field_definition[FORMAT] == "RR"
                ):  # if field format is numeric right aligned
                    value = "0".rjust(field_definition[MINLENGTH])
                else:
                    value = "0".zfill(field_definition[MINLENGTH])
            elif field_definition[BFORMAT] == "N":  # fixed decimals; round
                value = str(
                    decimal.Decimal("0").quantize(
                        decimal.Decimal(10) ** -field_definition[DECIMALS]
                    )
                )
                if (
                        field_definition[FORMAT] == "NL"
                ):  # if field format is numeric right aligned
                    value = value.ljust(field_definition[MINLENGTH])
                elif (
                        field_definition[FORMAT] == "NR"
                ):  # if field format is numeric right aligned
                    value = value.rjust(field_definition[MINLENGTH])
                else:
                    value = value.zfill(field_definition[MINLENGTH])
                value = value.replace(
                    ".", self.ta_info["decimaal"], 1
                )  # replace '.' by required decimal sep.
            elif field_definition[BFORMAT] == "I":  # implicit decimals
                dec_value = decimal.Decimal("0") * 10 ** field_definition[DECIMALS]
                value = str(dec_value.quantize(NODECIMAL))
                value = value.zfill(field_definition[MINLENGTH])
        return value
