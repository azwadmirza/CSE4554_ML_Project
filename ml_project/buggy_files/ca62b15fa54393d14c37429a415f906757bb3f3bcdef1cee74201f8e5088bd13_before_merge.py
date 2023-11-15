def prep_trans_tar(file_client, chunks, file_refs, pillar=None):
    '''
    Generate the execution package from the saltenv file refs and a low state
    data structure
    '''
    gendir = tempfile.mkdtemp()
    trans_tar = salt.utils.mkstemp()
    lowfn = os.path.join(gendir, 'lowstate.json')
    pillarfn = os.path.join(gendir, 'pillar.json')
    sync_refs = [
            ['salt://_modules'],
            ['salt://_states'],
            ['salt://_grains'],
            ['salt://_renderers'],
            ['salt://_returners'],
            ['salt://_outputters'],
            ['salt://_utils'],
            ]
    with salt.utils.fopen(lowfn, 'w+') as fp_:
        fp_.write(json.dumps(chunks))
    if pillar:
        with salt.utils.fopen(pillarfn, 'w+') as fp_:
            fp_.write(json.dumps(pillar))
    for saltenv in file_refs:
        file_refs[saltenv].extend(sync_refs)
        env_root = os.path.join(gendir, saltenv)
        if not os.path.isdir(env_root):
            os.makedirs(env_root)
        for ref in file_refs[saltenv]:
            for name in ref:
                short = name[7:]
                path = file_client.cache_file(name, saltenv)
                if path:
                    tgt = os.path.join(env_root, short)
                    tgt_dir = os.path.dirname(tgt)
                    if not os.path.isdir(tgt_dir):
                        os.makedirs(tgt_dir)
                    shutil.copy(path, tgt)
                    continue
                files = file_client.cache_dir(name, saltenv)
                if files:
                    for filename in files:
                        fn = filename[filename.find(short) + len(short):]
                        if fn.startswith('/'):
                            fn = fn.strip('/')
                        tgt = os.path.join(
                                env_root,
                                short,
                                fn,
                                )
                        tgt_dir = os.path.dirname(tgt)
                        if not os.path.isdir(tgt_dir):
                            os.makedirs(tgt_dir)
                        shutil.copy(filename, tgt)
                    continue
    cwd = os.getcwd()
    os.chdir(gendir)
    with closing(tarfile.open(trans_tar, 'w:gz')) as tfp:
        for root, dirs, files in os.walk(gendir):
            for name in files:
                full = os.path.join(root, name)
                tfp.add(full[len(gendir):].lstrip(os.sep))
    os.chdir(cwd)
    shutil.rmtree(gendir)
    return trans_tar