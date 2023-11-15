    def write_buildinfo(self):
        # type: () -> None
        # write build info file
        try:
            with open(path.join(self.outdir, '.buildinfo'), 'w') as fp:
                fp.write('# Sphinx build info version 1\n'
                         '# This file hashes the configuration used when building'
                         ' these files. When it is not found, a full rebuild will'
                         ' be done.\nconfig: %s\ntags: %s\n' %
                         (self.config_hash, self.tags_hash))
        except IOError as exc:
            logger.warning('Failed to write build info file: %r', exc)