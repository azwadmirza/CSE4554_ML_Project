def _process_folder(config, folder, cache, output):
    if config.source_folder:
        folder = os.path.join(folder, config.source_folder)
    for root, dirs, files in walk(folder):
        dirs[:] = [d for d in dirs if d != ".git"]
        if ".git" in root:
            continue
        for f in files:
            if f == "settings.yml":
                output.info("Installing settings.yml")
                settings_path = cache.settings_path
                shutil.copy(os.path.join(root, f), settings_path)
            elif f == "conan.conf":
                output.info("Processing conan.conf")
                _handle_conan_conf(cache.config, os.path.join(root, f))
            elif f == "remotes.txt":
                output.info("Defining remotes from remotes.txt")
                _handle_remotes(cache, os.path.join(root, f))
            elif f in ("registry.txt", "registry.json"):
                try:
                    os.remove(cache.registry_path)
                except OSError:
                    pass
                finally:
                    shutil.copy(os.path.join(root, f), cache.cache_folder)
                    migrate_registry_file(cache, output)
            elif f == "remotes.json":
                # Fix for Conan 2.0
                raise ConanException("remotes.json install is not supported yet. Use 'remotes.txt'")
            else:
                # This is ugly, should be removed in Conan 2.0
                if root == folder and f in ("README.md", "LICENSE.txt"):
                    output.info("Skip %s" % f)
                    continue
                relpath = os.path.relpath(root, folder)
                if config.target_folder:
                    target_folder = os.path.join(cache.cache_folder, config.target_folder,
                                                 relpath)
                else:
                    target_folder = os.path.join(cache.cache_folder, relpath)
                mkdir(target_folder)
                output.info("Copying file %s to %s" % (f, target_folder))
                shutil.copy(os.path.join(root, f), target_folder)