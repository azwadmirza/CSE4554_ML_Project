    def get_top(self):
        '''
        Returns the high data derived from the top file
        '''
        try:
            tops = self.get_tops()
        except SaltRenderError as err:
            log.error('Unable to render top file: ' + str(err.error))
            return {}
        return self.merge_tops(tops)