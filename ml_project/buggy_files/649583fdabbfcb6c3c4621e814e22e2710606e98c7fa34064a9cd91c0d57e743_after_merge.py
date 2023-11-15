def vb_get_manager():
    '''
    Creates a 'singleton' manager to communicate with a local virtualbox hypervisor.
    @return:
    @rtype: VirtualBoxManager
    '''
    global _virtualboxManager
    if _virtualboxManager is None and HAS_LIBS:
        reload(vboxapi)
        _virtualboxManager = vboxapi.VirtualBoxManager(None, None)

    return _virtualboxManager