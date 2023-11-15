    def _generate(self, env):
        mlog.debug('Build started at', datetime.datetime.now().isoformat())
        mlog.debug('Main binary:', sys.executable)
        mlog.debug('Python system:', platform.system())
        mlog.log(mlog.bold('The Meson build system'))
        self.check_pkgconfig_envvar(env)
        mlog.log('Version:', coredata.version)
        mlog.log('Source dir:', mlog.bold(self.source_dir))
        mlog.log('Build dir:', mlog.bold(self.build_dir))
        if env.is_cross_build():
            mlog.log('Build type:', mlog.bold('cross build'))
        else:
            mlog.log('Build type:', mlog.bold('native build'))
        b = build.Build(env)
        if self.options.backend == 'ninja':
            from .backend import ninjabackend
            g = ninjabackend.NinjaBackend(b)
        elif self.options.backend == 'vs':
            from .backend import vs2010backend
            g = vs2010backend.autodetect_vs_version(b)
            env.coredata.set_builtin_option('backend', g.name)
            mlog.log('Auto detected Visual Studio backend:', mlog.bold(g.name))
        elif self.options.backend == 'vs2010':
            from .backend import vs2010backend
            g = vs2010backend.Vs2010Backend(b)
        elif self.options.backend == 'vs2015':
            from .backend import vs2015backend
            g = vs2015backend.Vs2015Backend(b)
        elif self.options.backend == 'vs2017':
            from .backend import vs2017backend
            g = vs2017backend.Vs2017Backend(b)
        elif self.options.backend == 'xcode':
            from .backend import xcodebackend
            g = xcodebackend.XCodeBackend(b)
        else:
            raise RuntimeError('Unknown backend "%s".' % self.options.backend)

        intr = interpreter.Interpreter(b, g)
        if env.is_cross_build():
            mlog.log('Host machine cpu family:', mlog.bold(intr.builtin['host_machine'].cpu_family_method([], {})))
            mlog.log('Host machine cpu:', mlog.bold(intr.builtin['host_machine'].cpu_method([], {})))
            mlog.log('Target machine cpu family:', mlog.bold(intr.builtin['target_machine'].cpu_family_method([], {})))
            mlog.log('Target machine cpu:', mlog.bold(intr.builtin['target_machine'].cpu_method([], {})))
        mlog.log('Build machine cpu family:', mlog.bold(intr.builtin['build_machine'].cpu_family_method([], {})))
        mlog.log('Build machine cpu:', mlog.bold(intr.builtin['build_machine'].cpu_method([], {})))
        intr.run()
        try:
            # We would like to write coredata as late as possible since we use the existence of
            # this file to check if we generated the build file successfully. Since coredata
            # includes settings, the build files must depend on it and appear newer. However, due
            # to various kernel caches, we cannot guarantee that any time in Python is exactly in
            # sync with the time that gets applied to any files. Thus, we dump this file as late as
            # possible, but before build files, and if any error occurs, delete it.
            cdf = env.dump_coredata()
            g.generate(intr)
            dumpfile = os.path.join(env.get_scratch_dir(), 'build.dat')
            with open(dumpfile, 'wb') as f:
                pickle.dump(b, f)
            # Post-conf scripts must be run after writing coredata or else introspection fails.
            g.run_postconf_scripts()
        except:
            os.unlink(cdf)
            raise