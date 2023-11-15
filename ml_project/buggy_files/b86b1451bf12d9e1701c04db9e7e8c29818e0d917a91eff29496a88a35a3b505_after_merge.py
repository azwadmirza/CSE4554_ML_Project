    def format_args(self, **kwargs: Any) -> str:
        if self.env.config.autodoc_typehints in ('none', 'description'):
            kwargs.setdefault('show_annotation', False)

        unwrapped = inspect.unwrap(self.object)
        try:
            self.env.app.emit('autodoc-before-process-signature', unwrapped, False)
            sig = inspect.signature(unwrapped)
            args = stringify_signature(sig, **kwargs)
        except TypeError as exc:
            logger.warning(__("Failed to get a function signature for %s: %s"),
                           self.fullname, exc)
            return None
        except ValueError:
            args = ''

        if self.env.config.strip_signature_backslash:
            # escape backslashes for reST
            args = args.replace('\\', '\\\\')
        return args