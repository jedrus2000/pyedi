from .grammar import Grammar


class Test(Grammar):
    """ For unit tests """

    defaultsyntax = {
        "has_structure": True,  # is True, read structure, recorddef, check these
        "checkcollision": True,
        "noBOTSID": False,
    }