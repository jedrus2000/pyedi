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
def updateunlessset(updatedict, fromdict):
    # ~ updatedict.update((key,value) for key, value in fromdict.items() if key not in updatedict) #!!TODO when is this valid? Note: prevents setting charset from gramamr
    updatedict.update(
        (key, value)
        for key, value in fromdict.items()
        if key not in updatedict or not updatedict[key]
    )  # !!TODO when is this valid? Note: prevents setting charset from gramamr


def indent_xml(node, level=0, indentstring="    "):
    text2indent = "\n" + level * indentstring
    if len(node):
        if not node.text or not node.text.strip():
            node.text = text2indent + indentstring
        for subnode in node:
            indent_xml(subnode, level + 1)
            if not subnode.tail or not subnode.tail.strip():
                subnode.tail = text2indent + indentstring
        if not subnode.tail or not subnode.tail.strip():
            subnode.tail = text2indent
    else:
        if level and (not node.tail or not node.tail.strip()):
            node.tail = text2indent
