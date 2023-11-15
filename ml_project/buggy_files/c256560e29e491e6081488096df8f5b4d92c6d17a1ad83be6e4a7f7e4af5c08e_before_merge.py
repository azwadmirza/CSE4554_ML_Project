    def run(self):
        indent = 1 if self.args.cloud else 0
        try:
            st = self.repo.status(
                targets=self.args.targets,
                jobs=self.args.jobs,
                cloud=self.args.cloud,
                remote=self.args.remote,
                all_branches=self.args.all_branches,
                all_tags=self.args.all_tags,
                all_commits=self.args.all_commits,
                with_deps=self.args.with_deps,
                recursive=self.args.recursive,
            )

            if self.args.quiet:
                return bool(st)

            if self.args.show_json:
                import json

                logger.info(json.dumps(st))
            elif st:
                self._show(st, indent)
            elif not self.repo.stages:
                logger.info(self.EMPTY_PROJECT_MSG)
            else:
                logger.info(self.UP_TO_DATE_MSG)

        except DvcException:
            logger.exception("failed to obtain data status")
            return 1
        return 0