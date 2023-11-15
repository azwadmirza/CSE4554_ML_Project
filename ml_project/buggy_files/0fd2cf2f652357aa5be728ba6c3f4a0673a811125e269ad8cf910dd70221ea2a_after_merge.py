    def _progress_ret(self, progress, out):
        '''
        Print progress events
        '''
        import salt.output
        # Get the progress bar
        if not hasattr(self, 'progress_bar'):
            try:
                self.progress_bar = salt.output.get_progress(self.config, out, progress)
            except Exception as exc:
                raise salt.exceptions.LoaderError('\nWARNING: Install the `progressbar` python package. '
                                                  'Requested job was still run but output cannot be displayed.\n')
        salt.output.update_progress(self.config, progress, self.progress_bar, out)