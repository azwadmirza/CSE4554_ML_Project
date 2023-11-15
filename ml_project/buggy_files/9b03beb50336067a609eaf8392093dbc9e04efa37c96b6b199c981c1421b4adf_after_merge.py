    def _fill_template(
        self,
        template: Dict[Text, Any],
        filled_slots: Optional[Dict[Text, Any]] = None,
        **kwargs: Any,
    ) -> Dict[Text, Any]:
        """"Combine slot values and key word arguments to fill templates."""

        # Getting the slot values in the template variables
        template_vars = self._template_variables(filled_slots, kwargs)

        keys_to_interpolate = [
            "text",
            "image",
            "custom",
            "button",
            "attachment",
            "quick_replies",
        ]
        if template_vars:
            for key in keys_to_interpolate:
                if key in template:
                    template[key] = interpolator.interpolate(
                        template[key], template_vars
                    )
        return template