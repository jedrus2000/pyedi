"""
This is modified code of Bots project:
    http://bots.sourceforge.net/en/index.shtml
    ttp://bots.readthedocs.io
    https://github.com/eppye-bots/bots

originally created by Henk-Jan Ebbers.

This code include also changes from other forks, specially from:
    https://github.com/bots-edi

This project, as original Bots is licenced under GNU GENERAL PUBLIC LICENSE Version 3; for full
text: http://www.gnu.org/copyleft/gpl.html
"""
from .database import (query, changeq)
from .consts import *

confirmrules = []       #confirmrules are read into memory at start of run

def prepare_confirmrules():
    """ as confirmrules are often used, read these into memory. Reason: performance.
        additional notes:
        - there are only a few confirmrules (10 would be a lot I guess).
        - indexing is not helpfull for confirmrules, this means that each time the whole confirmrule-tabel is scanned.
        - as confirmrules are used for incoming and outgoing (x12, edifact, email) this will almost always lead to better performance.
    """
    for confirmdict in query(
        """SELECT confirmtype,
                  ruletype,
                  idroute,
                  idchannel_id as idchannel,
                  frompartner_id as frompartner,
                  topartner_id as topartner,
                  messagetype,
                  negativerule
                        FROM confirmrule
                        WHERE active=%(active)s
                        ORDER BY negativerule ASC
                        """,
        {"active": True},
    ):
        confirmrules.append(dict(confirmdict))


def set_asked_confirmrules(routedict, rootidta):
    """ set 'ask confirmation/acknowledgements for x12 and edifact
    """
    if not globalcheckconfirmrules("ask-x12-997") and not globalcheckconfirmrules(
        "ask-edifact-CONTRL"
    ):
        return
    for row in query(
        """SELECT parent,editype,messagetype,frompartner,topartner
                                FROM ta
                                WHERE idta>%(rootidta)s
                                AND status=%(status)s
                                AND statust=%(statust)s
                                AND (editype='edifact' OR editype='x12') """,
        {"status": FILEOUT, "statust": TransactionStatus.OK, "rootidta": rootidta},
    ):
        if row[str("editype")] == "x12":
            if row[str("messagetype")][:3] in ["997", "999"]:
                continue
            confirmtype = "ask-x12-997"
        else:
            if row[str("messagetype")][:6] in ["CONTRL", "APERAK"]:
                continue
            confirmtype = "ask-edifact-CONTRL"
        if not checkconfirmrules(
            confirmtype,
            idroute=routedict["idroute"],
            idchannel=routedict["tochannel"],
            topartner=row[str("topartner")],
            frompartner=row[str("frompartner")],
            messagetype=row[str("messagetype")],
        ):
            continue
        changeq(
            """UPDATE ta
                   SET confirmasked=%(confirmasked)s, confirmtype=%(confirmtype)s
                   WHERE idta=%(parent)s """,
            {
                "parent": row[str("parent")],
                "confirmasked": True,
                "confirmtype": confirmtype,
            },
        )


def globalcheckconfirmrules(confirmtype):
    """ global check if confirmrules with this confirmtype is uberhaupt used.
    """
    for confirmdict in confirmrules:
        if confirmdict["confirmtype"] == confirmtype:
            return True
    return False


def checkconfirmrules(confirmtype, **kwargs):
    confirm = False  # boolean to return: confirm of not?
    # confirmrules are evaluated one by one; first the positive rules, than the negative rules.
    # this make it possible to include first, than exclude. Eg: send for 'all', than exclude certain partners.
    for confirmdict in confirmrules:
        if confirmdict["confirmtype"] != confirmtype:
            continue
        if confirmdict["ruletype"] == "all":
            confirm = not confirmdict["negativerule"]
        elif confirmdict["ruletype"] == "route":
            if "idroute" in kwargs and confirmdict["idroute"] == kwargs["idroute"]:
                confirm = not confirmdict["negativerule"]
        elif confirmdict["ruletype"] == "channel":
            if (
                "idchannel" in kwargs
                and confirmdict["idchannel"] == kwargs["idchannel"]
            ):
                confirm = not confirmdict["negativerule"]
        elif confirmdict["ruletype"] == "frompartner":
            if (
                "frompartner" in kwargs
                and confirmdict["frompartner"] == kwargs["frompartner"]
            ):
                confirm = not confirmdict["negativerule"]
        elif confirmdict["ruletype"] == "topartner":
            if (
                "topartner" in kwargs
                and confirmdict["topartner"] == kwargs["topartner"]
            ):
                confirm = not confirmdict["negativerule"]
        elif confirmdict["ruletype"] == "messagetype":
            if (
                "messagetype" in kwargs
                and confirmdict["messagetype"] == kwargs["messagetype"]
            ):
                confirm = not confirmdict["negativerule"]
    return confirm
