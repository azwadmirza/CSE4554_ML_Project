def _peekkey_ss3(offset):
    global _cbuf
    if len(_cbuf) <= offset:
        return Key(kc.TYPE_UNICODE, u'O', kc.MOD_ALT)
    cmd = _cbuf[offset]
    if cmd < 0x40 or cmd >= 0x80:
        return
    _cbuf = _cbuf[offset:]

    if chr(cmd) in _csi_ss3s:
        return Key(*_csi_ss3s[chr(cmd)])

    if chr(cmd) in _csi_ss3kp:
        t, c, a = _csi_ss3kp[chr(cmd)]
        if FLAG_CONVERTKP and a:
            return Key(kc.TYPE_UNICODE, a)
        else:
            return Key(t, c)