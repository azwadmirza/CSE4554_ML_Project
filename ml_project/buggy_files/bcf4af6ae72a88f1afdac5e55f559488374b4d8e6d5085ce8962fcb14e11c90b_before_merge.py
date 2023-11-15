    def __init__(self, args, **kwargs):

        self.wait = not kwargs.pop('bg', False)
        self.stdin = kwargs.pop('stdin', None)
        self.with_communicate = kwargs.pop('with_communicate', self.wait)
        self.timeout = kwargs.pop('timeout', None)

        # If you're not willing to wait for the process
        # you can't define any stdin, stdout or stderr
        if not self.wait:
            self.stdin = kwargs['stdin'] = None
            self.with_communicate = False
        elif self.stdin is not None:
            # Translate a newline submitted as '\n' on the CLI to an actual
            # newline character.
            self.stdin = self.stdin.replace('\\n', '\n').encode(__salt_system_encoding__)
            kwargs['stdin'] = subprocess.PIPE

        if not self.with_communicate:
            self.stdout = kwargs['stdout'] = None
            self.stderr = kwargs['stderr'] = None

        if self.timeout and not isinstance(self.timeout, (int, float)):
            raise salt.exceptions.TimedProcTimeoutError('Error: timeout {0} must be a number'.format(self.timeout))
        if six.PY2 and kwargs.get('shell', False):
            args = salt.utils.stringutils.to_bytes(args)

        try:
            self.process = subprocess.Popen(args, **kwargs)
        except (AttributeError, TypeError):
            if not kwargs.get('shell', False):
                if not isinstance(args, (list, tuple)):
                    try:
                        args = shlex.split(args)
                    except AttributeError:
                        args = shlex.split(six.text_type(args))
                str_args = []
                for arg in args:
                    if not isinstance(arg, six.string_types):
                        str_args.append(six.text_type(arg))
                    else:
                        str_args.append(arg)
                args = str_args
            else:
                if not isinstance(args, (list, tuple, six.string_types)):
                    # Handle corner case where someone does a 'cmd.run 3'
                    args = six.text_type(args)
            # Ensure that environment variables are strings
            for key, val in six.iteritems(kwargs.get('env', {})):
                if not isinstance(val, six.string_types):
                    kwargs['env'][key] = six.text_type(val)
                if not isinstance(key, six.string_types):
                    kwargs['env'][six.text_type(key)] = kwargs['env'].pop(key)
            if six.PY2 and 'env' in kwargs:
                # Ensure no unicode in custom env dict, as it can cause
                # problems with subprocess.
                kwargs['env'] = salt.utils.data.encode_dict(kwargs['env'])
            args = salt.utils.data.decode(args)
            self.process = subprocess.Popen(args, **kwargs)
        self.command = args