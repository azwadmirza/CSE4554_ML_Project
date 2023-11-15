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