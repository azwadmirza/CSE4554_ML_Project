    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)

        _validate_menu_item_instance(cleaned_input, "page", page_models.Page)
        _validate_menu_item_instance(
            cleaned_input, "collection", product_models.Collection
        )
        _validate_menu_item_instance(cleaned_input, "category", product_models.Category)

        items = [
            cleaned_input.get("page"),
            cleaned_input.get("collection"),
            cleaned_input.get("url"),
            cleaned_input.get("category"),
        ]
        items = [item for item in items if item is not None]
        if len(items) > 1:
            raise ValidationError("More than one item provided.")
        return cleaned_input