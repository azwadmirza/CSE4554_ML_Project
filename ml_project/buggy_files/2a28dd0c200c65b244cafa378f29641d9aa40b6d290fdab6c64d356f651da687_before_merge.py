    def compute_collision_identifier(self, function_or_class):
        """The identifier is used to detect excessive duplicate exports.

        The identifier is used to determine when the same function or class is
        exported many times. This can yield false positives.

        Args:
            function_or_class: The function or class to compute an identifier
                for.

        Returns:
            The identifier. Note that different functions or classes can give
                rise to same identifier. However, the same function should
                hopefully always give rise to the same identifier. TODO(rkn):
                verify if this is actually the case. Note that if the
                identifier is incorrect in any way, then we may give warnings
                unnecessarily or fail to give warnings, but the application's
                behavior won't change.
        """
        import io
        string_file = io.StringIO()
        if sys.version_info[1] >= 7:
            dis.dis(function_or_class, file=string_file, depth=2)
        else:
            dis.dis(function_or_class, file=string_file)
        collision_identifier = (
            function_or_class.__name__ + ":" + string_file.getvalue())

        # Return a hash of the identifier in case it is too large.
        return hashlib.sha1(collision_identifier.encode("ascii")).digest()