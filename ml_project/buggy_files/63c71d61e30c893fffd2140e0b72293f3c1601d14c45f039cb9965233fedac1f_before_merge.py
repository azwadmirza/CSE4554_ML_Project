    def process(self):
        event = self.receive_message()
        event_dict = event.to_dict(hierarchical=False)

        for field in self.flatten_fields:
            if field in event_dict:
                val = event_dict[field]
                # if it's a string try to parse it as JSON
                if isinstance(val, str):
                    try:
                        val = loads(val)
                    except ValueError:
                        pass
                if isinstance(val, Mapping):
                    for key, value in val.items():
                        event_dict[field + '_' + key] = value
                    event_dict.pop(field)

        # For ES 2.x, replace dots with a specified replacement character
        if self.replacement_char and self.replacement_char != '.':
            event_dict = replace_keys(event_dict,
                                      replacement=self.replacement_char)

        self.es.index(index=self.get_index(event_dict, default_date=datetime.today().date()),
                      doc_type=self.elastic_doctype,
                      body=event_dict)
        self.acknowledge_message()