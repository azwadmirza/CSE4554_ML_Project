    def arg_split(commandline, posix=False, strict=True):
        """Split a command line's arguments in a shell-like manner.

        This is a special version for windows that use a ctypes call to CommandLineToArgvW
        to do the argv splitting. The posix paramter is ignored.
        
        If strict=False, process_common.arg_split(...strict=False) is used instead.
        """
        #CommandLineToArgvW returns path to executable if called with empty string.
        if commandline.strip() == "":
            return []
        if not strict:
            # not really a cl-arg, fallback on _process_common
            return py_arg_split(commandline, posix=posix, strict=strict)
        argvn = c_int()
        result_pointer = CommandLineToArgvW(py3compat.cast_unicode(commandline.lstrip()), ctypes.byref(argvn))
        result_array_type = LPCWSTR * argvn.value
        result = [arg for arg in result_array_type.from_address(result_pointer)]
        retval = LocalFree(result_pointer)
        return result