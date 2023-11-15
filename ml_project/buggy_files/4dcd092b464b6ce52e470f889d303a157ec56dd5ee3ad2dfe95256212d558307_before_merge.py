    def get_ethtool_macro():
        # see: https://github.com/giampaolo/psutil/issues/659
        from distutils.unixccompiler import UnixCCompiler
        from distutils.errors import CompileError
        with tempfile.NamedTemporaryFile(
                suffix='.c', delete=False, mode="wt") as f:
            f.write("#include <linux/ethtool.h>")
        atexit.register(os.remove, f.name)
        compiler = UnixCCompiler()
        try:
            with captured_output('stderr'):
                with captured_output('stdout'):
                    compiler.compile([f.name])
        except CompileError:
            return ("PSUTIL_ETHTOOL_MISSING_TYPES", 1)
        else:
            return None