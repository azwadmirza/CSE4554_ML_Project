def get_diff(module):

    reply = get_configuration(module, compare=True, format='text')
    output = reply.find('.//configuration-output')
    if output is not None:
        return output.text