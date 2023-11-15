    def dump(self):
        fname = self.path

        self._check_dvc_filename(fname)

        logger.info(
            "Saving information to '{file}'.".format(
                file=os.path.relpath(fname)
            )
        )
        d = self.dumpd()
        apply_diff(d, self._state)
        dump_stage_file(fname, self._state)

        self.repo.scm.track_file(os.path.relpath(fname))