from urllib.parse import urlencode


def qs_update(existing_qs, filter, value):
    rtn_qs = existing_qs.copy()
    rtn_qs.pop(filter, None)
    rtn_qs.update({filter: value})
    return urlencode(rtn_qs)
