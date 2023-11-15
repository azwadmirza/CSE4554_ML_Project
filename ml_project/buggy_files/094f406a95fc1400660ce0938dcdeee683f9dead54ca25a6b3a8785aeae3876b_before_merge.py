    def from_data(cls, data, **options):
        """
        This is a second way to initialize StructureFormat, using the raw data
        as input. Added to avoid changing the signature of __init__.
        """
        format_functions = []
        for field_name in data.dtype.names:
            format_function = _get_format_function(data[field_name], **options)
            if data.dtype[field_name].shape != ():
                format_function = SubArrayFormat(format_function)
            format_functions.append(format_function)
        return cls(format_functions)