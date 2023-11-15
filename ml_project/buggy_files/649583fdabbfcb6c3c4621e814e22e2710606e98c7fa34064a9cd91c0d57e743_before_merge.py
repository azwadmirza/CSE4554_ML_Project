def vb_get_manager():
    '''
    Creates a 'singleton' manager to communicate with a local virtualbox hypervisor.
    @return:
    @rtype: VirtualBoxManager
    '''
    global _virtualboxManager
    if _virtualboxManager is None and HAS_LIBS:
        try:
            from importlib import reload
        except ImportError:
            # If we get here, we are in py2 and reload is a built-in.
            pass

        # Reloading the API extends sys.paths for subprocesses of multiprocessing, since they seem to share contexts
        reload(vboxapi)
        _virtualboxManager = vboxapi.VirtualBoxManager(None, None)

    return _virtualboxManager