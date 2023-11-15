def create_macro_capture_env(node):

    class ParserMacroCapture(jinja2.Undefined):
        """
        This class sets up the parser to capture macros.
        """
        def __init__(self, hint=None, obj=None, name=None,
                     exc=None):
            super(jinja2.Undefined, self).__init__()
            self.node = node
            self.name = name
            self.package_name = node.get('package_name')
            # jinja uses these for safety, so we have to override them.
            # see https://github.com/pallets/jinja/blob/master/jinja2/sandbox.py#L332-L339 # noqa
            self.unsafe_callable = False
            self.alters_data = False

        def __deepcopy__(self, memo):
            path = os.path.join(self.node.get('root_path'),
                                self.node.get('original_file_path'))

            logger.debug(
                'A ParserMacroCapture has been deecopy()d, invalid reference '
                'to "{}" in node {}.{} (source path: {})'
                .format(self.name, self.node.get('package_name'),
                        self.node.get('name'),
                        path))

            dbt.exceptions.raise_compiler_error(
                'dbt has detected at least one invalid reference in {}.{}. '
                'Check logs for more information'
                .format(self.node.get('package_name'), self.node.get('name'))
            )

        def __getattr__(self, name):
            if name == 'name' or _is_dunder_name(name):
                raise AttributeError(
                    "'{}' object has no attribute '{}'"
                    .format(type(self).__name__, name)
                )

            self.package_name = self.name
            self.name = name

            return self

        def __call__(self, *args, **kwargs):
            return True

    return ParserMacroCapture