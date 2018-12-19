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
# **********************************************************/**
# **************getters/setters for some globals***********************/**
# **********************************************************/**

routeid = ''            #current route. This is used to set routeid for Processes.

def setrouteid(_routeid):
    global routeid
    routeid = _routeid


def getrouteid():
    global routeid
    return routeid