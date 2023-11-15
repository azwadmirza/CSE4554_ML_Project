    def run(self, dry=False):
        if self.locked:
            msg = u'Verifying outputs in locked stage \'{}\''
            self.project.logger.info(msg.format(self.relpath))
            if not dry:
                self.check_missing_outputs()
        elif self.is_import:
            msg = u'Importing \'{}\' -> \'{}\''
            self.project.logger.info(msg.format(self.deps[0].path,
                                                self.outs[0].path))

            if not dry:
                self.deps[0].download(self.outs[0].path_info)
        elif self.is_data_source:
            msg = u'Verifying data sources in \'{}\''.format(self.relpath)
            self.project.logger.info(msg)
            if not dry:
                self.check_missing_outputs()
        else:
            msg = u'Running command:\n\t{}'.format(self.cmd)
            self.project.logger.info(msg)

            if not dry:
                self._check_missing_deps()
                executable = os.getenv('SHELL') if os.name != 'nt' else None
                p = subprocess.Popen(self.cmd,
                                     cwd=self.cwd,
                                     shell=True,
                                     env=fix_env(os.environ),
                                     executable=executable)
                p.communicate()
                if p.returncode != 0:
                    raise StageCmdFailedError(self)

        if not dry:
            self.save()