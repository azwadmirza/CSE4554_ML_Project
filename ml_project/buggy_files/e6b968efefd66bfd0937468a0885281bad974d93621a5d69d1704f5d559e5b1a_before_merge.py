def __init__(opts, pack=None):
    if HAS_BOTO:
        __utils__['boto.assign_funcs'](__name__, 'cfn', module='cloudformation', pack=pack)