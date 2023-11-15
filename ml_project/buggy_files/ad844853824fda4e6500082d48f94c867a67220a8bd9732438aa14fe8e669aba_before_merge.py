def compile_device_template(pyfunc, debug=False, inline=False, opt=True):
    """Create a DeviceFunctionTemplate object and register the object to
    the CUDA typing context.
    """
    from .descriptor import CUDATargetDesc

    dft = DeviceFunctionTemplate(pyfunc, debug=debug, inline=inline, opt=opt)

    class device_function_template(AbstractTemplate):
        key = dft

        def generic(self, args, kws):
            assert not kws
            return dft.compile(args).signature

        def get_template_info(cls):
            basepath = os.path.dirname(os.path.dirname(numba.__file__))
            code, firstlineno = inspect.getsourcelines(pyfunc)
            path = inspect.getsourcefile(pyfunc)
            sig = str(utils.pysignature(pyfunc))
            info = {
                'kind': "overload",
                'name': getattr(cls.key, '__name__', "unknown"),
                'sig': sig,
                'filename': utils.safe_relpath(path, start=basepath),
                'lines': (firstlineno, firstlineno + len(code) - 1),
                'docstring': pyfunc.__doc__
            }
            return info

    typingctx = CUDATargetDesc.typingctx
    typingctx.insert_user_function(dft, device_function_template)
    return dft