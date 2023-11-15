def posix_pipe(fin, fout, delim='\n', buf_size=256,
               callback=lambda int: None  # pragma: no cover
               ):
    """
    Params
    ------
    fin  : file with `read(buf_size : int)` method
    fout  : file with `write` (and optionally `flush`) methods.
    callback  : function(int), e.g.: `tqdm.update`
    """
    fp_write = fout.write

    # tmp = ''
    if not delim:
        while True:
            tmp = fin.read(buf_size)

            # flush at EOF
            if not tmp:
                getattr(fout, 'flush', lambda: None)()  # pragma: no cover
                return

            fp_write(tmp)
            callback(len(tmp))
        # return

    buf = ''
    # n = 0
    while True:
        tmp = fin.read(buf_size)

        # flush at EOF
        if not tmp:
            if buf:
                fp_write(buf)
                callback(1 + buf.count(delim))  # n += 1 + buf.count(delim)
            getattr(fout, 'flush', lambda: None)()  # pragma: no cover
            return  # n

        while True:
            try:
                i = tmp.index(delim)
            except ValueError:
                buf += tmp
                break
            else:
                fp_write(buf + tmp[:i + len(delim)])
                callback(1)  # n += 1
                buf = ''
                tmp = tmp[i + len(delim):]