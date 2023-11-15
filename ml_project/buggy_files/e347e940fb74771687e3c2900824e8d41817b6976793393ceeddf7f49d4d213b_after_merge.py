    def __init__(self, traj, reference=None, select='all',
                 groupselections=None, filename="rmsd.dat",
                 mass_weighted=False, tol_mass=0.1, ref_frame=0):
        """Setting up the RMSD analysis.

        The RMSD will be computed between *select* and *reference* for
        all frames in the trajectory in *universe*.

        Parameters
        ----------
        traj : :class:`MDAnalysis.Universe`
            universe that contains a trajectory
        reference : :class:`MDAnalysis.Universe` (optional)
            reference coordinates, if ``None`` current frame of *traj* is used
        select : str / dict / tuple (optional)
            The selection to operate on; can be one of:

            1. any valid selection string for
               :meth:`~MDAnalysis.core.AtomGroup.AtomGroup.select_atoms` that
               produces identical selections in *mobile* and *reference*; or

            2. a dictionary ``{'mobile':sel1, 'reference':sel2}`` (the
               :func:`MDAnalysis.analysis.align.fasta2select` function returns
               such a dictionary based on a ClustalW_ or STAMP_ sequence
               alignment); or
            3. a tuple ``(sel1, sel2)``

            When using 2. or 3. with *sel1* and *sel2* then these selections
            can also each be a list of selection strings (to generate a
            AtomGroup with defined atom order as described under
            :ref:`ordered-selections-label`).
        groupselections : list (optional)
            A list of selections as described for *select*. Each selection
            describes additional RMSDs to be computed *after the structures
            have be superpositioned* according to *select*. The output contains
            one additional column for each selection. [``None``]

            .. Note:: Experimental feature. Only limited error checking
                      implemented.
        filename : str (optional)
            write RSMD into file file :meth:`RMSD.save`
        mass_weighted : bool (optional)
             do a mass-weighted RMSD fit
        tol_mass : float (optional)
             Reject match if the atomic masses for matched atoms differ by more
             than `tol_mass`
        ref_frame : int (optional)
             frame index to select frame from `reference`

        .. _ClustalW: http://www.clustal.org/
        .. _STAMP: http://www.compbio.dundee.ac.uk/manuals/stamp.4.2/

        .. versionadded:: 0.7.7
        .. versionchanged:: 0.8
           *groupselections* added

        """
        self.universe = traj
        if reference is None:
            self.reference = self.universe
        else:
            self.reference = reference
        self.select = process_selection(select)
        if groupselections is not None:
            self.groupselections = [process_selection(s) for s in groupselections]
        else:
            self.groupselections = []
        self.mass_weighted = mass_weighted
        self.tol_mass = tol_mass
        self.ref_frame = ref_frame
        self.filename = filename

        self.ref_atoms = self.reference.select_atoms(*self.select['reference'])
        self.traj_atoms = self.universe.select_atoms(*self.select['mobile'])
        if len(self.ref_atoms) != len(self.traj_atoms):
            errmsg = ("Reference and trajectory atom selections do "+
                      "not contain the same number of atoms: "+
                      "N_ref={0:d}, N_traj={1:d}".format(self.ref_atoms.n_atoms,
                                                        self.traj_atoms.n_atoms))
            logger.exception(errmsg)
            raise SelectionError(errmsg)
        logger.info("RMS calculation for {0:d} atoms.".format(len(self.ref_atoms)))
        mass_mismatches = (np.absolute(self.ref_atoms.masses - self.traj_atoms.masses) > self.tol_mass)
        if np.any(mass_mismatches):
            # diagnostic output:
            logger.error("Atoms: reference | trajectory")
            for ar, at in zip(self.ref_atoms, self.traj_atoms):
                if ar.name != at.name:
                    logger.error("{0!s:>4} {1:3d} {2!s:>3} {3!s:>3} {4:6.3f}  |  {5!s:>4} {6:3d} {7!s:>3} {8!s:>3} {9:6.3f}".format(ar.segid, ar.resid, ar.resname, ar.name, ar.mass,
                                 at.segid, at.resid, at.resname, at.name, at.mass))
            errmsg = ("Inconsistent selections, masses differ by more than"
                     + "{0:f}; mis-matching atoms are shown above.".format(
                     self.tol_mass))
            logger.error(errmsg)
            raise SelectionError(errmsg)
        del mass_mismatches

        # TODO:
        # - make a group comparison a class that contains the checks above
        # - use this class for the *select* group and the additional
        #   *groupselections* groups each a dict with reference/mobile
        self.groupselections_atoms = [
            {
                'reference': self.reference.select_atoms(*s['reference']),
                'mobile': self.universe.select_atoms(*s['mobile']),
            }
            for s in self.groupselections]
        # sanity check
        for igroup, (sel, atoms) in enumerate(zip(self.groupselections,
                                                  self.groupselections_atoms)):
            if len(atoms['mobile']) != len(atoms['reference']):
                logger.exception('SelectionError: Group Selection')
                raise SelectionError(
                    "Group selection {0}: {1} | {2}: Reference and trajectory "
                    "atom selections do not contain the same number of atoms: "
                    "N_ref={3}, N_traj={4}".format(
                        igroup, sel['reference'], sel['mobile'],
                        len(atoms['reference']), len(atoms['mobile'])))

        self.rmsd = None