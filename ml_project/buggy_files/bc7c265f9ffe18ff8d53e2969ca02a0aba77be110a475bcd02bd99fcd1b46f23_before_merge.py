    def parse_line(self, row, report):

        conf = self.sparser_config

        # we need to copy here...
        fields = copy.copy(self.fieldnames)
        # We will use this variable later.
        # Each time a field was successfully added to the
        # intelmq-event, this field will be removed from
        # the fields array.
        # at the end, all remaining fields are added to the
        # extra field.

        event = Event(report)
        extra = {}  # The Json-Object which will be populated with the
        # fields that could not be added to the standard intelmq fields
        # the parser is going to write this information into an object
        # one level below the "extra root"
        # e.g.: extra {'cc_dns': '127.0.0.1'}

        # set feed.name and code, honor the override parameter

        if hasattr(self.parameters, 'feedname'):
            if 'feed.name' in event and self.override:
                event.add('feed.name', self.parameters.feedname, force=True)
            elif 'feed.name' not in event:
                event.add('feed.name', self.parameters.feedname)

        # Iterate Config, add required fields.
        # Fail hard if not possible:
        for item in conf.get('required_fields'):
            intelmqkey, shadowkey = item[:2]
            if len(item) > 2:
                conv_func = item[2]
            else:
                conv_func = None

            raw_value = row.get(shadowkey)

            value = raw_value

            if conv_func is not None and raw_value is not None:
                if len(item) == 4 and item[3]:
                    value = conv_func(raw_value, row)
                else:
                    value = conv_func(raw_value)

            if value is not None:
                event.add(intelmqkey, value)
                fields.remove(shadowkey)

        # Now add optional fields.
        # This action may fail, the value is added to
        # extra if an add operation failed
        for item in conf.get('optional_fields'):
            intelmqkey, shadowkey = item[:2]
            if len(item) > 2:
                conv_func = item[2]
            else:
                conv_func = None
            raw_value = row.get(shadowkey)
            value = raw_value

            if conv_func is not None and raw_value is not None:
                if len(item) == 4 and item[3]:
                    value = conv_func(raw_value, row)
                else:
                    try:
                        value = conv_func(raw_value)
                    except:
                        self.logger.error('could not convert shadowkey: "{}", ' +
                                          'value: "{}" via conversion function {}'.format(shadowkey, raw_value, repr(conv_func)))
                        value = None
                        # """ fail early and often in this case. We want to be able to convert everything """
                        # self.stop()

            if value is not None:
                if intelmqkey == 'extra.':
                    extra[shadowkey] = value
                    fields.remove(shadowkey)
                    continue
                try:
                    event.add(intelmqkey, value)
                    fields.remove(shadowkey)
                except InvalidValue:
                    self.logger.info(
                        'Could not add key "{}";'
                        ' adding it to extras...'.format(shadowkey)
                    )
                    self.logger.debug('The value of the event is %s', value)
                except InvalidKey:
                    extra[intelmqkey] = value
                    fields.remove(shadowkey)
            else:
                fields.remove(shadowkey)

        # Now add additional constant fields.
        for key, value in conf.get('constant_fields', {}).items():
            event.add(key, value)

        raw_line = {k: self.conv_csv_shadowserver(v) for k, v in row.items()}
        event.add('raw', self.recover_line(raw_line))

        # Add everything which could not be resolved to extra.
        for f in fields:
            val = row[f]
            if not val == "":
                extra[f] = val

        if extra:
            event.add('extra', extra)

        yield event