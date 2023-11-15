def run_hooks(conf, name):
    if conf.has_option('hooks', name):
        pre_import = aslist(conf.get('hooks', name))
        if pre_import is not None:
            for hook in pre_import:
                exit_code = subprocess.call(hook, shell=True)
                if exit_code is not 0:
                    msg = 'Non-zero exit code %d on hook %s' % (
                        exit_code, hook
                    )
                    log.error(msg)
                    raise RuntimeError(msg)