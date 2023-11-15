    def _common_request(  # pylint: disable=too-many-locals
        self,
        args_name,
        traced_args,
        operation_name,
        original_func,
        instance,
        args,
        kwargs,
    ):

        endpoint_name = getattr(instance, "host").split(".")[0]

        with self._tracer.start_as_current_span(
            "{}.command".format(endpoint_name), kind=SpanKind.CONSUMER,
        ) as span:
            if args:
                http_method = args[0]
                span.resource = "%s.%s" % (endpoint_name, http_method.lower())
            else:
                span.resource = endpoint_name

            add_span_arg_tags(
                span, endpoint_name, args, args_name, traced_args,
            )

            # Obtaining region name
            region_name = _get_instance_region_name(instance)

            meta = {
                "aws.agent": "boto",
                "aws.operation": operation_name,
            }
            if region_name:
                meta["aws.region"] = region_name

            for key, value in meta.items():
                span.set_attribute(key, value)

            # Original func returns a boto.connection.HTTPResponse object
            result = original_func(*args, **kwargs)
            span.set_attribute("http.status_code", getattr(result, "status"))
            span.set_attribute("http.method", getattr(result, "_method"))

            return result