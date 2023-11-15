    def handle_msg(self, message):
        """Handle one message"""
        msg_type, _id, file, msg = [
            message[k] for k in ('type', 'id', 'file', 'msg')]
        logger.debug(u'Got request id {0}: {1} for file {2}'.format(
            _id, msg_type, file))
        if msg_type == LSPRequestTypes.DOCUMENT_DID_OPEN:
            self.file_tokens[file] = {
                'text': msg['text'],
                'offset': msg['offset'],
                'language': msg['language'],
            }
        elif msg_type == LSPRequestTypes.DOCUMENT_DID_CHANGE:
            if file not in self.file_tokens:
                self.file_tokens[file] = {
                    'text': '',
                    'offset': msg['offset'],
                    'language': msg['language'],
                }
            diff = msg['diff']
            text = self.file_tokens[file]
            text['offset'] = msg['offset']
            text, _ = self.diff_patch.patch_apply(
                diff, text['text'])
            self.file_tokens[file]['text'] = text
        elif msg_type == LSPRequestTypes.DOCUMENT_DID_CLOSE:
            self.file_tokens.pop(file, {})
        elif msg_type == LSPRequestTypes.DOCUMENT_COMPLETION:
            tokens = []
            if file in self.file_tokens:
                text_info = self.file_tokens[file]
                tokens = self.tokenize(
                    text_info['text'],
                    text_info['offset'],
                    text_info['language'])
            tokens = {'params': tokens}
            self.sig_set_tokens.emit(_id, tokens)