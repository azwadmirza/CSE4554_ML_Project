def _is_utf(encoding):
    return encoding.lower().startswith('utf-') or ('U8' == encoding)