    def out(self):
        """
        Prints a readable Quil string representation of this gate.

        :returns: String representation of a gate
        :rtype: string
        """
        def format_matrix_element(element):
            """
            Formats a parameterized matrix element.

            :param element: {int, float, complex, str} The parameterized element to format.
            """
            if isinstance(element, integer_types) or isinstance(element, (float, complex)):
                return format_parameter(element)
            elif isinstance(element, string_types):
                return element
            else:
                raise TypeError("Invalid matrix element: %r" % element)

        result = "DEFGATE %s:\n" % self.name
        for row in self.matrix:
            result += "    "
            fcols = [format_matrix_element(col) for col in row]
            result += ", ".join(fcols)
            result += "\n"
        return result