    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        items = [
            cleaned_input.get("page"),
            cleaned_input.get("collection"),
            cleaned_input.get("url"),
            cleaned_input.get("category"),
        ]
        items = [item for item in items if item is not None]
        if len(items) > 1:
            raise ValidationError({"items": "More than one item provided."})
        return cleaned_input