    def run(self):
        if not self.skip_git_actions and not self.git.is_ready_to_go():
            return 1

        data_dir_path = self.get_not_existing_dir(self.parsed_args.data_dir)
        cache_dir_path = self.get_not_existing_dir(self.parsed_args.cache_dir)
        state_dir_path = self.get_not_existing_dir(self.parsed_args.state_dir)

        conf_file_name = self.get_not_existing_conf_file_name()

        data_dir_path.mkdir()
        cache_dir_path.mkdir()
        state_dir_path.mkdir()
        Logger.info('Directories {}/, {}/ and {}/ were created'.format(
            data_dir_path.name,
            cache_dir_path.name,
            state_dir_path.name))

        data_empty_file = os.path.join(self.parsed_args.data_dir, self.EMPTY_FILE_NAME)
        cache_empty_file = os.path.join(self.parsed_args.cache_dir, self.EMPTY_FILE_NAME)
        state_empty_file = os.path.join(self.parsed_args.state_dir, self.EMPTY_FILE_NAME)

        open(data_empty_file, 'w').close()
        open(cache_empty_file, 'w').close()
        open(state_empty_file, 'w').close()

        Logger.info('Empty files {}, {} and {} were created'.format(
            data_empty_file,
            cache_empty_file,
            state_empty_file))

        conf_file = open(conf_file_name, 'wt')
        conf_file.write(self.CONFIG_TEMPLATE.format(data_dir_path.name,
                                                    cache_dir_path.name,
                                                    state_dir_path.name))
        conf_file.close()

        message = 'DVC init. data dir {}, cache dir {}, state dir {}'.format(
                        data_dir_path.name,
                        cache_dir_path.name,
                        state_dir_path.name
        )
        if self.commit_if_needed(message) == 1:
            return 1

        self.modify_gitignore(cache_dir_path.name)
        return self.commit_if_needed('DVC init. Commit .gitignore file')