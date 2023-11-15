    def parse_line(self, row, report):
        event = self.new_event(report)

        for keygroup, value, required in zip(self.columns, row, self.columns_required):
            keys = keygroup.split('|') if '|' in keygroup else [keygroup, ]
            for key in keys:
                if isinstance(value, str) and not value:  # empty string is never valid
                    break
                regex = self.column_regex_search.get(key, None)
                if regex:
                    search = re.search(regex, value)
                    if search:
                        value = search.group(0)
                    else:
                        value = None

                if key in ["__IGNORE__", ""]:
                    break

                if key in self.data_type:
                    value = DATA_CONVERSIONS[self.data_type[key]](value)

                if key in ["time.source", "time.destination"]:
                    value = TIME_CONVERSIONS[self.time_format](value)
                elif key.endswith('.url'):
                    if not value:
                        continue
                    if '://' not in value:
                        value = self.parameters.default_url_protocol + value
                elif key in ["classification.type"] and self.type_translation:
                    if value in self.type_translation:
                        value = self.type_translation[value]
                    elif not hasattr(self.parameters, 'type'):
                        continue
                if event.add(key, value, raise_failure=False) is not False:
                    break
            else:
                # if the value sill remains unadded we need to inform if the key is needed
                if required:
                    raise InvalidValue(key, value)

        if hasattr(self.parameters, 'type')\
                and "classification.type" not in event:
            event.add('classification.type', self.parameters.type)
        event.add("raw", self.recover_line(row))
        yield event