def _process_config(config, cache, output, requester):
    try:
        if config.type == "git":
            _process_git_repo(config, cache, output)
        elif config.type == "dir":
            _process_folder(config, config.uri, cache, output)
        elif config.type == "file":
            with tmp_config_install_folder(cache) as tmp_folder:
                _process_zip_file(config, config.uri, cache, output, tmp_folder)
        elif config.type == "url":
            _process_download(config, cache, output, requester=requester)
        else:
            raise ConanException("Unable to process config install: %s" % config.uri)
    except Exception as e:
        raise ConanException("Failed conan config install: %s" % str(e))