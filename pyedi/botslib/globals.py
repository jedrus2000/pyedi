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