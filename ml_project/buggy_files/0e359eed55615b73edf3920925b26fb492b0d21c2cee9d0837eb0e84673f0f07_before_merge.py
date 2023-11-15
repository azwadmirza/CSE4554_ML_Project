def _is_utf(encoding):
    try:
        u'\u2588\u2589'.encode(encoding)
    except UnicodeEncodeError:  # pragma: no cover
        return False
    except Exception:  # pragma: no cover
        try:
            return encoding.lower().startswith('utf-') or ('U8' == encoding)
        except:
            return False
    else:
        return True