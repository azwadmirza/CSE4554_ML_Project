    def parse(self, **kwargs):
        """Parse PSF file into Topology

        Returns
        -------
        MDAnalysis *Topology* object
        """
        # Open and check psf validity
        with openany(self.filename) as psffile:
            header = next(psffile)
            if not header.startswith("PSF"):
                err = ("{0} is not valid PSF file (header = {1})"
                       "".format(self.filename, header))
                logger.error(err)
                raise ValueError(err)
            header_flags = header[3:].split()

            if "NAMD" in header_flags:
                self._format = "NAMD"        # NAMD/VMD
            elif "EXT" in header_flags:
                self._format = "EXTENDED"    # CHARMM
            else:
                self._format = "STANDARD"    # CHARMM

            next(psffile)
            title = next(psffile).split()
            if not (title[1] == "!NTITLE"):
                err = "{0} is not a valid PSF file".format(self.filename)
                logger.error(err)
                raise ValueError(err)
            # psfremarks = [psffile.next() for i in range(int(title[0]))]
            for _ in range(int(title[0])):
                next(psffile)
            logger.debug("PSF file {0}: format {1}"
                         "".format(self.filename, self._format))

            # Atoms first and mandatory
            top = self._parse_sec(
                psffile, ('NATOM', 1, 1, self._parseatoms))
            # Then possibly other sections
            sections = (
                #("atoms", ("NATOM", 1, 1, self._parseatoms)),
                (Bonds, ("NBOND", 2, 4, self._parsesection)),
                (Angles, ("NTHETA", 3, 3, self._parsesection)),
                (Dihedrals, ("NPHI", 4, 2, self._parsesection)),
                (Impropers, ("NIMPHI", 4, 2, self._parsesection)),
                #("donors", ("NDON", 2, 4, self._parsesection)),
                #("acceptors", ("NACC", 2, 4, self._parsesection))
            )

            try:
                for attr, info in sections:
                    next(psffile)
                    top.add_TopologyAttr(
                        attr(self._parse_sec(psffile, info)))
            except StopIteration:
                # Reached the end of the file before we expected
                pass

        return top