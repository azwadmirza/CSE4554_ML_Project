def run_hooks(conf, name):
    if conf.has_option('hooks', name):
        pre_import = [
            t.strip() for t in conf.get('hooks', name).split(',')
        ]
        if pre_import is not None:
            for hook in pre_import:
                exit_code = subprocess.call(hook, shell=True)
                if exit_code is not 0:
                    msg = 'Non-zero exit code %d on hook %s' % (
                        exit_code, hook
                    )
                    log.error(msg)
                    raise RuntimeError(msg)