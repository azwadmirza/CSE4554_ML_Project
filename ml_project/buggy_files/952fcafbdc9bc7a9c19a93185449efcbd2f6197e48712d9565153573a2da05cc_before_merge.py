def revert_to_snapshot(name, kwargs=None, call=None):
    '''
    Revert virtual machine to it's current snapshot. If no snapshot
    exists, the state of the virtual machine remains unchanged

    .. note::

        The virtual machine will be powered on if the power state of
        the snapshot when it was created was set to "Powered On". Set
        ``power_off=True`` so that the virtual machine stays powered
        off regardless of the power state of the snapshot when it was
        created. Default is ``power_off=False``.

        If the power state of the snapshot when it was created was
        "Powered On" and if ``power_off=True``, the VM will be put in
        suspended state after it has been reverted to the snapshot.

    CLI Example:

    .. code-block:: bash

        salt-cloud -a revert_to_snapshot vmame [power_off=True]
    '''
    if call != 'action':
        raise SaltCloudSystemExit(
            'The revert_to_snapshot action must be called with '
            '-a or --action.'
        )

    suppress_power_on = _str_to_bool(kwargs.get('power_off', False))

    vm_ref = _get_mor_by_property(vim.VirtualMachine, name)

    if not vm_ref.rootSnapshot:
        log.error('VM {0} does not contain any current snapshots'.format(name))
        return 'revert failed'

    try:
        task = vm_ref.RevertToCurrentSnapshot(suppressPowerOn=suppress_power_on)
        _wait_for_task(task, name, "revert to snapshot", 5, 'info')

    except Exception as exc:
        log.error(
            'Error while reverting VM {0} to snapshot: {1}'.format(
                name,
                exc
            ),
            # Show the traceback if the debug logging level is enabled
            exc_info_on_loglevel=logging.DEBUG
        )
        return 'revert failed'

    return 'reverted to current snapshot'