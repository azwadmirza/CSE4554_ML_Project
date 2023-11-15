    def __init__(self, atomgroup, reference=None, select='all',
                 groupselections=None, weights=None, weights_groupselections=False,
                 tol_mass=0.1, ref_frame=0, **kwargs):
        r"""Parameters
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
            A list of selections as described for `select`, with the difference
            that these selections are *always applied to the full universes*,
            i.e., ``atomgroup.universe.select_atoms(sel1)`` and
            ``reference.universe.select_atoms(sel2)``. Each selection describes
            additional RMSDs to be computed *after the structures have been
            superimposed* according to `select`. No additional fitting is
            performed.The output contains one additional column for each
            selection.

            .. Note:: Experimental feature. Only limited error checking
                      implemented.

        weights : {"mass", ``None``} or array_like (optional)
             1. "mass" will use masses as weights for both `select` and `groupselections`.

             2. ``None`` will weigh each atom equally for both `select` and `groupselections`.

             3. If 1D float array of the same length as `atomgroup` is provided,
             use each element of the `array_like` as a weight for the
             corresponding atom in `select`, and assumes ``None`` for `groupselections`.

        weights_groupselections : False or list of {"mass", ``None`` or array_like} (optional)
             1. ``False`` will apply imposed weights to `groupselections` from ``weights`` option.

             2. A list of {"mass", ``None`` or array_like} with the length of `groupselections`
             will apply the weights to `groupselections` correspondingly.

        tol_mass : float (optional)
             Reject match if the atomic masses for matched atoms differ by more
             than `tol_mass`.
        ref_frame : int (optional)
             frame index to select frame from `reference`
        verbose : bool (optional)
             Show detailed progress of the calculation if set to ``True``; the
             default is ``False``.

        Raises
        ------
        SelectionError
             If the selections from `atomgroup` and `reference` do not match.
        TypeError
             If `weights` or `weights_groupselections` is not of the appropriate type;
             see also :func:`MDAnalysis.lib.util.get_weights`
        ValueError
             If `weights` are not compatible with `atomgroup` (not the same
             length) or if it is not a 1D array (see
             :func:`MDAnalysis.lib.util.get_weights`).

             A :exc:`ValueError` is also raised if the length of `weights_groupselections` 
             are not compatible with `groupselections`.

        Notes
        -----
        The root mean square deviation :math:`\rho(t)` of a group of :math:`N`
        atoms relative to a reference structure as a function of time is
        calculated as

        .. math::

           \rho(t) = \sqrt{\frac{1}{N} \sum_{i=1}^N w_i \left(\mathbf{x}_i(t)
                                    - \mathbf{x}_i^{\text{ref}}\right)^2}

        The weights :math:`w_i` are calculated from the input weights `weights`
        :math:`w'_i` as relative to the mean of the input weights:

        .. math::

           w_i = \frac{w'_i}{\langle w' \rangle}

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


        See Also
        --------
        rmsd


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
        .. versionchanged:: 1.0.0
           `filename` keyword was removed.

        """
        super(RMSD, self).__init__(atomgroup.universe.trajectory,
                                   **kwargs)
        self.atomgroup = atomgroup
        self.reference = reference if reference is not None else self.atomgroup

        select = process_selection(select)
        self.groupselections = ([process_selection(s) for s in groupselections]
                                if groupselections is not None else [])
        self.weights = weights
        self.tol_mass = tol_mass
        self.ref_frame = ref_frame
        self.weights_groupselections = weights_groupselections
        self.ref_atoms = self.reference.select_atoms(*select['reference'])
        self.mobile_atoms = self.atomgroup.select_atoms(*select['mobile'])

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
                'reference': self.reference.universe.select_atoms(*s['reference']),
                'mobile': self.atomgroup.universe.select_atoms(*s['mobile']),
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

        # check weights type
        if iterable(self.weights) and (np.array(weights).dtype
                                not in (np.dtype('float64'),np.dtype('int64'))):
            raise TypeError("weight should only be be 'mass', None or 1D float array."
                                 "For weights on groupselections, use **weight_groupselections** ")
        if iterable(self.weights) or self.weights != "mass":
            get_weights(self.mobile_atoms, self.weights)

        if self.weights_groupselections:
            if len(self.weights_groupselections) != len(self.groupselections):
                raise ValueError("Length of weights_groupselections is not equal to "
                                 "length of groupselections ")
            for weights, atoms, selection in zip(self.weights_groupselections,
                                                 self._groupselections_atoms,
                                                 self.groupselections):
                try:
                    if iterable(weights) or weights != "mass":
                        get_weights(atoms['mobile'], weights)
                except Exception as e:
                    raise type(e)(str(e) + ' happens in selection %s' % selection['mobile'])