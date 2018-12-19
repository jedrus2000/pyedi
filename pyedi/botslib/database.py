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
from random import randrange

from .logger import logger

# **********************************************************/**
# *************************Database***********************/**
# **********************************************************/**
def addinfocore(change, where, wherestring):
    """ core function for add/changes information in db-ta's.

    wherestring = " WHERE idta > %(rootidta)s AND " + wherestring
    counter = 0  # count the number of dbta changed
    for row in query("SELECT idta FROM ta "+ wherestring, where):
        counter += 1
        ta_from = OldTransaction(row[str("idta")])
        ta_from.copyta(
            **change
        )  # make new ta from ta_from, using parameters from change
        ta_from.update(statust=TransactionStatus.DONE)  # update 'old' ta
    return counter
    """
    raise NotImplemented


def addinfo(change, where):
    """ change ta's to new phase: ta's are copied to new ta.
        returns the number of db-ta that have been changed.
        change (dict): values to change.
        where (dict): selection.

    if "rootidta" not in where:
        where["rootidta"] = botsglobal.currentrun.get_minta4query()
    if "statust" not in where:  # by default: look only for statust is TransactionStatus.OK
        where["statust"] = TransactionStatus.OK
    if "statust" not in change:  # by default: new ta is TransactionStatus.OK
        change["statust"] = TransactionStatus.OK
    wherestring = " AND ".join(
        key + "=%(" + key + ")s " for key in where if key != "rootidta"
    )  # wherestring; does not use rootidta
    return addinfocore(change=change, where=where, wherestring=wherestring)
    """
    raise NotImplemented

def updateinfocore(change, where, wherestring=""):
    """ update info in ta's.
        where (dict) selects ta's,
        change (dict) sets values;

    wherestring = " WHERE idta > %(rootidta)s AND " + wherestring
    # change-dict: discard empty values. Change keys: this is needed because same keys can be in where-dict
    change2 = [(key, value) for key, value in change.items() if value]
    if not change2:
        return
    changestring = ",".join(key + "=%(change_" + key + ")s" for key, value in change2)
    where.update(("change_" + key, value) for key, value in change2)
    return changeq("UPDATE ta SET " + changestring + wherestring, where)
    """
    raise NotImplemented


def updateinfo(change, where):
    """ update ta's.
        returns the number of db-ta that have been changed.
        change (dict): values to change.
        where (dict): selection.

    if "rootidta" not in where:
        where["rootidta"] = botsglobal.currentrun.get_minta4query()
    if "statust" not in where:  # by default: look only for statust is TransactionStatus.OK
        where["statust"] = TransactionStatus.OK
    if "statust" not in change:  # by default: new ta is TransactionStatus.OK
        change["statust"] = TransactionStatus.OK
    wherestring = " AND ".join(
        key + "=%(" + key + ")s " for key in where if key != "rootidta"
    )  # wherestring for copy & done
    return updateinfocore(change=change, where=where, wherestring=wherestring)
    """
    raise NotImplemented


def changestatustinfo(change, where):
    """
    return updateinfo({"statust": change}, where)
    """
    raise NotImplemented

def query(querystring, *args):
    """ general query. yields rows from query
    cursor = botsglobal.db.cursor()
    cursor.execute(querystring, *args)
    results = cursor.fetchall()
    cursor.close()
    for result in results:
        yield result
    """
    raise NotImplemented

def changeq(querystring, *args):
    """general inset/update. no return
    cursor = botsglobal.db.cursor()
    try:
        cursor.execute(querystring, *args)
    except:
        botsglobal.db.rollback()  # rollback is needed for postgreSQL as this is also used by user scripts (eg via persist)
        raise
    botsglobal.db.commit()
    terug = cursor.rowcount
    cursor.close()
    return terug
    """
    # TODO raise NotImplemented
    logger.info(f'changeq: querystring={querystring}, args={args}')

def insertta(querystring, *args):
    """ insert ta
        from insert get back the idta; this is different with postgrSQL.

    cursor = botsglobal.db.cursor()
    cursor.execute(querystring, *args)
    newidta = cursor.lastrowid
    if not newidta:  # if botsglobal.settings.DATABASE_ENGINE ==
        cursor.execute("SELECT lastval() as idta")
        newidta = cursor.fetchone()["idta"]
    botsglobal.db.commit()
    cursor.close()
    return newidta
    """
    # TODO NotImplemented
    random_newidta = randrange(300)
    logger.info(f'insertta: querystring={querystring}, args={args}, random_ret_value={random_newidta}')
    return random_newidta

def unique_runcounter(domain, updatewith=None):
    """ as unique, but per run of bots-engine.

    domain += "bots_1_8_4_9_6"  # avoid using/mixing other values in botsglobal
    if sys.version_info[0] <= 2:
        domain = domain.encode("unicode-escape")
    nummer = getattr(botsglobal, domain, 0)
    if updatewith is None:
        nummer += 1
        updatewith = nummer
        if updatewith > MAXINT:
            updatewith = 0
    setattr(botsglobal, domain, updatewith)
    return nummer
    """
    raise NotImplemented

def unique(domein, updatewith=None):
    """ generate unique number within range domain. Uses db to keep track of last generated number.
        3 use cases:
        - in acceptance: use unique_runcounter
        - if updatewith is not None: return current number, update database with updatewith
        - if updatewith is None: return current number plus 1; update database with  current number plus 1
            if domain not used before, initialize with 1.

    if botsglobal.ini.getboolean("acceptance", "runacceptancetest", False):
        return unique_runcounter(domein)
    else:
        cursor = botsglobal.db.cursor()
        try:
            cursor.execute(
                "SELECT nummer FROM uniek WHERE domein=%(domein)s",
                {"domein": domein},
            )
            nummer = cursor.fetchone()[str("nummer")]
            if updatewith is None:
                nummer += 1
                updatewith = nummer
                if updatewith > MAXINT:
                    updatewith = 0
            cursor.execute(
                "UPDATE uniek SET nummer=%(nummer)s WHERE domein=%(domein)s",
                {"domein": domein, "nummer": updatewith},
            )
        except TypeError:  # if domein does not exist, cursor.fetchone returns None, so TypeError
            cursor.execute(
                "INSERT INTO uniek (domein,nummer) VALUES (%(domein)s,1)",
                {"domein": domein},
            )
            nummer = 1
        botsglobal.db.commit()
        cursor.close()
        return nummer

    """
    # TODO raise NotImplemented
    nummer = 1
    logger.info(f'unique: domein={domein}, updatewith={updatewith}, nummer={nummer}')
    return nummer

def checkunique(domein, receivednumber):
    """ to check if received number is sequential: value is compare with new generated number.
        if domain not used before, initialize it . '1' is the first value expected.

    newnumber = unique(domein)
    if newnumber == receivednumber:
        return True
    else:
        # received number is not TransactionStatus.OK. Reset counter in database to previous value.
        if botsglobal.ini.getboolean("acceptance", "runacceptancetest", False):
            return False  # TODO: set the unique_runcounter
        else:
            changeq(
                "UPDATE uniek SET nummer=%(nummer)s WHERE domein=%(domein)s",
                {"domein": domein, "nummer": newnumber - 1},
            )
            return False
    """
    raise NotImplemented

