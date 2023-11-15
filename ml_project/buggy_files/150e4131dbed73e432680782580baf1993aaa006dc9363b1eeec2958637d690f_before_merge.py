def _safe_output(line):
    '''
    Looks for rabbitmqctl warning, or general formatting, strings that aren't
    intended to be parsed as output.
    Returns a boolean whether the line can be parsed as rabbitmqctl output.
    '''
    return not any([
        line.startswith('Listing') and line.endswith('...'),
        '...done' in line,
        line.startswith('WARNING:')
    ])