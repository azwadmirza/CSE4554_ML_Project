    def __init__(self, vstring):
        self.vstring = vstring
        ver_main = re.match(r'\d[.]\d+[.]\d+', vstring)
        if not ver_main:
            raise ValueError("Not a valid numpy version string")

        self.version = ver_main.group()
        self.major, self.minor, self.bugfix = [int(x) for x in
            self.version.split('.')]
        if len(vstring) == ver_main.end():
            self.pre_release = 'final'
        else:
            alpha = re.match(r'a\d', vstring[ver_main.end():])
            beta = re.match(r'b\d', vstring[ver_main.end():])
            rc = re.match(r'rc\d', vstring[ver_main.end():])
            pre_rel = [m for m in [alpha, beta, rc] if m is not None]
            if pre_rel:
                self.pre_release = pre_rel[0].group()
            else:
                self.pre_release = ''

        self.is_devversion = bool(re.search(r'.dev', vstring))