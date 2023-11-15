    def display(self, ret, indent, prefix, out):
        '''
        Recursively iterate down through data structures to determine output
        '''
        if isinstance(ret, bytes):
            try:
                ret = salt.utils.stringutils.to_unicode(ret)
            except UnicodeDecodeError:
                # ret contains binary data that can't be decoded
                pass

        if ret is None or ret is True or ret is False:
            out.append(
                self.ustring(
                    indent,
                    self.LIGHT_YELLOW,
                    ret,
                    prefix=prefix
                )
            )
        # Number includes all python numbers types
        #  (float, int, long, complex, ...)
        elif isinstance(ret, Number):
            out.append(
                self.ustring(
                    indent,
                    self.LIGHT_YELLOW,
                    ret,
                    prefix=prefix
                )
            )
        elif isinstance(ret, six.string_types):
            first_line = True
            for line in ret.splitlines():
                if self.strip_colors:
                    line = salt.output.strip_esc_sequence(line)
                line_prefix = ' ' * len(prefix) if not first_line else prefix
                out.append(
                    self.ustring(
                        indent,
                        self.GREEN,
                        line,
                        prefix=line_prefix
                    )
                )
                first_line = False
        elif isinstance(ret, (list, tuple)):
            color = self.GREEN
            if self.retcode != 0:
                color = self.RED
            for ind in ret:
                if isinstance(ind, (list, tuple, dict)):
                    out.append(
                        self.ustring(
                            indent,
                            color,
                            '|_'
                        )
                    )
                    prefix = '' if isinstance(ind, dict) else '- '
                    self.display(ind, indent + 2, prefix, out)
                else:
                    self.display(ind, indent, '- ', out)
        elif isinstance(ret, dict):
            if indent:
                color = self.CYAN
                if self.retcode != 0:
                    color = self.RED
                out.append(
                    self.ustring(
                        indent,
                        color,
                        '----------'
                    )
                )

            # respect key ordering of ordered dicts
            if isinstance(ret, salt.utils.odict.OrderedDict):
                keys = ret.keys()
            else:
                keys = sorted(ret)
            color = self.CYAN
            if self.retcode != 0:
                color = self.RED
            for key in keys:
                val = ret[key]
                out.append(
                    self.ustring(
                        indent,
                        color,
                        key,
                        suffix=':',
                        prefix=prefix
                    )
                )
                self.display(val, indent + 4, '', out)
        return out