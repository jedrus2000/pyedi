from gettext import gettext as _

from pyedi.botslib import GrammarError, BotsImportError

from .jsonnocheck import JsonNoCheck
from .json import Json
from .xmlnocheck import XmlNoCheck
from .xml import Xml
from .tradacoms import Tradacoms
from .x12 import X12
from .csv import Csv
from .edifact import Edifact
from .fixed import Fixed
from .idoc import Idoc
from .templatehtml import TemplateHtml
from .test import Test
from .excel import Excel

grammar_classes = {
    'csv': Csv,
    'edifact': Edifact,
    'excel': Excel,
    'fixed': Fixed,
    'idoc': Idoc,
    'jsonnocheck': JsonNoCheck,
    'json': Json,
    'templatehtml': TemplateHtml,
    'tradacoms': Tradacoms,
    'test': Test,
    'xmlnocheck': XmlNoCheck,
    'xml': Xml,
    'x12': X12
}

def grammarread(editype, grammarname, typeofgrammarfile):
    """ reads/imports a grammar (dispatch function for class Grammar and subclasses).
        typeofgrammarfile indicates some differences in reading/syntax handling:
        - envelope: read whole grammar, get right syntax
        - grammar: read whole grammar, get right syntax.
        - partners: only syntax is read
        grammars are imported from usersys/<'typeofgrammarfile'>/<editype>/<grammarname>.
    """
    try:
        classtocall = grammar_classes.get(editype.lower())
    except KeyError:
        raise GrammarError(
            _(
                'Read grammar for editype "%(editype)s" messagetype "%(messagetype)s", but editype is unknown.'
            ),
            {"editype": editype, "messagetype": grammarname},
        )
    if typeofgrammarfile == "grammars":
        # read grammar for a certain editype/messagetype
        messagegrammar = classtocall(
            typeofgrammarfile="grammars", editype=editype, grammarname=grammarname
        )
        # Get right syntax: 1. start with classtocall.defaultsyntax
        messagegrammar.syntax = classtocall.defaultsyntax.copy()
        # Find out what envelope is used:
        envelope = (
            messagegrammar.original_syntaxfromgrammar.get("envelope")
            or messagegrammar.syntax["envelope"]
        )
        # when reading messagetype 'edifact' envelope will also be edifact->so do not read it.
        if envelope and envelope != grammarname:
            try:
                # read envelope grammar
                envelopegrammar = classtocall(
                    typeofgrammarfile="grammars", editype=editype, grammarname=envelope
                )
                # Get right syntax: 2. update with syntax from envelope
                messagegrammar.syntax.update(envelopegrammar.original_syntaxfromgrammar)
            except BotsImportError:  # not all envelopes have grammar files; eg csvheader, user defined envelope.
                pass
        # Get right syntax: 3. update with syntax of messagetype
        messagegrammar.syntax.update(messagegrammar.original_syntaxfromgrammar)
        messagegrammar._init_restofgrammar()
        return messagegrammar
    elif typeofgrammarfile == "envelope":
        # Read grammar for enveloping (outgoing). For 'noenvelope' no grammar is read.
        # Read grammar for messagetype first -> to find out envelope.
        messagegrammar = classtocall(
            typeofgrammarfile="grammars", editype=editype, grammarname=grammarname
        )
        # Get right syntax: 1. start with default syntax
        syntax = classtocall.defaultsyntax.copy()
        envelope = (
            messagegrammar.original_syntaxfromgrammar.get("envelope")
            or syntax["envelope"]
        )
        try:
            envelopegrammar = classtocall(
                typeofgrammarfile="grammars", editype=editype, grammarname=envelope
            )
            # Get right syntax: 2. update with envelope syntax
            syntax.update(envelopegrammar.original_syntaxfromgrammar)
        except BotsImportError:
            envelopegrammar = messagegrammar
        # Get right syntax: 3. update with message syntax
        syntax.update(messagegrammar.original_syntaxfromgrammar)
        envelopegrammar.syntax = syntax
        envelopegrammar._init_restofgrammar()
        return envelopegrammar
    else:  # typeofgrammarfile == 'partners':
        messagegrammar = classtocall(
            typeofgrammarfile="partners", editype=editype, grammarname=grammarname
        )
        messagegrammar.syntax = messagegrammar.original_syntaxfromgrammar.copy()
        return messagegrammar