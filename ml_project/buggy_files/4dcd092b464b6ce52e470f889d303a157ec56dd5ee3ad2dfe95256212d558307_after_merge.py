    def get_ethtool_macro():
        # see: https://github.com/giampaolo/psutil/issues/659
        from distutils.unixccompiler import UnixCCompiler
        from distutils.errors import CompileError

        with tempfile.NamedTemporaryFile(
                suffix='.c', delete=False, mode="wt") as f:
            f.write("#include <linux/ethtool.h>")

        @atexit.register
        def on_exit():
            try:
                os.remove(f.name)
            except OSError:
                pass

        compiler = UnixCCompiler()
        try:
            with silenced_output('stderr'):
                with silenced_output('stdout'):
                    compiler.compile([f.name])
        except CompileError:
            return ("PSUTIL_ETHTOOL_MISSING_TYPES", 1)
        else:
            return None