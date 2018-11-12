# **********************************************************/**
# ***************** class  Transaction *********************/**
# **********************************************************/**
from .logger import logger
from .consts import *

from .database import (
    query,
    changeq,
    insertta
)

from .exceptions import txtexc
from .globals import getrouteid


def log_session(func):
    """ used as decorator.
        The decorated functions are logged as processes.
        Errors in these functions are caught and logged.
    """

    def wrapper(*args, **argv):
        try:
            ta_process = NewProcess(func.__name__)
        except:
            logger.exception("System error - no new process made")
            raise
        try:
            terug = func(*args, **argv)
        except:
            txt = txtexc()
            logger.debug("Error in process: %(txt)s", {"txt": txt})
            ta_process.update(statust=ERROR, errortext=txt)
        else:
            ta_process.update(statust=DONE)
            return terug

    return wrapper


class _Transaction(object):
    """ abstract class for db-ta.
        This class is used for communication with db-ta.
    """

    # filtering values for db handling to avoid unknown fields in db.
    filterlist = (
        "statust",
        "status",
        "divtext",
        "parent",
        "child",
        "script",
        "frompartner",
        "topartner",
        "fromchannel",
        "tochannel",
        "editype",
        "messagetype",
        "merge",
        "testindicator",
        "reference",
        "frommail",
        "tomail",
        "contenttype",
        "errortext",
        "filename",
        "charset",
        "alt",
        "idroute",
        "nrmessages",
        "retransmit",
        "confirmasked",
        "confirmed",
        "confirmtype",
        "confirmidta",
        "envelope",
        "botskey",
        "cc",
        "rsrv1",
        "filesize",
        "numberofresends",
        "rsrv3",
    )
    processlist = [
        0
    ]  # stack for bots-processes. last one is the current process; starts with 1 element in list: root

    def update(self, **ta_info):
        """ Updates db-ta with named-parameters/dict.
            Use a filter to update only valid fields in db-ta
        """
        setstring = ",".join(
            key + "=%(" + key + ")s" for key in ta_info if key in self.filterlist
        )
        if not setstring:  # nothing to update
            return
        ta_info["selfid"] = self.idta
        changeq(
            """UPDATE ta
                    SET """
            + setstring
            + """
                    WHERE idta=%(selfid)s""",
            ta_info,
        )

    def delete(self):
        """Deletes current transaction """
        changeq(
            """DELETE FROM ta
                    WHERE idta=%(idta)s""",
            {"idta": self.idta},
        )

    def deletechildren(self):
        self.deleteonlychildren_core(self.idta)

    def deleteonlychildren_core(self, idta):
        for row in query(
            """SELECT idta
                            FROM ta
                            WHERE parent=%(idta)s""",
            {"idta": idta},
        ):
            self.deleteonlychildren_core(row[str("idta")])
            changeq(
                """DELETE FROM ta
                        WHERE idta=%(idta)s""",
                {"idta": row[str("idta")]},
            )

    def syn(self, *ta_vars):
        """access of attributes of transaction as ta.fromid, ta.filename etc"""
        varsstring = ",".join(ta_vars)
        for row in query(
            """SELECT """
            + varsstring
            + """
                              FROM ta
                              WHERE idta=%(idta)s""",
            {"idta": self.idta},
        ):
            self.__dict__.update(dict(row))

    def synall(self):
        """access of attributes of transaction as ta.fromid, ta.filename etc"""
        self.syn(*self.filterlist)

    def copyta(self, status, **ta_info):
        """ copy old transaction, return new transaction.
            parameters for new transaction are in ta_info (new transaction is updated with these values).
        """
        script = _Transaction.processlist[-1]
        newidta = insertta(
            """INSERT INTO ta (script,  status,parent,frompartner,topartner,fromchannel,tochannel,editype,messagetype,alt,merge,testindicator,reference,frommail,tomail,charset,contenttype,filename,idroute,nrmessages,botskey,envelope,rsrv3,cc)
                                SELECT %(script)s,%(newstatus)s,idta,frompartner,topartner,fromchannel,tochannel,editype,messagetype,alt,merge,testindicator,reference,frommail,tomail,charset,contenttype,filename,idroute,nrmessages,botskey,envelope,rsrv3,cc
                                FROM ta
                                WHERE idta=%(idta)s""",
            {"idta": self.idta, "script": script, "newstatus": status},
        )
        newta = OldTransaction(newidta)
        newta.update(**ta_info)
        return newta


class OldTransaction(_Transaction):
    """ Resurrect old transaction """

    def __init__(self, idta):
        self.idta = idta


class NewTransaction(_Transaction):
    """ Generate new transaction. """

    def __init__(self, **ta_info):
        updatedict = dict(
            (key, value) for key, value in ta_info.items() if key in self.filterlist
        )  # filter ta_info
        updatedict["script"] = self.processlist[-1]
        namesstring = ",".join(key for key in updatedict)
        varsstring = ",".join("%(" + key + ")s" for key in updatedict)
        self.idta = insertta(
            """INSERT INTO ta ("""
            + namesstring
            + """)
                                 VALUES   ("""
            + varsstring
            + """)""",
            updatedict,
        )


class NewProcess(NewTransaction):
    """ Create a new process (which is very much like a transaction).
        Used in logging of processes.
        Each process is placed on stack processlist
    """

    def __init__(self, functionname=""):
        super(NewProcess, self).__init__(
            filename=functionname, status=PROCESS, idroute=getrouteid()
        )
        self.processlist.append(self.idta)

    def update(self, **ta_info):
        """ update process, delete from process-stack. """
        super(NewProcess, self).update(**ta_info)
        self.processlist.pop()
