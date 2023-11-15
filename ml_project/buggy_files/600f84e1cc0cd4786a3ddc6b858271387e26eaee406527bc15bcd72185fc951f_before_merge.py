def load_ipython_extension(ip):
    """Load the extension in IPython."""
    import IPython

    global _loaded
    # Use extension manager to track loaded status if available
    # This is currently in IPython 0.14.dev
    if hasattr(ip.extension_manager, 'loaded'):
        loaded = 'sympy.interactive.ipythonprinting' not in ip.extension_manager.loaded
    else:
        loaded = _loaded

    if not loaded:
        init_printing(ip=ip)
        _loaded = True