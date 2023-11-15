    def put(self, request):
        # TODO(dcramer): this should validate options before saving them
        for k, v in six.iteritems(request.data):
            if v and isinstance(v, six.string_types):
                v = v.strip()
            try:
                option = options.lookup_key(k)
            except options.UnknownOption:
                # TODO(dcramer): unify API errors
                return Response(
                    {"error": "unknown_option", "errorDetail": {"option": k}}, status=400
                )

            try:
                if not (option.flags & options.FLAG_ALLOW_EMPTY) and not v:
                    options.delete(k)
                else:
                    options.set(k, v)
            except (TypeError, AssertionError) as e:
                # TODO(chadwhitacre): Use a custom exception for the
                # immutability case, especially since asserts disappear with
                # `python -O`.
                return Response(
                    {
                        "error": "invalid_type" if type(e) is TypeError else "immutable_option",
                        "errorDetail": {"option": k, "message": six.text_type(e)},
                    },
                    status=400,
                )
        # TODO(dcramer): this has nothing to do with configuring options and
        # should not be set here
        options.set("sentry:version-configured", sentry.get_version())
        return Response(status=200)