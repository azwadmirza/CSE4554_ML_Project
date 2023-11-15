def findTTFont(fname):

    def get_family(query):
        data = os.popen("fc-match \"%s\""%query, "r").read()
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            fname, family, _, variant = line.split('"')[:4]
            family = family.replace('"', '')
            if family:
                return family
        return None

    def get_fname(query):
        data = os.popen("fc-match -v \"%s\""%query, "r").read()
        for line in data.splitlines():
            line = line.strip()
            if line.startswith("file: "):
                return line.split('"')[1]
        return None

    def get_variants(family):
        variants = [
            get_fname(family + ":style=Roman"),
            get_fname(family + ":style=Bold"),
            get_fname(family + ":style=Oblique"),
            get_fname(family + ":style=Bold Oblique")]
        if variants[2] == variants[0]:
            variants[2] = get_fname(family + ":style=Italic")
        if variants[3] == variants[0]:
            variants[3] = get_fname(family + ":style=Bold Italic")
        if variants[0].endswith('.pfb') or variants[0].endswith('.gz'):
            return None
        return variants

    if os.name != 'nt':
        family = get_family(fname)
        if not family:
            log.error("Unknown font: %s", fname)
            return None
        return get_variants(family)
    else:
        # lookup required font in registry lookup, alternative approach
        # is to let loadFont() traverse windows font directory or use
        # ctypes with EnumFontFamiliesEx

        def get_nt_fname(ftname):
            import _winreg as _w
            fontkey = _w.OpenKey(_w.HKEY_LOCAL_MACHINE,
                "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")
            fontname = ftname + " (TrueType)"
            try:
                fname = _w.QueryValueEx(fontkey, fontname)[0]
                if os.path.isabs(fname):
                    fontkey.close()
                    return fname
                fontdir = os.environ.get("SystemRoot", u"C:\\Windows")
                fontdir += u"\\Fonts"
                fontkey.Close()
                return fontdir + "\\" + fname
            except WindowsError as err:
                fontkey.Close()
                return None

        family, pos = guessFont(fname)
        fontfile = get_nt_fname(fname)
        if not fontfile:
            if pos == 0:
                fontfile = get_nt_fname(family)
            elif pos == 1:
                fontfile = get_nt_fname(family + " Bold")
            elif pos == 2:
                fontfile = get_nt_fname(family + " Italic") or \
                    get_nt_fname(family + " Oblique")
            else:
                fontfile = get_nt_fname(family + " Bold Italic") or \
                    get_nt_fname(family + " Bold Oblique")

            if not fontfile:
                log.error("Unknown font: %s", fname)
                return None

        family, pos = guessFont(fname)
        variants = [
            get_nt_fname(family) or fontfile,
            get_nt_fname(family+" Bold") or fontfile,
            get_nt_fname(family+" Italic") or \
                get_nt_fname(family+" Oblique") or fontfile,
            get_nt_fname(family+" Bold Italic") or \
                get_nt_fname(family+" Bold Oblique") or fontfile,
        ]
        return variants