    def target_metric_from_git_history(self, hash, symlink_content, target, settings):
        cache_rel_to_data = os.path.relpath(settings.config.cache_dir, settings.config.data_dir)
        common_prefix = os.path.commonprefix([symlink_content, cache_rel_to_data])
        cache_file_name = symlink_content[len(common_prefix):]
        if cache_file_name[0] == os.path.sep:
            cache_file_name = cache_file_name[1:]

        file_name = os.path.join(settings.config.cache_dir, cache_file_name)
        full_file_name = os.path.join(self.git_dir_abs, file_name)

        if os.path.exists(full_file_name):
            lines = open(full_file_name).readlines(2)
            if len(lines) != 1:
                msg = '[dvc-git] Target file {} with hash {} has wrong format: {} lines were obtained, 1 expected.'
                Logger.warn(msg.format(target, hash, len(lines)))
            else:
                return float(lines[0])

        return None