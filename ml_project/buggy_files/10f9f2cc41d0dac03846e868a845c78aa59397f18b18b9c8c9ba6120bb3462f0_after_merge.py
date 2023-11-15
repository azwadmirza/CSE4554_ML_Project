    def install(self, spec, prefix):
        self.check_variants(spec)

        base_components = "ALL"  # when in doubt, install everything
        mpi_components = ""
        mkl_components = ""
        daal_components = ""
        ipp_components = ""

        if not spec.satisfies('+all'):
            all_components = get_all_components()
            regex = '(comp|openmp|intel-tbb|icc|ifort|psxe|icsxe-pset)'
            base_components = \
                filter_pick(all_components, re.compile(regex).search)
            regex = '(icsxe|imb|mpi|itac|intel-ta|intel-tc|clck)'
            mpi_components = \
                filter_pick(all_components, re.compile(regex).search)
            mkl_components = \
                filter_pick(all_components, re.compile('(mkl)').search)
            daal_components = \
                filter_pick(all_components, re.compile('(daal)').search)
            ipp_components = \
                filter_pick(all_components, re.compile('(ipp)').search)
            regex = '(gdb|vtune|inspector|advisor)'
            tool_components = \
                filter_pick(all_components, re.compile(regex).search)
            components = base_components

        if not spec.satisfies('+all'):
            if spec.satisfies('+mpi'):
                components += mpi_components
            if spec.satisfies('+mkl'):
                components += mkl_components
            if spec.satisfies('+daal'):
                components += daal_components
            if spec.satisfies('+ipp'):
                components += ipp_components
            if spec.satisfies('+tools') and (spec.satisfies('@cluster') or
                                             spec.satisfies('@professional')):
                components += tool_components

        if spec.satisfies('+all'):
            self.intel_components = 'ALL'
        else:
            self.intel_components = ';'.join(components)
        IntelInstaller.install(self, spec, prefix)

        absbindir = os.path.dirname(
            os.path.realpath(os.path.join(self.prefix.bin, "icc")))
        abslibdir = os.path.dirname(
            os.path.realpath(os.path.join(
                self.prefix.lib, "intel64", "libimf.a")))

        os.symlink(self.global_license_file, os.path.join(absbindir,
                                                          "license.lic"))
        if spec.satisfies('+tools') and (spec.satisfies('@cluster') or
                                         spec.satisfies('@professional')):
            inspector_dir = "inspector_xe/licenses"
            advisor_dir = "advisor_xe/licenses"
            vtune_amplifier_dir = "vtune_amplifier_xe/licenses"

            year = int(str(self.version).split('.')[1])
            if year >= 2017:
                inspector_dir = "inspector/licenses"
                advisor_dir = "advisor/licenses"

            os.mkdir(os.path.join(self.prefix, inspector_dir))
            os.symlink(self.global_license_file, os.path.join(
                self.prefix, inspector_dir, "license.lic"))
            os.mkdir(os.path.join(self.prefix, advisor_dir))
            os.symlink(self.global_license_file, os.path.join(
                self.prefix, advisor_dir, "license.lic"))
            os.mkdir(os.path.join(self.prefix, vtune_amplifier_dir))
            os.symlink(self.global_license_file, os.path.join(
                self.prefix, vtune_amplifier_dir, "license.lic"))

        if (spec.satisfies('+all') or spec.satisfies('+mpi')) and \
                spec.satisfies('@cluster'):
            for ifile in os.listdir(os.path.join(self.prefix, "itac")):
                if os.path.isdir(os.path.join(self.prefix, "itac", ifile)):
                    os.symlink(self.global_license_file,
                               os.path.join(self.prefix, "itac", ifile,
                                            "license.lic"))
                if os.path.isdir(os.path.join(self.prefix, "itac",
                                              ifile, "intel64")):
                    os.symlink(self.global_license_file,
                               os.path.join(self.prefix, "itac",
                                            ifile, "intel64",
                                            "license.lic"))
            if spec.satisfies('~newdtags'):
                wrappers = ["mpif77", "mpif77", "mpif90", "mpif90",
                            "mpigcc", "mpigcc", "mpigxx", "mpigxx",
                            "mpiicc", "mpiicc", "mpiicpc", "mpiicpc",
                            "mpiifort", "mpiifort"]
                wrapper_paths = []
                for root, dirs, files in os.walk(spec.prefix):
                    for name in files:
                        if name in wrappers:
                            wrapper_paths.append(os.path.join(spec.prefix,
                                                              root, name))
                for wrapper in wrapper_paths:
                    filter_file(r'-Xlinker --enable-new-dtags', r' ',
                                wrapper)

        if spec.satisfies('+rpath'):
            for compiler_command in ["icc", "icpc", "ifort"]:
                cfgfilename = os.path.join(absbindir, "%s.cfg" %
                                           compiler_command)
                with open(cfgfilename, "w") as f:
                    f.write('-Xlinker -rpath -Xlinker %s\n' % abslibdir)

        os.symlink(os.path.join(self.prefix.man, "common", "man1"),
                   os.path.join(self.prefix.man, "man1"))