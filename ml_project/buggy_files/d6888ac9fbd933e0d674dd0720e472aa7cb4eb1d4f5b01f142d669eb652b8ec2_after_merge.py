    def eval_custom_target_command(self, target, absolute_paths=False):
        if not absolute_paths:
            ofilenames = [os.path.join(self.get_target_dir(target), i) for i in target.output]
        else:
            ofilenames = [os.path.join(self.environment.get_build_dir(), self.get_target_dir(target), i) \
                          for i in target.output]
        srcs = []
        outdir = self.get_target_dir(target)
        # Many external programs fail on empty arguments.
        if outdir == '':
            outdir = '.'
        if absolute_paths:
            outdir = os.path.join(self.environment.get_build_dir(), outdir)
        for i in target.get_sources():
            if hasattr(i, 'held_object'):
                i = i.held_object
            if isinstance(i, str):
                fname = [os.path.join(self.build_to_src, target.subdir, i)]
            elif isinstance(i, build.BuildTarget):
                fname = [self.get_target_filename(i)]
            elif isinstance(i, build.CustomTarget):
                fname = [os.path.join(self.get_target_dir(i), p) for p in i.get_outputs()]
            elif isinstance(i, build.GeneratedList):
                fname = [os.path.join(self.get_target_private_dir(target), p) for p in i.get_outputs()]
            else:
                fname = [i.rel_to_builddir(self.build_to_src)]
            if absolute_paths:
                fname =[os.path.join(self.environment.get_build_dir(), f) for f in fname]
            srcs += fname
        cmd = []
        for i in target.command:
            if isinstance(i, build.Executable):
                cmd += self.exe_object_to_cmd_array(i)
                continue
            elif isinstance(i, build.CustomTarget):
                # GIR scanner will attempt to execute this binary but
                # it assumes that it is in path, so always give it a full path.
                tmp = i.get_outputs()[0]
                i = os.path.join(self.get_target_dir(i), tmp)
            elif isinstance(i, mesonlib.File):
                i = i.rel_to_builddir(self.build_to_src)
                if absolute_paths:
                    i = os.path.join(self.environment.get_build_dir(), i)
            # FIXME: str types are blindly added and ignore the 'absolute_paths' argument
            elif not isinstance(i, str):
                err_msg = 'Argument {0} is of unknown type {1}'
                raise RuntimeError(err_msg.format(str(i), str(type(i))))
            for (j, src) in enumerate(srcs):
                i = i.replace('@INPUT%d@' % j, src)
            for (j, res) in enumerate(ofilenames):
                i = i.replace('@OUTPUT%d@' % j, res)
            if '@INPUT@' in i:
                msg = 'Custom target {} has @INPUT@ in the command, but'.format(target.name)
                if len(srcs) == 0:
                    raise MesonException(msg + ' no input files')
                if i == '@INPUT@':
                    cmd += srcs
                    continue
                else:
                    if len(srcs) > 1:
                        raise MesonException(msg + ' more than one input file')
                    i = i.replace('@INPUT@', srcs[0])
            elif '@OUTPUT@' in i:
                msg = 'Custom target {} has @OUTPUT@ in the command, but'.format(target.name)
                if len(ofilenames) == 0:
                    raise MesonException(msg + ' no output files')
                if i == '@OUTPUT@':
                    cmd += ofilenames
                    continue
                else:
                    if len(ofilenames) > 1:
                        raise MesonException(msg + ' more than one output file')
                    i = i.replace('@OUTPUT@', ofilenames[0])
            elif '@OUTDIR@' in i:
                i = i.replace('@OUTDIR@', outdir)
            elif '@DEPFILE@' in i:
                if target.depfile is None:
                    msg = 'Custom target {!r} has @DEPFILE@ but no depfile ' \
                          'keyword argument.'.format(target.name)
                    raise MesonException(msg)
                dfilename = os.path.join(outdir, target.depfile)
                i = i.replace('@DEPFILE@', dfilename)
            elif '@PRIVATE_OUTDIR_' in i:
                match = re.search('@PRIVATE_OUTDIR_(ABS_)?([^\/\s*]*)@', i)
                if not match:
                    msg = 'Custom target {!r} has an invalid argument {!r}' \
                          ''.format(target.name, i)
                    raise MesonException(msg)
                source = match.group(0)
                if match.group(1) is None and not absolute_paths:
                    lead_dir = ''
                else:
                    lead_dir = self.environment.get_build_dir()
                i = i.replace(source,
                              os.path.join(lead_dir,
                                           outdir))
            cmd.append(i)
        # This should not be necessary but removing it breaks
        # building GStreamer on Windows. The underlying issue
        # is problems with quoting backslashes on Windows
        # which is the seventh circle of hell. The downside is
        # that this breaks custom targets whose command lines
        # have backslashes. If you try to fix this be sure to
        # check that it does not break GST.
        #
        # The bug causes file paths such as c:\foo to get escaped
        # into c:\\foo.
        #
        # Unfortunately we have not been able to come up with an
        # isolated test case for this so unless you manage to come up
        # with one, the only way is to test the building with Gst's
        # setup. Note this in your MR or ping us and we will get it
        # fixed.
        #
        # https://github.com/mesonbuild/meson/pull/737
        cmd = [i.replace('\\', '/') for i in cmd]
        return (srcs, ofilenames, cmd)