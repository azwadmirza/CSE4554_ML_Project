def _enqueue(revent):
    '''
    Enqueue the event
    '''
    __context__['inotify.que'].append(revent)