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

    The mask list can contain the following events (the default mask is create,
    delete, and modify):
        * access            File accessed
        * attrib            File metadata changed
        * close_nowrite     Unwritable file closed
        * close_write       Writable file closed
        * create            File created in watched directory
        * delete            File deleted from watched directory
        * delete_self       Watched file or directory deleted
        * modify            File modified
        * moved_from        File moved out of watched directory
        * moved_to          File moved into watched directory
        * move_self         Watched file moved
        * open              File opened

    The mask can also contain the following options:
        * dont_follow       Don't dereference symbolic links
        * excl_unlink       Omit events for children after they have been unlinked
        * oneshot           Remove watch after one event
        * onlydir           Operate only if name is directory

    recurse:
      Recursively watch files in the directory
    auto_add:
      Automatically start watching files that are created in the watched directory
    '''
    ret = []
    notifier = _get_notifier()
    wm = notifier._watch_manager

    # Read in existing events
    if notifier.check_events(1):
        notifier.read_events()
        notifier.process_events()
        queue = __context__['inotify.queue']
        while queue:
            event = queue.popleft()
            sub = {'tag': event.path,
                   'path': event.pathname,
                   'change': event.maskname}
            ret.append(sub)

    # Get paths currently being watched
    current = set()
    for wd in wm.watches:
        current.add(wm.watches[wd].path)

    # Update existing watches and add new ones
    # TODO: make the config handle more options
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

        if path in current:
            for wd in wm.watches:
                if path == wm.watches[wd].path:
                    update = False
                    if wm.watches[wd].mask != mask:
                        update = True
                    if wm.watches[wd].auto_add != auto_add:
                        update = True
                    if update:
                        wm.update_watch(wd, mask=mask, rec=rec, auto_add=auto_add)
        else:
            wm.add_watch(path, mask, rec=rec, auto_add=auto_add)

    # Return event data
    return ret