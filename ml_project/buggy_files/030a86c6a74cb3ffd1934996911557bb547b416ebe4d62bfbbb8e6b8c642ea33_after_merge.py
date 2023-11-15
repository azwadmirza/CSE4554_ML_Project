def create_snapshot(name, kwargs=None, call=None):
    '''
    Create a snapshot of the specified virtual machine in this VMware
    environment

    .. note::

        If the VM is powered on, the internal state of the VM (memory
        dump) is included in the snapshot by default which will also set
        the power state of the snapshot to "powered on". You can set
        ``memdump=False`` to override this. This field is ignored if
        the virtual machine is powered off or if the VM does not support
        snapshots with memory dumps. Default is ``memdump=True``

    .. note::

        If the VM is powered on when the snapshot is taken, VMware Tools
        can be used to quiesce the file system in the virtual machine by
        setting ``quiesce=True``. This field is ignored if the virtual
        machine is powered off; if VMware Tools are not available or if
        ``memdump=True``. Default is ``quiesce=False``

    CLI Example:

    .. code-block:: bash

        salt-cloud -a create_snapshot vmname snapshot_name="mySnapshot"
        salt-cloud -a create_snapshot vmname snapshot_name="mySnapshot" [description="My snapshot"] [memdump=False] [quiesce=True]
    '''
    if call != 'action':
        raise SaltCloudSystemExit(
            'The create_snapshot action must be called with '
            '-a or --action.'
        )

    if kwargs is None:
        kwargs = {}

    snapshot_name = kwargs.get('snapshot_name') if kwargs and 'snapshot_name' in kwargs else None

    if not snapshot_name:
        raise SaltCloudSystemExit(
            'You must specify snapshot name for the snapshot to be created.'
        )

    memdump = _str_to_bool(kwargs.get('memdump', True))
    quiesce = _str_to_bool(kwargs.get('quiesce', False))

    vm_ref = _get_mor_by_property(vim.VirtualMachine, name)

    if vm_ref.summary.runtime.powerState != "poweredOn":
        log.debug('VM {0} is not powered on. Setting both memdump and quiesce to False'.format(name))
        memdump = False
        quiesce = False

    if memdump and quiesce:
        # Either memdump or quiesce should be set to True
        log.warning('You can only set either memdump or quiesce to True. Setting quiesce=False')
        quiesce = False

    desc = kwargs.get('description') if 'description' in kwargs else ''

    try:
        task = vm_ref.CreateSnapshot(snapshot_name, desc, memdump, quiesce)
        _wait_for_task(task, name, "create snapshot", 5, 'info')
    except Exception as exc:
        log.error(
            'Error while creating snapshot of {0}: {1}'.format(
                name,
                exc
            ),
            # Show the traceback if the debug logging level is enabled
            exc_info_on_loglevel=logging.DEBUG
        )
        return 'failed to create snapshot'

    return {'Snapshot created successfully': _get_snapshots(vm_ref.snapshot.rootSnapshotList, vm_ref.snapshot.currentSnapshot)}