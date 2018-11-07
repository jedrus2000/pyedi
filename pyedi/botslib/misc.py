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
