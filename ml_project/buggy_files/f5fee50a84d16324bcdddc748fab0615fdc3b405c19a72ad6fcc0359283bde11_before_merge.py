def hy_exc_handler(exc_type, exc_value, exc_traceback):
    """Produce exceptions print-outs with all frames originating from the
    modules in `_tb_hidden_modules` filtered out.

    The frames are actually filtered by each module's filename and only when a
    subclass of `HyLanguageError` is emitted.

    This does not remove the frames from the actual tracebacks, so debugging
    will show everything.
    """
    try:
        # frame = (filename, line number, function name*, text)
        new_tb = [frame for frame in traceback.extract_tb(exc_traceback)
                  if not (frame[0].replace('.pyc', '.py') in _tb_hidden_modules or
                          os.path.dirname(frame[0]) in _tb_hidden_modules)]

        lines = traceback.format_list(new_tb)

        if lines:
            lines.insert(0, "Traceback (most recent call last):\n")

        lines.extend(traceback.format_exception_only(exc_type, exc_value))
        output = ''.join(lines)

        sys.stderr.write(output)
        sys.stderr.flush()
    except Exception:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)