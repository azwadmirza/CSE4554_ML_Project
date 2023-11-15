    def document_did_close(self, params):
        file_signal = params['signal']
        debug_print('[{0}] File: {1}'.format(
            LSPRequestTypes.DOCUMENT_DID_CLOSE, params['file']))
        filename = path_as_uri(params['file'])

        params = {
            'textDocument': {
                'uri': filename
            }
        }
        if filename not in self.watched_files:
            params[ClientConstants.CANCEL] = True
        else:
            editors = self.watched_files[filename]
            idx = -1
            for i, signal in enumerate(editors):
                if id(file_signal) == id(signal):
                    idx = i
                    break
            if idx > 0:
                editors.pop(idx)

            if len(editors) == 0:
                self.watched_files.pop(filename)
        return params