def pillars(opts, functions, context=None):
    '''
    Returns the pillars modules
    '''
    ret = LazyLoader(_module_dirs(opts, 'pillar', 'pillar'),
                     opts,
                     tag='pillar',
                     pack={'__salt__': functions,
                           '__context__': context})
    return FilterDictWrapper(ret, '.ext_pillar')