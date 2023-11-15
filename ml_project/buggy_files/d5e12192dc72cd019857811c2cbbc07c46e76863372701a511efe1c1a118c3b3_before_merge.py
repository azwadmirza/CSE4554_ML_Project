def download(datapath):
    model_name = 'pretrained_transformers'
    mdir = os.path.join(get_model_dir(datapath), model_name)
    version = 'v2.0'
    if not built(mdir, version):
        opt = {'datapath': datapath}
        fnames = ['pretrained_transformers.tgz']
        download_models(opt, fnames, model_name, version=version, use_model_type=False)