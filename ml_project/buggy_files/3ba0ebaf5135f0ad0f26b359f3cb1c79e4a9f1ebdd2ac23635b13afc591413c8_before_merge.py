    def handle_hover_response(self, contents):
        text = contents['params']
        self.sig_display_signature.emit(text)
        self.show_calltip(_("Hint"), text, at_point=self.mouse_point)