    def run(self):
        with DvcLock(self.is_locker, self.git):
            cmd = [self.parsed_args.command] + self.parsed_args.args
            data_items_from_args, not_data_items_from_args = self.argv_files_by_type(cmd)
            return self.run_and_commit_if_needed(cmd,
                                                 data_items_from_args,
                                                 not_data_items_from_args,
                                                 self.parsed_args.stdout,
                                                 self.parsed_args.stderr,
                                                 self.parsed_args.shell)
        pass