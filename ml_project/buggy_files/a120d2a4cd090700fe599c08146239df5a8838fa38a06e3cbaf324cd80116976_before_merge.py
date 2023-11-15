def prompt_for_config(context, no_input=False):
    """
    Prompts the user to enter new config, using context as a source for the
    field names and sample values.

    :param no_input: Prompt the user at command line for manual configuration?
    """
    cookiecutter_dict = {}
    env = Environment()

    for key, raw in iteritems(context['cookiecutter']):
        val = env.from_string(raw).render(cookiecutter=cookiecutter_dict)

        if not no_input:
            prompt = '{0} (default is "{1}")? '.format(key, val)

            new_val = read_response(prompt).strip()

            if new_val != '':
                val = new_val

        cookiecutter_dict[key] = val
    return cookiecutter_dict