    def select_atoms(self, sel, *othersel, **selgroups):
        """Select :class:`Atoms<Atom>` using a selection string.

        Returns an :class:`AtomGroup` with :class:`Atoms<Atom>` sorted according
        to their index in the topology (this is to ensure that there are no
        duplicates, which can happen with complicated selections).

        Raises
        ------
        TypeError
            If the arbitrary groups passed are not of type
            :class:`MDAnalysis.core.groups.AtomGroup`

        Examples
        --------
        All simple selection listed below support multiple arguments which are
        implicitly combined with an or operator. For example

           >>> sel = universe.select_atoms('resname MET GLY')

        is equivalent to

           >>> sel = universe.select_atoms('resname MET or resname GLY')

        Will select all atoms with a residue name of either MET or GLY.

        Subselections can be grouped with parentheses.

           >>> sel = universe.select_atoms("segid DMPC and not ( name H* O* )")
           >>> sel
           <AtomGroup with 3420 atoms>


        Existing :class:`AtomGroup` objects can be passed as named arguments,
        which will then be available to the selection parser.

           >>> universe.select_atoms("around 10 group notHO", notHO=sel)
           <AtomGroup with 1250 atoms>

        Selections can be set to update automatically on frame change, by
        setting the `updating` keyword argument to `True`.  This will return
        a :class:`UpdatingAtomGroup` which can represent the solvation shell
        around another object.

           >>> universe.select_atoms("resname SOL and around 2.0 protein", updating=True)
           <Updating AtomGroup with 100 atoms>

        Notes
        -----

        If exact ordering of atoms is required (for instance, for
        :meth:`~AtomGroup.angle` or :meth:`~AtomGroup.dihedral` calculations)
        then one supplies selections *separately* in the required order. Also,
        when multiple :class:`AtomGroup` instances are concatenated with the
        ``+`` operator, then the order of :class:`Atom` instances is preserved
        and duplicates are *not* removed.


        See Also
        --------
        :ref:`selection-commands-label` for further details and examples.


        .. rubric:: Selection syntax


        The selection parser understands the following CASE SENSITIVE
        *keywords*:

        **Simple selections**

            protein, backbone, nucleic, nucleicbackbone
                selects all atoms that belong to a standard set of residues;
                a protein is identfied by a hard-coded set of residue names so
                it  may not work for esoteric residues.
            segid *seg-name*
                select by segid (as given in the topology), e.g. ``segid 4AKE``
                or ``segid DMPC``
            resid *residue-number-range*
                resid can take a single residue number or a range of numbers. A
                range consists of two numbers separated by a colon (inclusive)
                such as ``resid 1:5``. A residue number ("resid") is taken
                directly from the topology.
                If icodes are present in the topology, then these will be
                taken into account.  Ie 'resid 163B' will only select resid
                163 with icode B while 'resid 163' will select only residue 163.
                Range selections will also respect icodes, so 'resid 162-163B'
                will select all residues in 162 and those in 163 up to icode B.
            resnum *resnum-number-range*
                resnum is the canonical residue number; typically it is set to
                the residue id in the original PDB structure.
            resname *residue-name*
                select by residue name, e.g. ``resname LYS``
            name *atom-name*
                select by atom name (as given in the topology). Often, this is
                force field dependent. Example: ``name CA`` (for C&alpha; atoms)
                or ``name OW`` (for SPC water oxygen)
            type *atom-type*
                select by atom type; this is either a string or a number and
                depends on the force field; it is read from the topology file
                (e.g. the CHARMM PSF file contains numeric atom types). It has
                non-sensical values when a PDB or GRO file is used as a topology
            atom *seg-name*  *residue-number*  *atom-name*
                a selector for a single atom consisting of segid resid atomname,
                e.g. ``DMPC 1 C2`` selects the C2 carbon of the first residue of
                the DMPC segment
            altloc *alternative-location*
                a selection for atoms where alternative locations are available,
                which is often the case with high-resolution crystal structures
                e.g. `resid 4 and resname ALA and altloc B` selects only the
                atoms of ALA-4 that have an altloc B record.
            moltype *molecule-type*
                select by molecule type, e.g. ``moltype Protein_A``. At the
                moment, only the TPR format defines the molecule type.

        **Boolean**

            not
                all atoms not in the selection, e.g. ``not protein`` selects
                all atoms that aren't part of a protein

            and, or
                combine two selections according to the rules of boolean
                algebra, e.g. ``protein and not resname ALA LYS``
                selects all atoms that belong to a protein, but are not in a
                lysine or alanine residue

        **Geometric**

            around *distance*  *selection*
                selects all atoms a certain cutoff away from another selection,
                e.g. ``around 3.5 protein`` selects all atoms not belonging to
                protein that are within 3.5 Angstroms from the protein
            point *x* *y* *z*  *distance*
                selects all atoms within a cutoff of a point in space, make sure
                coordinate is separated by spaces,
                e.g. ``point 5.0 5.0 5.0  3.5`` selects all atoms within 3.5
                Angstroms of the coordinate (5.0, 5.0, 5.0)
            prop [abs] *property*  *operator*  *value*
                selects atoms based on position, using *property*  **x**, **y**,
                or **z** coordinate. Supports the **abs** keyword (for absolute
                value) and the following *operators*: **<, >, <=, >=, ==, !=**.
                For example, ``prop z >= 5.0`` selects all atoms with z
                coordinate greater than 5.0; ``prop abs z <= 5.0`` selects all
                atoms within -5.0 <= z <= 5.0.
            sphzone *radius* *selection*
                Selects all atoms that are within *radius* of the center of
                geometry of *selection*
            sphlayer *inner radius* *outer radius* *selection*
                Similar to sphzone, but also excludes atoms that are within
                *inner radius* of the selection COG
            cyzone *externalRadius* *zMax* *zMin* *selection*
                selects all atoms within a cylindric zone centered in the
                center of geometry (COG) of a given selection,
                e.g. ``cyzone 15 4 -8 protein and resid 42`` selects the
                center of geometry of protein and resid 42, and creates a
                cylinder of external radius 15 centered on the COG. In z, the
                cylinder extends from 4 above the COG to 8 below. Positive
                values for *zMin*, or negative ones for *zMax*, are allowed.
            cylayer *innerRadius* *externalRadius* *zMax* *zMin* *selection*
                selects all atoms within a cylindric layer centered in the
                center of geometry (COG) of a given selection,
                e.g. ``cylayer 5 10 10 -8 protein`` selects the center of
                geometry of protein, and creates a cylindrical layer of inner
                radius 5, external radius 10 centered on the COG. In z, the
                cylinder extends from 10 above the COG to 8 below. Positive
                values for *zMin*, or negative ones for *zMax*, are allowed.

        **Connectivity**

            byres *selection*
                selects all atoms that are in the same segment and residue as
                selection, e.g. specify the subselection after the byres keyword
            bonded *selection*
                selects all atoms that are bonded to selection
                eg: ``select name H and bonded name O`` selects only hydrogens
                bonded to oxygens

        **Index**

            bynum *index-range*
                selects all atoms within a range of (1-based) inclusive indices,
                e.g. ``bynum 1`` selects the first atom in the universe;
                ``bynum 5:10`` selects atoms 5 through 10 inclusive. All atoms
                in the :class:`~MDAnalysis.core.universe.Universe` are
                consecutively numbered, and the index runs from 1 up to the
                total number of atoms.

        **Preexisting selections**

            group `group-name`
                selects the atoms in the :class:`AtomGroup` passed to the
                function as an argument named `group-name`. Only the atoms
                common to `group-name` and the instance
                :meth:`~MDAnalysis.core.groups.AtomGroup.select_atoms`
                was called from will be considered, unless ``group`` is
                preceded by the ``global`` keyword. `group-name` will be
                included in the parsing just by comparison of atom indices.
                This means that it is up to the user to make sure the
                `group-name` group was defined in an appropriate
                :class:`~MDAnalysis.core.universe.Universe`.

            global *selection*
                by default, when issuing
                :meth:`~MDAnalysis.core.groups.AtomGroup.select_atoms` from an
                :class:`~MDAnalysis.core.groups.AtomGroup`, selections and
                subselections are returned intersected with the atoms of that
                instance. Prefixing a selection term with ``global`` causes its
                selection to be returned in its entirety.  As an example, the
                ``global`` keyword allows for
                ``lipids.select_atoms("around 10 global protein")`` --- where
                ``lipids`` is a group that does not contain any proteins. Were
                ``global`` absent, the result would be an empty selection since
                the ``protein`` subselection would itself be empty. When issuing
                :meth:`~MDAnalysis.core.groups.AtomGroup.select_atoms` from a
                :class:`~MDAnalysis.core.universe.Universe`, ``global`` is
                ignored.

        **Dynamic selections**
            If :meth:`~MDAnalysis.core.groups.AtomGroup.select_atoms` is
            invoked with named argument `updating` set to `True`, an
            :class:`~MDAnalysis.core.groups.UpdatingAtomGroup` instance will be
            returned, instead of a regular
            :class:`~MDAnalysis.core.groups.AtomGroup`. It behaves just like
            the latter, with the difference that the selection expressions are
            re-evaluated every time the trajectory frame changes (this happens
            lazily, only when the
            :class:`~MDAnalysis.core.groups.UpdatingAtomGroup` is accessed so
            that there is no redundant updating going on).
            Issuing an updating selection from an already updating group will
            cause later updates to also reflect the updating of the base group.
            A non-updating selection or a slicing operation made on an
            :class:`~MDAnalysis.core.groups.UpdatingAtomGroup` will return a
            static :class:`~MDAnalysis.core.groups.AtomGroup`, which will no
            longer update across frames.


        .. versionchanged:: 0.7.4 Added *resnum* selection.
        .. versionchanged:: 0.8.1 Added *group* and *fullgroup* selections.
        .. deprecated:: 0.11 The use of *fullgroup* has been deprecated in favor
            of the equivalent *global group* selections.
        .. versionchanged:: 0.13.0 Added *bonded* selection.
        .. versionchanged:: 0.16.0 Resid selection now takes icodes into account
            where present.
        .. versionchanged:: 0.16.0 Updating selections now possible by setting
            the `updating` argument.
        .. versionchanged:: 0.17.0 Added *moltype* and *molnum* selections.
        .. versionchanged:: 0.19.0
           Added strict type checking for passed groups.
           Added periodic kwarg (default True)
        .. versionchanged:: 0.19.2
           Empty sel string now returns an empty Atom group.
        """

        if not sel:
            warnings.warn("Empty string to select atoms, empty group returned.",
                          UserWarning)
            return self[[]]

        # once flags removed, replace with default=True
        periodic = selgroups.pop('periodic', flags['use_periodic_selections'])

        updating = selgroups.pop('updating', False)
        sel_strs = (sel,) + othersel

        for group, thing in selgroups.items():
            if not isinstance(thing, AtomGroup):
                raise TypeError("Passed groups must be AtomGroups. "
                                "You provided {} for group '{}'".format(
                                    thing.__class__.__name__, group))

        selections = tuple((selection.Parser.parse(s, selgroups, periodic=periodic)
                            for s in sel_strs))
        if updating:
            atomgrp = UpdatingAtomGroup(self, selections, sel_strs)
        else:
            # Apply the first selection and sum to it
            atomgrp = sum([sel.apply(self) for sel in selections[1:]],
                          selections[0].apply(self))
        return atomgrp