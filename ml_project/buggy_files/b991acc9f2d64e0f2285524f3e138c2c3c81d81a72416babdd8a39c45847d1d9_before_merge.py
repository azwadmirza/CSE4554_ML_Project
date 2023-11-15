    def __init__(self, atomgroup, reference=None, select='all',
                 groupselections=None, filename="rmsd.dat",
                 weights=None, tol_mass=0.1, ref_frame=0, **kwargs):
        r"""
        Parameters
        ----------
        atomgroup : AtomGroup or Universe
            Group of atoms for which the RMSD is calculated. If a trajectory is
            associated with the atoms then the computation iterates over the
            trajectory.
        reference : AtomGroup or Universe (optional)
            Group of reference atoms; if ``None`` then the current frame of
            `atomgroup` is used.
        select : str or dict or tuple (optional)
            The selection to operate on; can be one of:

            1. any valid selection string for
               :meth:`~MDAnalysis.core.groups.AtomGroup.select_atoms` that
               produces identical selections in `atomgroup` and `reference`; or

            2. a dictionary ``{'mobile': sel1, 'reference': sel2}`` where *sel1*
               and *sel2* are valid selection strings that are applied to
               `atomgroup` and `reference` respectively (the
               :func:`MDAnalysis.analysis.align.fasta2select` function returns such
               a dictionary based on a ClustalW_ or STAMP_ sequence alignment); or

            3. a tuple ``(sel1, sel2)``

            When using 2. or 3. with *sel1* and *sel2* then these selection strings
            are applied to `atomgroup` and `reference` respectively and should
            generate *groups of equivalent atoms*.  *sel1* and *sel2* can each also
            be a *list of selection strings* to generate a
            :class:`~MDAnalysis.core.groups.AtomGroup` with defined atom order as
            described under :ref:`ordered-selections-label`).

        groupselections : list (optional)
            A list of selections as described for `select`. Each selection
            describes additional RMSDs to be computed *after the
            structures have been superimposed* according to `select`. No
            additional fitting is performed.The output contains one
            additional column for each selection.

            .. Note:: Experimental feature. Only limited error checking
                      implemented.

        start : int (optional)
            starting frame, default None becomes 0.
        stop : int (optional)
            Frame index to stop analysis. Default: None becomes
            n_frames. Iteration stops *before* this frame number,
            which means that the trajectory would be read until the end.
        step : int (optional)
            step between frames, default ``None`` becomes 1.
        filename : str (optional)
            write RMSD into file with :meth:`RMSD.save`
        weights : {"mass", ``None``} or array_like (optional)
             choose weights. With ``"mass"`` uses masses as weights; with ``None``
             weigh each atom equally. If a float array of the same length as
             `atomgroup` is provided, use each element of the `array_like` as a
             weight for the corresponding atom in `atomgroup`.
        tol_mass : float (optional)
             Reject match if the atomic masses for matched atoms differ by more
             than `tol_mass`.
        ref_frame : int (optional)
             frame index to select frame from `reference`

        Raises
        ------
        SelectionError
             If the selections from `atomgroup` and `reference` do not match.
        TypeError
             If `weights` is not of the appropriate type; see
             :func:`MDAnalysis.lib.util.get_weights`
        ValueError
             If `weights` are not compatible with `groupselections`: only equal
             weights (``weights=None``) or mass-weighted (``weights="mass"``)
             is supported.

        Notes
        -----
        The root mean square deviation of a group of :math:`N` atoms relative to a
        reference structure as a function of time is calculated as

        .. math::

           \rho(t) = \sqrt{\frac{1}{N} \sum_{i=1}^N w_i \left(\mathbf{x}_i(t)
                                    - \mathbf{x}_i^{\text{ref}}\right)^2}

        The selected coordinates from `atomgroup` are optimally superimposed
        (translation and rotation) on the `reference` coordinates at each time step
        as to minimize the RMSD. Douglas Theobald's fast QCP algorithm
        [Theobald2005]_ is used for the rotational superposition and to calculate
        the RMSD (see :mod:`MDAnalysis.lib.qcprot` for implementation details).

        The class runs various checks on the input to ensure that the two atom
        groups can be compared. This includes a comparison of atom masses (i.e.,
        only the positions of atoms of the same mass will be considered to be
        correct for comparison). If masses should not be checked, just set
        `tol_mass` to a large value such as 1000.

        .. _ClustalW: http://www.clustal.org/
        .. _STAMP: http://www.compbio.dundee.ac.uk/manuals/stamp.4.2/


        .. versionadded:: 0.7.7
        .. versionchanged:: 0.8
           `groupselections` added
        .. versionchanged:: 0.16.0
           Flexible weighting scheme with new `weights` keyword.
        .. deprecated:: 0.16.0
           Instead of ``mass_weighted=True`` (removal in 0.17.0) use new
           ``weights='mass'``; refactored to fit with AnalysisBase API
        .. versionchanged:: 0.17.0
           removed deprecated `mass_weighted` keyword; `groupselections`
           are *not* rotationally superimposed any more.
        """
        super(RMSD, self).__init__(atomgroup.universe.trajectory,
                                   **kwargs)
        self.universe = atomgroup.universe
        self.reference = reference if reference is not None else self.universe

        select = process_selection(select)
        self.groupselections = ([process_selection(s) for s in groupselections]
                                if groupselections is not None else [])
        self.weights = weights
        self.tol_mass = tol_mass
        self.ref_frame = ref_frame
        self.filename = filename

        self.ref_atoms = self.reference.select_atoms(*select['reference'])
        self.mobile_atoms = self.universe.select_atoms(*select['mobile'])

        if len(self.ref_atoms) != len(self.mobile_atoms):
            err = ("Reference and trajectory atom selections do "
                   "not contain the same number of atoms: "
                   "N_ref={0:d}, N_traj={1:d}".format(self.ref_atoms.n_atoms,
                                                      self.mobile_atoms.n_atoms))
            logger.exception(err)
            raise SelectionError(err)
        logger.info("RMS calculation "
                    "for {0:d} atoms.".format(len(self.ref_atoms)))
        mass_mismatches = (np.absolute((self.ref_atoms.masses -
                                        self.mobile_atoms.masses)) >
                           self.tol_mass)

        if np.any(mass_mismatches):
            # diagnostic output:
            logger.error("Atoms: reference | mobile")
            for ar, at in zip(self.ref_atoms, self.mobile_atoms):
                if ar.name != at.name:
                    logger.error("{0!s:>4} {1:3d} {2!s:>3} {3!s:>3} {4:6.3f}"
                                 "|  {5!s:>4} {6:3d} {7!s:>3} {8!s:>3}"
                                 "{9:6.3f}".format(ar.segid, ar.resid,
                                                   ar.resname, ar.name,
                                                   ar.mass, at.segid, at.resid,
                                                   at.resname, at.name,
                                                   at.mass))
            errmsg = ("Inconsistent selections, masses differ by more than"
                      "{0:f}; mis-matching atoms"
                      "are shown above.".format(self.tol_mass))
            logger.error(errmsg)
            raise SelectionError(errmsg)
        del mass_mismatches

        # TODO:
        # - make a group comparison a class that contains the checks above
        # - use this class for the *select* group and the additional
        #   *groupselections* groups each a dict with reference/mobile
        self._groupselections_atoms = [
            {
                'reference': self.reference.select_atoms(*s['reference']),
                'mobile': self.universe.select_atoms(*s['mobile']),
            }
            for s in self.groupselections]
        # sanity check
        for igroup, (sel, atoms) in enumerate(zip(self.groupselections,
                                                  self._groupselections_atoms)):
            if len(atoms['mobile']) != len(atoms['reference']):
                logger.exception('SelectionError: Group Selection')
                raise SelectionError(
                    "Group selection {0}: {1} | {2}: Reference and trajectory "
                    "atom selections do not contain the same number of atoms: "
                    "N_ref={3}, N_traj={4}".format(
                        igroup, sel['reference'], sel['mobile'],
                        len(atoms['reference']), len(atoms['mobile'])))

        # Explicitly check for "mass" because this option CAN
        # be used with groupselection. (get_weights() returns the mass array
        # for "mass")
        if self.weights != "mass":
            self.weights = get_weights(self.mobile_atoms, self.weights)

        # cannot use arbitrary weight array (for superposition) with
        # groupselections because arrays will not match
        if len(self.groupselections) > 0 and self.weights not in ("mass", None):
            raise ValueError("groupselections can only be combined with "
                             "weights=None or weights='mass', not a weight "
                             "array.")

        # initialized to note for testing the save function
        self.rmsd = None