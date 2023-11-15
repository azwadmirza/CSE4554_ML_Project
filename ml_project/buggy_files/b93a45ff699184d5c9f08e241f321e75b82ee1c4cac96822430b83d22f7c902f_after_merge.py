    def get_form_class(cls, model):
        """
        Construct a form class that has all the fields and formsets named in
        the children of this edit handler.
        """
        if cls._form_class is None:
            # If a custom form class was passed to the EditHandler, use it.
            # Otherwise, use the base_form_class from the model.
            # If that is not defined, use WagtailAdminModelForm.
            model_form_class = getattr(model, 'base_form_class', WagtailAdminModelForm)
            base_form_class = cls.base_form_class or model_form_class

            cls._form_class = get_form_for_model(
                model,
                form_class=base_form_class,
                fields=cls.required_fields(),
                formsets=cls.required_formsets(),
                widgets=cls.widget_overrides())
        return cls._form_class