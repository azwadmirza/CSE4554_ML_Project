    def _get_value_and_line_offset(self, key, values):
        """Returns the index of the location of key, value pair in lines.

        :type key: str
        :param key: key, in config file.

        :type values: str
        :param values: values for key, in config file. This is plural,
            because you can have multiple values per key. Eg.

            >>> key =
            ...     value1
            ...     value2

        :type lines: list
        :param lines: a collection of lines-so-far in file

        :rtype: list(tuple)
        """
        values_list = self._construct_values_list(values)
        if not values_list:
            return []

        current_value_list_index = 0
        output = []
        lines_modified = False

        first_line_regex = re.compile(r'^\s*{}[ :=]+{}'.format(
            re.escape(key),
            re.escape(values_list[current_value_list_index]),
        ))
        comment_regex = re.compile(r'\s*[;#]')
        for index, line in enumerate(self.lines):
            if current_value_list_index == 0:
                if first_line_regex.match(line):
                    output.append((
                        values_list[current_value_list_index],
                        self.line_offset + index + 1,
                    ))

                    current_value_list_index += 1

                continue

            # Check ignored lines before checking values, because
            # you can write comments *after* the value.

            # Ignore blank lines
            if not line.strip():
                continue

            # Ignore comments
            if comment_regex.match(line):
                continue

            if current_value_list_index == len(values_list):
                if index == 0:
                    index = 1       # don't want to count the same line again

                self.line_offset += index
                self.lines = self.lines[index:]
                lines_modified = True

                break
            else:
                output.append((
                    values_list[current_value_list_index],
                    self.line_offset + index + 1,
                ))

                current_value_list_index += 1

        if not lines_modified:
            # No more lines left, if loop was not explicitly left.
            self.lines = []

        return output