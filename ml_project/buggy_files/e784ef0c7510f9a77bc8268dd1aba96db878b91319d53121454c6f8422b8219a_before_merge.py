    def warn(self, docname, msg, lineno=None, **kwargs):
        # type: (unicode, unicode, int, Any) -> None
        """Emit a warning.

        This differs from using ``app.warn()`` in that the warning may not
        be emitted instantly, but collected for emitting all warnings after
        the update of the environment.
        """
        # strange argument order is due to backwards compatibility
        self._warnfunc(msg, (docname, lineno), **kwargs)