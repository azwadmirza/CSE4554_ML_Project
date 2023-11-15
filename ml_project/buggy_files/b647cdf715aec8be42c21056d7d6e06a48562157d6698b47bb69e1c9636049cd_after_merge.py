def get_generic_completion_list(generic_list):

    @Completer
    def completer(cmd, prefix, namespace, **kwargs):  # pylint: disable=unused-argument
        return generic_list
    return completer