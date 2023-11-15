def _get_notifier():
    '''
    Check the context for the notifier and construct it if not present
    '''
    if 'inotify.notifier' in __context__:
        return __context__['inotify.notifier']
    __context__['inotify.que'] = collections.deque()
    wm = pyinotify.WatchManager()
    __context__['inotify.notifier'] = pyinotify.Notifier(wm, _enqueue)
    return __context__['inotify.notifier']