    def __init__(self, filename, n_atoms, title='TRZ', convert_units=None):
        """Create a TRZWriter

        Parameters
        ----------
        filename : str
            name of output file
        n_atoms : int
            number of atoms in trajectory
        title : str (optional)
            title of the trajectory; the title must be 80 characters or
            shorter, a longer title raises a ValueError exception.
        convert_units : bool (optional)
            units are converted to the MDAnalysis base format; ``None`` selects
            the value of :data:`MDAnalysis.core.flags` ['convert_lengths'].
            (see :ref:`flags-label`)
        """
        self.filename = filename
        if n_atoms is None:
            raise ValueError("TRZWriter requires the n_atoms keyword")
        if n_atoms == 0:
            raise ValueError("TRZWriter: no atoms in output trajectory")
        self.n_atoms = n_atoms

        if len(title) > 80:
            raise ValueError("TRZWriter: 'title' must be 80 characters of shorter")

        if convert_units is None:
            convert_units = flags['convert_lengths']
        self.convert_units = convert_units

        self.trzfile = util.anyopen(self.filename, 'wb')

        self._writeheader(title)

        floatsize = str(n_atoms) + 'f4'
        self.frameDtype = np.dtype([
            ('p1a', 'i4'),
            ('nframe', 'i4'),
            ('ntrj', 'i4'),
            ('natoms', 'i4'),
            ('treal', 'f8'),
            ('p1b', 'i4'),
            ('p2a', 'i4'),
            ('box', '9f8'),
            ('p2b', 'i4'),
            ('p3a', 'i4'),
            ('pressure', 'f8'),
            ('ptensor', '6f8'),
            ('p3b', 'i4'),
            ('p4a', 'i4'),
            ('six', 'i4'),
            ('etot', 'f8'),
            ('ptot', 'f8'),
            ('ek', 'f8'),
            ('T', 'f8'),
            ('blanks', '2f8'),
            ('p4b', 'i4'),
            ('p5a', 'i4'),
            ('rx', floatsize),
            ('p5b', 'i4'),
            ('p6a', 'i4'),
            ('ry', floatsize),
            ('p6b', 'i4'),
            ('p7a', 'i4'),
            ('rz', floatsize),
            ('p7b', 'i4'),
            ('p8a', 'i4'),
            ('vx', floatsize),
            ('p8b', 'i4'),
            ('p9a', 'i4'),
            ('vy', floatsize),
            ('p9b', 'i4'),
            ('p10a', 'i4'),
            ('vz', floatsize),
            ('p10b', 'i4')])