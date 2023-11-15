    def request_hover(self, params):
        text = self.opened_files.get(params['file'], "")
        md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
        path = str(params['file'])
        path = path.replace(osp.sep, ':')
        logger.debug(path)
        if os.name == 'nt':
            path = path.replace('::', ':')
            path = 'windows:' + path
        request = {
            'filename': path,
            'hash': md5,
            'cursor_runes': params['offset']
        }
        return None, request