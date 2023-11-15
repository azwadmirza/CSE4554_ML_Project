def __init__(opts):
    if HAS_BOTO:
        __utils__['boto.assign_funcs'](__name__, 'cfn', module='cloudformation', pack=__salt__)