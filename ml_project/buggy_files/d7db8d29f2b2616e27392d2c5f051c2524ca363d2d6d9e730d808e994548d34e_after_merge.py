def quote_ps_string(s):
    "Quote dangerous characters of S for use in a PostScript string constant."
    s = s.replace(b"\\", b"\\\\")
    s = s.replace(b"(", b"\\(")
    s = s.replace(b")", b"\\)")
    s = s.replace(b"'", b"\\251")
    s = s.replace(b"`", b"\\301")
    s = re.sub(br"[^ -~\n]", lambda x: br"\%03o" % ord(x.group()), s)
    return s.decode('ascii')