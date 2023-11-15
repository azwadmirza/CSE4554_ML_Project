def jdump(text):
    try:
        display.display(json.dumps(text, cls=AnsibleJSONEncoder, sort_keys=True, indent=4))
    except TypeError as e:
        raise AnsibleError('We could not convert all the documentation into JSON as there was a conversion issue: %s' % to_native(e))