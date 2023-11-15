def main():
    # Remove this module's path from sys.path:
    try:
        sys.path.remove(osp.dirname(__file__))
    except ValueError:
        pass

    try:
        locals().pop('__file__')
    except KeyError:
        pass
    __doc__ = ''
    __name__ = '__main__'

    # Add current directory to sys.path (like for any standard Python interpreter
    # executed in interactive mode):
    sys.path.insert(0, '')

    # Fire up the kernel instance.
    from ipykernel.kernelapp import IPKernelApp

    if not IS_EXT_INTERPRETER:
        from spyder.utils.ipython.spyder_kernel import SpyderKernel
    else:
        # We add "spyder" to sys.path for external interpreters,
        # so this works!
        # See create_kernel_spec of plugins/ipythonconsole
        from utils.ipython.spyder_kernel import SpyderKernel

    kernel = IPKernelApp.instance()
    kernel.kernel_class = SpyderKernel
    try:
        kernel.config = kernel_config()
    except:
        pass
    kernel.initialize()

    # NOTE: Leave this and other magic modifications *after* setting
    # __ipythonkernel__ to not have problems while starting kernels
    kernel.shell.register_magic_function(varexp)

    # Start the (infinite) kernel event loop.
    kernel.start()