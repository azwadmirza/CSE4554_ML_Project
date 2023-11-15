def _handle_output(result):
    """Convert result to unicode."""
    if not result:
        return result

    if isinstance(result, binary_type):
        # on windows the returned info from fs operations needs to be decoded using fs encoding
        return text_type(result, 'utf-8' if os.name != 'nt' else fs_encoding)

    if isinstance(result, list) or isinstance(result, tuple):
        return map(_handle_output, result)

    if isinstance(result, dict):
        for k, v in result.items():
            result[k] = _handle_output(v)
        return result

    return result