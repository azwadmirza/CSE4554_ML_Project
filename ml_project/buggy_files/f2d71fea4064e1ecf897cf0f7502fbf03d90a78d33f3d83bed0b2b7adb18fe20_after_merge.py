    def generate_pbx_build_file(self):
        self.ofile.write('\n/* Begin PBXBuildFile section */\n')
        templ = '%s /* %s */ = { isa = PBXBuildFile; fileRef = %s /* %s */; settings = { COMPILER_FLAGS = "%s"; }; };\n'
        otempl = '%s /* %s */ = { isa = PBXBuildFile; fileRef = %s /* %s */;};\n'

        for t in self.build.targets.values():

            for dep in t.get_external_deps():
                if isinstance(dep, dependencies.AppleFrameworks):
                    for f in dep.frameworks:
                        self.write_line('%s /* %s.framework in Frameworks */ = {isa = PBXBuildFile; fileRef = %s /* %s.framework */; };\n' % (self.native_frameworks[f], f, self.native_frameworks_fileref[f], f))

            for s in t.sources:
                if isinstance(s, mesonlib.File):
                    s = os.path.join(s.subdir, s.fname)

                if isinstance(s, str):
                    s = os.path.join(t.subdir, s)
                    idval = self.buildmap[s]
                    fullpath = os.path.join(self.environment.get_source_dir(), s)
                    fileref = self.filemap[s]
                    fullpath2 = fullpath
                    compiler_args = ''
                    self.write_line(templ % (idval, fullpath, fileref, fullpath2, compiler_args))
            for o in t.objects:
                o = os.path.join(t.subdir, o)
                idval = self.buildmap[o]
                fileref = self.filemap[o]
                fullpath = os.path.join(self.environment.get_source_dir(), o)
                fullpath2 = fullpath
                self.write_line(otempl % (idval, fullpath, fileref, fullpath2))
        self.ofile.write('/* End PBXBuildFile section */\n')