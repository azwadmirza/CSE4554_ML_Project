    def show_calltip(self, signature, parameter=None):
        """
        Show calltip.

        Calltips look like tooltips but will not disappear if mouse hovers
        them. They are useful for displaying signature information on methods
        and functions.
        """
        # Find position of calltip
        point = self._calculate_position()

        # Format
        res = self._check_signature_and_format(signature, parameter)
        new_signature, text, inspect_word = res
        text = self._format_text(
            signature=new_signature,
            text=text,
            inspect_word=inspect_word,
            display_link=False,
        )
        self._update_stylesheet(self.calltip_widget)

        # Show calltip
        self.calltip_widget.show_tip(point, text, [])
        self.calltip_widget.show()