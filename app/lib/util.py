def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def normalize_archive_letter(letter: str | None) -> str:
    """
    Normalize a letter for archive navigation and filtering.

    Args:
        letter: Single character or special value '0-9'

    Returns:
        - Lowercase letter (a-z) for alphabetic characters
        - '0-9' for the digits/symbols category
        - Empty string for invalid input
    """
    if not letter:
        return ""

    letter = letter.strip()

    if letter == "0-9":
        return "0-9"

    if len(letter) == 1 and letter.isalpha():
        return letter.lower()

    return ""
