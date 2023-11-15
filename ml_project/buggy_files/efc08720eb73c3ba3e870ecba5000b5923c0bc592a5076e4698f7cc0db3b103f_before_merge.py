def get_printout(out, opts=None, **kwargs):
    '''
    Return a printer function
    '''
    if opts is None:
        opts = {}

    if 'output' in opts:
        # new --out option
        out = opts['output']

    if out == 'text':
        out = 'txt'
    elif out is None or out == '':
        out = 'nested'
    if opts.get('progress', False):
        out = 'progress'

    opts.update(kwargs)
    if 'color' not in opts:
        def is_pipe():
            '''
            Check if sys.stdout is a pipe or not
            '''
            try:
                fileno = sys.stdout.fileno()
            except AttributeError:
                fileno = -1  # sys.stdout is StringIO or fake
            return not os.isatty(fileno)

        if opts.get('force_color', False):
            opts['color'] = True
        elif opts.get('no_color', False) or is_pipe() or salt.utils.is_windows():
            opts['color'] = False
        else:
            opts['color'] = True

    outputters = salt.loader.outputters(opts)
    if out not in outputters:
        # Since the grains outputter was removed we don't need to fire this
        # error when old minions are asking for it
        if out != 'grains':
            log.error('Invalid outputter {0} specified, fall back to nested'.format(out))
        return outputters['nested']
    return outputters[out]