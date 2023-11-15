    def __init__(self, trzfilename, n_atoms=None, **kwargs):
        """Creates a TRZ Reader

        Parameters
        ----------
        trzfilename : str
            name of input file
        n_atoms : int
            number of atoms in trajectory, must be taken from topology file!
        convert_units : bool (optional)
            converts units to MDAnalysis defaults
        """
        super(TRZReader, self).__init__(trzfilename,  **kwargs)

        if n_atoms is None:
            raise ValueError('TRZReader requires the n_atoms keyword')

        self.trzfile = util.anyopen(self.filename, 'rb')
        self._cache = dict()
        self._n_atoms = n_atoms

        self._read_trz_header()
        self.ts = Timestep(self.n_atoms,
                           velocities=True,
                           forces=self.has_force,
                           reader=self,
                           **self._ts_kwargs)

        # structured dtype of a single trajectory frame
        readarg = str(n_atoms) + '<f4'
        frame_contents = [
            ('p1', '<i4'),
            ('nframe', '<i4'),
            ('ntrj', '<i4'),
            ('natoms', '<i4'),
            ('treal', '<f8'),
            ('p2', '<2i4'),
            ('box', '<9f8'),
            ('p3', '<2i4'),
            ('pressure', '<f8'),
            ('ptensor', '<6f8'),
            ('p4', '<3i4'),
            ('etot', '<f8'),
            ('ptot', '<f8'),
            ('ek', '<f8'),
            ('T', '<f8'),
            ('p5', '<6i4'),
            ('rx', readarg),
            ('pad2', '<2i4'),
            ('ry', readarg),
            ('pad3', '<2i4'),
            ('rz', readarg),
            ('pad4', '<2i4'),
            ('vx', readarg),
            ('pad5', '<2i4'),
            ('vy', readarg),
            ('pad6', '<2i4'),
            ('vz', readarg)]
        if not self.has_force:
            frame_contents += [('pad7', '<i4')]
        else:
            frame_contents += [
                ('pad7', '<2i4'),
                ('fx', readarg),
                ('pad8', '<2i4'),
                ('fy', readarg),
                ('pad9', '<2i4'),
                ('fz', readarg),
                ('pad10', '<i4')]
        self._dtype = np.dtype(frame_contents)

        self._read_next_timestep()