    def __init__(self,              # pylint: disable=C0103
                 major,
                 minor,
                 bugfix=0,
                 rc=0,              # pylint: disable=C0103
                 noc=0,
                 sha=None):

        if isinstance(major, string_types):
            major = int(major)

        if isinstance(minor, string_types):
            minor = int(minor)

        if bugfix is None:
            bugfix = 0
        elif isinstance(bugfix, string_types):
            bugfix = int(bugfix)

        if rc is None:
            rc = 0
        elif isinstance(rc, string_types):
            rc = int(rc)

        if noc is None:
            noc = 0
        elif isinstance(noc, string_types):
            noc = int(noc)

        self.major = major
        self.minor = minor
        self.bugfix = bugfix
        self.rc = rc  # pylint: disable=C0103
        self.name = self.VNAMES.get((major, minor, bugfix, rc), None)
        self.noc = noc
        self.sha = sha