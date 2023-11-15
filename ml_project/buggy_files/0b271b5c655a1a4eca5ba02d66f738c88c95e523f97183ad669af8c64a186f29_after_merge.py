    def run(self, edit: sublime.Edit, event: 'Optional[dict]' = None) -> None:
        client = self.client_with_capability('referencesProvider')
        if client:
            pos = get_position(self.view, event)
            window = self.view.window()
            self.word_region = self.view.word(pos)
            self.word = self.view.substr(self.word_region)

            # use relative paths if file on the same root.
            base_dir = windows.lookup(window).get_project_path()
            if base_dir:
                if os.path.commonprefix([base_dir, self.view.file_name()]):
                    self.base_dir = base_dir

            document_position = get_document_position(self.view, pos)
            if document_position:
                document_position['context'] = {
                    "includeDeclaration": False
                }
                request = Request.references(document_position)
                client.send_request(
                    request, lambda response: self.handle_response(response, pos))