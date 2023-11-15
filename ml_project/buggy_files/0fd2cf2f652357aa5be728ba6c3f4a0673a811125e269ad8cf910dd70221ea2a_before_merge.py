    def _progress_ret(self, progress, out):
        '''
        Print progress events
        '''
        import salt.output
        # Get the progress bar
        if not hasattr(self, 'progress_bar'):
            self.progress_bar = salt.output.get_progress(self.config, out, progress)
        salt.output.update_progress(self.config, progress, self.progress_bar, out)