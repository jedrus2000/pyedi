def safe_unicode(value):
    """ For errors: return best possible unicode...should never lead to errors.
    """
    # ~ print('safe_unicode0')
    try:
        if isinstance(value, str):  # is already unicode, just return
            return value
        elif isinstance(value, bytes):  # string/bytecode, encoding unknown.
            for charset in ["utf_8", "latin_1"]:
                try:
                    return value.decode(charset, "strict")  # decode strict
                except:
                    continue
            print("safe_unicode3")  # should never get here?
            return value.decode(
                "utf_8", "ignore"
            )  # decode as if it is utf-8, ignore errors.
        else:
            # ~ print('safe_unicode1',type(value))
            return str(value)
    except Exception as msg:
        print("safe_unicode2", msg)
        try:
            return str(repr(value))
        except:
            return "Error while displaying error"
