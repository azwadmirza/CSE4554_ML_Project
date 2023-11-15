    def get_searchable_content(self, value):
        # Return the display value as the searchable value
        text_value = force_text(value)
        for k, v in self.field.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == force_text(k2):
                        return [k, v2]
            else:
                if value == k or text_value == force_text(k):
                    return [v]
        return []  # Value was not found in the list of choices