def beacon(config):
    '''
    Watch the configured files

    Example Config

    .. code-block:: yaml

        beacons:
          inotify:
            /path/to/file/or/dir:
              mask:
                - open
                - create
                - close_write
              recurse: True
              auto_add: True

    The mask list can contain options:
        * access            File was accessed
        * attrib            Metadata changed
        * close_nowrite     Unwrittable file closed
        * close_write       Writtable file was closed
        * create            File created
        * delete            File deleted
        * delete_self       Named file or directory deleted
        * excl_unlink
        * ignored
        * modify            File was modified
        * moved_from        File being watched was moved
        * moved_to          File moved into watched area
        * move_self         Named file was moved
        * oneshot
        * onlydir           Operate only if name is directory
        * open              File was opened
        * unmount           Backing fs was unmounted
    recurse:
      Tell the beacon to recursively watch files in the directory
    auto_add:
      Automatically start adding files that are created in the watched directory
    '''
    ret = []
    notifier = _get_notifier()
    wm = notifier._watch_manager
    # Read in existing events
    # remove watcher files that are not in the config
    # update all existing files with watcher settings
    # return original data
    if notifier.check_events(1):
        notifier.read_events()
        notifier.process_events()
        while __context__['inotify.que']:
            sub = {}
            event = __context__['inotify.que'].popleft()
            sub['tag'] = event.path
            sub['path'] = event.pathname
            sub['change'] = event.maskname
            ret.append(sub)

    current = set()
    for wd in wm.watches:
        current.add(wm.watches[wd].path)
    need = set(config)
    for path in current.difference(need):
        # These need to be removed
        for wd in wm.watches:
            if path == wm.watches[wd].path:
                wm.rm_watch(wd)
    for path in config:
        if isinstance(config[path], dict):
            mask = config[path].get('mask', DEFAULT_MASK)
            if isinstance(mask, list):
                r_mask = 0
                for sub in mask:
                    r_mask |= _get_mask(sub)
            elif isinstance(mask, salt.ext.six.binary_type):
                r_mask = _get_mask(mask)
            else:
                r_mask = mask
            mask = r_mask
            rec = config[path].get('recurse', False)
            auto_add = config[path].get('auto_add', False)
        else:
            mask = DEFAULT_MASK
            rec = False
            auto_add = False
        # TODO: make the config handle more options
        if path not in current:
            wm.add_watch(
                path,
                mask,
                rec=rec,
                auto_add=auto_add)
        else:
            for wd in wm.watches:
                if path == wm.watches[wd].path:
                    update = False
                    if wm.watches[wd].mask != mask:
                        update = True
                    if wm.watches[wd].auto_add != auto_add:
                        update = True
                    if update:
                        wm.update_watch(
                            wd,
                            mask=mask,
                            rec=rec,
                            auto_add=auto_add)
    return ret