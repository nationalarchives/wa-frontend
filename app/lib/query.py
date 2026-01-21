from urllib.parse import urlencode


def qs_update(existing_qs, filter, value):
    rtn_qs = existing_qs.copy()
    try:
        rtn_qs.pop(filter)
    except KeyError:
        pass
    rtn_qs.update({filter: value})
    return urlencode(rtn_qs)
