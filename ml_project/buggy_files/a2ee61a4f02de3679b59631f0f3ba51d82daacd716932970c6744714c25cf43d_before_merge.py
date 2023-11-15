    def started(self, event: monitoring.CommandStartedEvent):
        """ Method to handle a pymongo CommandStartedEvent """
        if not self.is_enabled:
            return
        command = event.command.get(event.command_name, "")
        name = DATABASE_TYPE + "." + event.command_name
        statement = event.command_name
        if command:
            name += "." + command
            statement += " " + command

        try:
            span = self._tracer.start_span(name, kind=SpanKind.CLIENT)
            span.set_attribute("component", DATABASE_TYPE)
            span.set_attribute("db.type", DATABASE_TYPE)
            span.set_attribute("db.instance", event.database_name)
            span.set_attribute("db.statement", statement)
            if event.connection_id is not None:
                span.set_attribute("net.peer.name", event.connection_id[0])
                span.set_attribute("net.peer.port", event.connection_id[1])

            # pymongo specific, not specified by spec
            span.set_attribute("db.mongo.operation_id", event.operation_id)
            span.set_attribute("db.mongo.request_id", event.request_id)

            for attr in COMMAND_ATTRIBUTES:
                _attr = event.command.get(attr)
                if _attr is not None:
                    span.set_attribute("db.mongo." + attr, str(_attr))

            # Add Span to dictionary
            self._span_dict[_get_span_dict_key(event)] = span
        except Exception as ex:  # noqa pylint: disable=broad-except
            if span is not None:
                span.set_status(Status(StatusCanonicalCode.INTERNAL, str(ex)))
                span.end()
                self._pop_span(event)