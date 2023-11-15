def get_generic_completion_list(generic_list):
    def completer(prefix, action, parsed_args, **kwargs):  # pylint: disable=unused-argument
        return generic_list
    return completer