from .fixed import Fixed


class Idoc(Fixed):
    """ class for idoc ediobjects.
        for incoming the same as fixed.
        SAP does strip all empty fields for record; is catered for in grammar.defaultsyntax
    """
    pass
