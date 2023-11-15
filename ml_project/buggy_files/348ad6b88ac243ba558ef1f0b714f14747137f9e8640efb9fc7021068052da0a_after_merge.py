    def parse_lsp_config(self, config):
        """Parse and load LSP server editor capabilities."""
        sync_options = config['textDocumentSync']
        completion_options = config['completionProvider']
        signature_options = config['signatureHelpProvider']
        range_formatting_options = config['documentOnTypeFormattingProvider']
        self.open_close_notifications = sync_options.get('openClose', False)
        self.sync_mode = sync_options.get('change', TextDocumentSyncKind.NONE)
        self.will_save_notify = sync_options.get('willSave', False)
        self.will_save_until_notify = sync_options.get('willSaveWaitUntil',
                                                       False)
        self.save_include_text = sync_options['save']['includeText']
        self.enable_hover = config['hoverProvider']
        self.auto_completion_characters = (
            completion_options['triggerCharacters'])
        self.signature_completion_characters = (
            signature_options['triggerCharacters'] + ['='])  # FIXME:
        self.go_to_definition_enabled = config['definitionProvider']
        self.find_references_enabled = config['referencesProvider']
        self.highlight_enabled = config['documentHighlightProvider']
        self.formatting_enabled = config['documentFormattingProvider']
        self.range_formatting_enabled = (
            config['documentRangeFormattingProvider'])
        self.formatting_characters.append(
            range_formatting_options['firstTriggerCharacter'])
        self.formatting_characters += (
            range_formatting_options.get('moreTriggerCharacter', []))