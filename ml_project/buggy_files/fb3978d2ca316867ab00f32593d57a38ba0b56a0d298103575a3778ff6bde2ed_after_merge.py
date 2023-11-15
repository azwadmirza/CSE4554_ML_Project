def init():
    '''Return True if the plugin has loaded successfully.'''
    global got_docutils
    if import_ok: # Fix #734.
        if not got_docutils:
            g.es_print('Warning: viewrendered2.py running without docutils.')
        g.plugin_signon(__name__)
        g.registerHandler('after-create-leo-frame', onCreate)
        g.registerHandler('scrolledMessage', show_scrolled_message)
        return True
    return False