def clean():
    print('Removing build and dist directories')
    root = os.path.dirname(os.path.realpath(__file__))
    for d in ['build', 'dist', 'leo.egg-info']:
        dpath = os.path.join(root, d)
        if os.path.isdir(dpath):
            rmtree(dpath)