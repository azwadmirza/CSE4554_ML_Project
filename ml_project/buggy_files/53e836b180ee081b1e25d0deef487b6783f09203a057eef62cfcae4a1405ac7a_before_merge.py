    def show_calltip(self, signature, parameter=None):
        """
        Show calltip.

        Calltips look like tooltips but will not disappear if mouse hovers
        them. They are useful for displaying signature information on methods
        and functions.
        """
        # Find position of calltip
        point = self._calculate_position()

        # Format signature
        html_signature = self._format_signature(
            signature=signature,
            parameter=parameter,
        )

        inspect_word = signature.split('(')[0]
        text = self._format_text(
            signature=html_signature,
            inspect_word=inspect_word,
            display_link=False,
        )

        self._update_stylesheet(self.calltip_widget)

        # Show calltip
        self.calltip_widget.show_tip(point, text, [])
        self.calltip_widget.show()