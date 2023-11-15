def clean():
    print('\nRemoving build, dist and egg directories')
    root = os.path.dirname(os.path.realpath(__file__))
    for d in ['build', 'dist', 'leo.egg-info', '.eggs']:
        dpath = os.path.join(root, d)
        if os.path.isdir(dpath):
            rmtree(dpath)