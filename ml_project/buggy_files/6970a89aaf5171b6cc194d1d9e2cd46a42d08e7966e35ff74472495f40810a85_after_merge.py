    def __init__(self, app):
        # type: (Sphinx) -> None
        self.srcdir = app.srcdir
        self.confdir = app.confdir
        self.outdir = app.outdir
        self.doctreedir = app.doctreedir
        ensuredir(self.doctreedir)

        self.app = app              # type: Sphinx
        self.env = None             # type: BuildEnvironment
        self.warn = app.warn        # type: Callable
        self.info = app.info        # type: Callable
        self.config = app.config    # type: Config
        self.tags = app.tags        # type: Tags
        self.tags.add(self.format)
        self.tags.add(self.name)
        self.tags.add("format_%s" % self.format)
        self.tags.add("builder_%s" % self.name)
        # compatibility aliases
        self.status_iterator = app.status_iterator
        self.old_status_iterator = app.old_status_iterator

        # images that need to be copied over (source -> dest)
        self.images = {}  # type: Dict[unicode, unicode]
        # basename of images directory
        self.imagedir = ""
        # relative path to image directory from current docname (used at writing docs)
        self.imgpath = ""  # type: unicode

        # these get set later
        self.parallel_ok = False
        self.finish_tasks = None  # type: Any