    def __init__(self, o):
        """
        Initialize the artist inspector with an
        :class:`~matplotlib.artist.Artist` or iterable of :class:`Artists`.
        If an iterable is used, we assume it is a homogeneous sequence (all
        :class:`Artists` are of the same type) and it is your responsibility
        to make sure this is so.
        """
        if cbook.iterable(o):
            # Wrapped in list instead of doing try-except around next(iter(o))
            o = list(o)
            if len(o):
                o = o[0]

        self.oorig = o
        if not inspect.isclass(o):
            o = type(o)
        self.o = o

        self.aliasd = self.get_aliases()