    def _patched_api_call(self, original_func, instance, args, kwargs):

        endpoint_name = deep_getattr(instance, "_endpoint._endpoint_prefix")

        with self._tracer.start_as_current_span(
            "{}.command".format(endpoint_name), kind=SpanKind.CONSUMER,
        ) as span:

            operation = None
            if args:
                operation = args[0]
                span.resource = Resource(
                    labels={
                        "endpoint": endpoint_name,
                        "operation": operation.lower(),
                    }
                )

            else:
                span.resource = Resource(labels={"endpoint": endpoint_name})

            add_span_arg_tags(
                span,
                endpoint_name,
                args,
                ("action", "params", "path", "verb"),
                {"params", "path", "verb"},
            )

            region_name = deep_getattr(instance, "meta.region_name")

            meta = {
                "aws.agent": "botocore",
                "aws.operation": operation,
                "aws.region": region_name,
            }
            for key, value in meta.items():
                span.set_attribute(key, value)

            result = original_func(*args, **kwargs)

            span.set_attribute(
                "http.status_code",
                result["ResponseMetadata"]["HTTPStatusCode"],
            )
            span.set_attribute(
                "retry_attempts", result["ResponseMetadata"]["RetryAttempts"],
            )

            return result