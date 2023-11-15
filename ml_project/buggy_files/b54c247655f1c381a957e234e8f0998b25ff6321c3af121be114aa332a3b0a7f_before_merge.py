def get_yes_or_no(prompt, **kwargs):
    default_value = kwargs.get('default', None)

    if default_value is None:
        prompt += ' [y/n] '
    elif default_value is True:
        prompt += ' [Y/n] '
    elif default_value is False:
        prompt += ' [y/N] '
    else:
        raise ValueError(
            "default for get_yes_no() must be True, False, or None.")

    result = None
    while result is None:
        msg(prompt, newline=False)
        ans = raw_input().lower()
        if not ans:
            result = default_value
            if result is None:
                print("Please enter yes or no.")
        else:
            if ans == 'y' or ans == 'yes':
                result = True
            elif ans == 'n' or ans == 'no':
                result = False
    return result