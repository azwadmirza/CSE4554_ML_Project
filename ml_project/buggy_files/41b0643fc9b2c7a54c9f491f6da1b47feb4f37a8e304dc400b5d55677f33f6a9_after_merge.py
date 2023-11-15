    def serialize(self, form):
        data = {}

        for key in form.inputs.keys():
            input = form.inputs[key]
            if getattr(input, 'type', '') == 'submit':
                try:
                    form.remove(input)
                # Issue 595: throws ValueError: Element not child of this node
                except ValueError:
                    pass

        for k, v in form.fields.items():
            if v is None:
                continue

            if isinstance(v, lxml.html.MultipleSelectOptions):
                data[k] = [val for val in v]
            else:
                data[k] = v

        for key in form.inputs.keys():
            input = form.inputs[key]
            if getattr(input, 'type', '') == 'file' and key in data:
                data[key] = open(data[key], 'rb')

        return data