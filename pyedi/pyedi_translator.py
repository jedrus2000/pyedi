import os
import copy
from gettext import gettext as _
from pyedi.botslib import (
    abspathdata,
    query,
    log_session,
    BotsError,
    BotsImportError,
    FileTooLargeError,
    GotoException,
    TranslationNotFoundError,
    botsimport,
    OldTransaction,
    config,
    logger,
    runscript,
    unique,
    txtexc,
)
from pyedi.botslib.consts import *
import pyedi.inmessage as inmessage
import pyedi.outmessage as outmessage

@log_session
def translate(startstatus, endstatus, routedict, rootidta):
    """ query edifiles to be translated.
        status: FILEIN--PARSED-<SPLITUP--TRANSLATED
    """
    try:  # see if there is a userscript that can determine the translation
        userscript, scriptname = botsimport("mappings", "translation")
    except BotsImportError:  # userscript is not there; other errors like syntax errors are not catched
        userscript = scriptname = None
    # select edifiles to translate
    for rawrow in query(
        """SELECT idta,frompartner,topartner,filename,messagetype,testindicator,editype,charset,alt,fromchannel,filesize,frommail,tomail
                                FROM ta
                                WHERE idta>%(rootidta)s
                                AND status=%(status)s
                                AND statust=%(statust)s
                                AND idroute=%(idroute)s """,
        {
            "status": startstatus,
            "statust": OK,
            "idroute": routedict["idroute"],
            "rootidta": rootidta,
        },
    ):
        row = dict(rawrow)  # convert to real dictionary
        _translate_one_file(row, routedict, endstatus, userscript, scriptname)


def _translate_one_file(row, routedict, endstatus, userscript, scriptname):
    """ -   read, lex, parse, make tree of nodes.
        -   split up files into messages (using 'nextmessage' of grammar)
        -   get mappingscript, start mappingscript.
        -   write the results of translation (no enveloping yet)
    """
    try:
        ta_fromfile = OldTransaction(row["idta"])
        ta_parsed = ta_fromfile.copyta(status=PARSED)
        if row["filesize"] > config.get(["settings", "maxfilesizeincoming"]):
            ta_parsed.update(filesize=row["filesize"])
            raise FileTooLargeError(
                _(
                    'File size of %(filesize)s is too big; option "maxfilesizeincoming" in bots.ini is %(maxfilesizeincoming)s.'
                ),
                {
                    "filesize": row["filesize"],
                    "maxfilesizeincoming": config.get(
                        ["settings", "maxfilesizeincoming"]
                    ),
                },
            )
        logger.debug(
            _(
                'Start translating file "%(filename)s" editype "%(editype)s" messagetype "%(messagetype)s".'
            ),
            row,
        )
        # read whole edi-file: read, parse and made into a inmessage-object.
        # Message is represented as a tree (inmessage.root is the root of the
        # tree).
        edifile = inmessage.parse_edi_file(
            frompartner=row["frompartner"],
            topartner=row["topartner"],
            filename=row["filename"],
            messagetype=row["messagetype"],
            testindicator=row["testindicator"],
            editype=row["editype"],
            charset=row["charset"],
            alt=row["alt"],
            fromchannel=row["fromchannel"],
            frommail=row["frommail"],
            tomail=row["tomail"],
            idroute=routedict["idroute"],
            command=routedict["command"],
        )
        edifile.checkforerrorlist()  # no exception if infile has been lexed and parsed OK else raises an error

        # parse & passthrough; file is parsed, partners are known, no mapping, does confirm.
        if int(routedict["translateind"]) == 3:
            # partners should be queried from ISA level!
            raise GotoException("dummy")
        # edifile.ta_info contains info: QUERIES, charset etc
        for (
            inn_splitup
        ) in (
            edifile.nextmessage()
        ):  # for each message in parsed edifile (one message might get translation multiple times via 'alt'
            try:
                ta_splitup = ta_parsed.copyta(
                    status=SPLITUP, **inn_splitup.ta_info
                )  # copy db-ta from PARSED
                # inn_splitup.ta_info contains parameters from inmessage.parse_edi_file():
                # syntax-information, parse-information
                # for confirmations in userscript; the idta of incoming file
                inn_splitup.ta_info["idta_fromfile"] = ta_fromfile.idta
                # for confirmations in userscript; the idta of 'confirming message'
                inn_splitup.ta_info["idta"] = ta_splitup.idta
                number_of_loops_with_same_alt = 0
                while (
                    True
                ):  # more than one translation can be done via 'alt'; there is an explicit brreak if no more translation need to be done.
                    # find/lookup the translation************************
                    tscript, toeditype, tomessagetype = inmessage.lookup_translation(
                        fromeditype=inn_splitup.ta_info["editype"],
                        frommessagetype=inn_splitup.ta_info["messagetype"],
                        frompartner=inn_splitup.ta_info["frompartner"],
                        topartner=inn_splitup.ta_info["topartner"],
                        alt=inn_splitup.ta_info["alt"],
                    )
                    if (
                        not tscript
                    ):  # no translation found in translate table; check if can find translation via user script
                        if userscript and hasattr(userscript, "gettranslation"):
                            tscript, toeditype, tomessagetype = runscript(
                                userscript,
                                scriptname,
                                "gettranslation",
                                idroute=routedict["idroute"],
                                message=inn_splitup,
                            )
                        if not tscript:
                            raise TranslationNotFoundError(
                                _(
                                    'Translation not found for editype "%(editype)s", messagetype "%(messagetype)s", frompartner "%(frompartner)s", topartner "%(topartner)s", alt "%(alt)s".'
                                ),
                                inn_splitup.ta_info,
                            )

                    # store name of mapping script for reporting (used for display in GUI).
                    inn_splitup.ta_info["divtext"] = tscript
                    # initialize new out-object*************************
                    # make ta for translated message (new out-ta); explicitly erase mail-addresses
                    ta_translated = ta_splitup.copyta(
                        status=endstatus, frommail="", tomail="", cc=""
                    )
                    filename_translated = str(ta_translated.idta)
                    out_translated = outmessage.outmessage_init(
                        editype=toeditype,
                        messagetype=tomessagetype,
                        filename=filename_translated,
                        reference=unique("messagecounter"),
                        statust=OK,
                        divtext=tscript,
                    )  # make outmessage object

                    # run mapping script************************
                    logger.debug(
                        _(
                            'Mappingscript "%(tscript)s" translates messagetype "%(messagetype)s" to messagetype "%(tomessagetype)s".'
                        ),
                        {
                            "tscript": tscript,
                            "messagetype": inn_splitup.ta_info["messagetype"],
                            "tomessagetype": out_translated.ta_info["messagetype"],
                        },
                    )
                    translationscript, scriptfilename = botsimport(
                        "mappings", inn_splitup.ta_info["editype"], tscript
                    )  # get the mappingscript
                    alt_from_previous_run = inn_splitup.ta_info[
                        "alt"
                    ]  # needed to check for infinite loop
                    doalttranslation = runscript(
                        translationscript,
                        scriptfilename,
                        "main",
                        inn=inn_splitup,
                        out=out_translated,
                    )
                    logger.debug(
                        _('Mappingscript "%(tscript)s" finished.'), {"tscript": tscript}
                    )

                    # ~ if 'topartner' not in out_translated.ta_info:    #out_translated does not contain values from ta......#20140516: disable this. suspected since long it does not acutally do soemthing. tested this.
                    # ~ out_translated.ta_info['topartner'] = inn_splitup.ta_info['topartner']
                    # manipulate botskey after mapping script:
                    if "botskey" in inn_splitup.ta_info:
                        inn_splitup.ta_info["reference"] = inn_splitup.ta_info[
                            "botskey"
                        ]
                    if "botskey" in out_translated.ta_info:
                        out_translated.ta_info["reference"] = out_translated.ta_info[
                            "botskey"
                        ]

                    # check the value received from the mappingscript to determine what to do
                    # in this while-loop. Handling of chained trasnlations.
                    if doalttranslation is None:
                        # translation(s) are done; handle out-message
                        handle_out_message(out_translated, ta_translated)
                        break  # break out of while loop
                    elif isinstance(doalttranslation, dict):
                        # some extended cases; a dict is returned that contains 'instructions' for
                        # some type of chained translations
                        if (
                            "type" not in doalttranslation
                            or "alt" not in doalttranslation
                        ):
                            raise BotsError(
                                _(
                                    'Mappingscript returned "%(alt)s". This dict should not have "type" and "alt.'
                                ),
                                {"alt": doalttranslation},
                            )
                        if alt_from_previous_run == doalttranslation["alt"]:
                            number_of_loops_with_same_alt += 1
                        else:
                            number_of_loops_with_same_alt = 0
                        if doalttranslation["type"] == "out_as_inn":
                            # do chained translation: use the out-object as inn-object, new out-object
                            # use case: detected error in incoming file; use out-object to generate warning email
                            copy_out_message = copy.deepcopy(out_translated)
                            handle_out_message(copy_out_message, ta_translated)
                            inn_splitup = out_translated  # out-object is now inn-object
                            # get the alt-value for the next chained translation
                            inn_splitup.ta_info["alt"] = doalttranslation["alt"]
                            if not "frompartner" in inn_splitup.ta_info:
                                inn_splitup.ta_info["frompartner"] = ""
                            if not "topartner" in inn_splitup.ta_info:
                                inn_splitup.ta_info["topartner"] = ""
                            inn_splitup.ta_info.pop("statust")
                        elif doalttranslation["type"] == "no_check_on_infinite_loop":
                            # do chained translation: allow many loops wit hsame alt-value.
                            # mapping script will have to handle this correctly.
                            number_of_loops_with_same_alt = 0
                            handle_out_message(out_translated, ta_translated)
                            # get the alt-value for the next chained translation
                            inn_splitup.ta_info["alt"] = doalttranslation["alt"]
                        else:  # there is nothing else
                            raise BotsError(
                                _(
                                    'Mappingscript returned dict with an unknown "type": "%(doalttranslation)s".'
                                ),
                                {"doalttranslation": doalttranslation},
                            )
                    else:  # note: this includes alt '' (empty string)
                        if alt_from_previous_run == doalttranslation:
                            number_of_loops_with_same_alt += 1
                        else:
                            number_of_loops_with_same_alt = 0
                        # do normal chained translation: same inn-object, new out-object
                        handle_out_message(out_translated, ta_translated)
                        # get the alt-value for the next chained translation
                        inn_splitup.ta_info["alt"] = doalttranslation
                    if number_of_loops_with_same_alt > 10:
                        raise BotsError(
                            _(
                                'Mappingscript returns same alt value over and over again (infinite loop?). Alt: "%(doalttranslation)s".'
                            ),
                            {"doalttranslation": doalttranslation},
                        )
                # end of while-loop **********************************************************************************
            # exceptions file_out-level: exception in mappingscript or writing of out-file
            except:
                # two ways to handle errors in mapping script or in writing outgoing message:
                # 1. do process other messages in file/interchange (default in bots 3.*)
                # 2. one error in file/interchange->drop all results (as in bots 2.*)
                if inn_splitup.ta_info.get(
                    "no_results_if_any_error_in_translation_edifile", False
                ):
                    raise
                txt = txtexc()
                # update db. inn_splitup.ta_info could be changed by mappingscript. Is this useful?
                ta_splitup.update(statust=ERROR, errortext=txt, **inn_splitup.ta_info)
                ta_splitup.deletechildren()
            else:
                # update db. inn_splitup.ta_info could be changed by mappingscript. Is this useful?
                ta_splitup.update(statust=DONE, **inn_splitup.ta_info)

    # exceptions file_in-level
    except GotoException:  # edi-file is OK, file is passed-through after parsing.
        ta_parsed.update(
            statust=DONE, filesize=row["filesize"], **edifile.ta_info
        )  # update with info from eg queries
        ta_parsed.copyta(
            status=MERGED, statust=OK
        )  # original file goes straight to MERGED
        edifile.handleconfirm(ta_fromfile, routedict, error=False)
        logger.debug(
            _('Parse & passthrough for input file "%(filename)s".'), row
        )
    except FileTooLargeError as msg:
        ta_parsed.update(statust=ERROR, errortext=str(msg))
        ta_parsed.deletechildren()
        logger.debug(
            'Error in translating input file "%(filename)s":\n%(msg)s',
            {"filename": row["filename"], "msg": msg},
        )
    except:
        txt = txtexc()
        ta_parsed.update(statust=ERROR, errortext=txt, **edifile.ta_info)
        ta_parsed.deletechildren()
        edifile.handleconfirm(ta_fromfile, routedict, error=True)
        logger.debug(
            'Error in translating input file "%(filename)s":\n%(msg)s',
            {"filename": row["filename"], "msg": txt},
        )
    else:
        edifile.handleconfirm(ta_fromfile, routedict, error=False)
        ta_parsed.update(statust=DONE, filesize=row["filesize"], **edifile.ta_info)
        logger.debug(_('Translated input file "%(filename)s".'), row)
    finally:
        ta_fromfile.update(statust=DONE)


def handle_out_message(out_translated, ta_translated):
    if (
        out_translated.ta_info["statust"] == DONE
    ):  # if indicated in mappingscript the message should be discarded
        logger.debug(
            _("No output file because mappingscript explicitly indicated this.")
        )
        out_translated.ta_info["filename"] = ""
        out_translated.ta_info["status"] = DISCARD
    else:
        logger.debug(
            _(
                'Start writing output file editype "%(editype)s" messagetype "%(messagetype)s".'
            ),
            out_translated.ta_info,
        )
        out_translated.writeall()  # write result of translation.
        out_translated.ta_info["filesize"] = os.path.getsize(
            abspathdata(out_translated.ta_info["filename"])
        )  # get filesize
    ta_translated.update(
        **out_translated.ta_info
    )  # update outmessage transaction with ta_info; statust = OK
