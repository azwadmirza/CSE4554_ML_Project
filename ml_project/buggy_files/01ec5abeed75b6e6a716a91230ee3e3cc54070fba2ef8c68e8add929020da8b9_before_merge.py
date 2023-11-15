    def parse(self):
        """Parse atom information from PQR file *filename*.

        Returns
        -------
        A MDAnalysis Topology object
        """
        serials = []
        names = []
        resnames = []
        chainIDs = []
        resids = []
        charges = []
        radii = []

        with openany(self.filename, 'r') as f:
            for line in f:
                if line.startswith(("ATOM", "HETATM")):
                    fields = line.split()
                    try:
                        (recordName, serial, name, resName,
                         chainID, resSeq, x, y, z, charge,
                         radius) = fields
                    except ValueError:
                        # files without the chainID
                        (recordName, serial, name, resName,
                         resSeq, x, y, z, charge, radius) = fields
                        chainID = "SYSTEM"
                    serials.append(serial)
                    names.append(name)
                    resnames.append(resName)
                    resids.append(resSeq)
                    charges.append(charge)
                    radii.append(radius)
                    chainIDs.append(chainID)

        n_atoms = len(serials)

        atomtypes = guessers.guess_types(names)
        masses = guessers.guess_masses(atomtypes)

        attrs = []
        attrs.append(Atomids(np.array(serials, dtype=np.int32)))
        attrs.append(Atomnames(np.array(names, dtype=object)))
        attrs.append(Charges(np.array(charges, dtype=np.float32)))
        attrs.append(Atomtypes(atomtypes, guessed=True))
        attrs.append(Masses(masses, guessed=True))
        attrs.append(Radii(np.array(radii, dtype=np.float32)))

        resids = np.array(resids, dtype=np.int32)
        resnames = np.array(resnames, dtype=object)
        chainIDs = np.array(chainIDs, dtype=object)

        residx, resids, (resnames, chainIDs) = squash_by(
            resids, resnames, chainIDs)

        n_residues = len(resids)
        attrs.append(Resids(resids))
        attrs.append(Resnums(resids.copy()))
        attrs.append(Resnames(resnames))

        segidx, chainIDs = squash_by(chainIDs)[:2]

        n_segments = len(chainIDs)
        attrs.append(Segids(chainIDs))

        top = Topology(n_atoms, n_residues, n_segments,
                       attrs=attrs,
                       atom_resindex=residx,
                       residue_segindex=segidx)

        return top