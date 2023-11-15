def clean_json(path, target):
    """Delete key in the JSON file"""
    import json
    changed = False
    targets = target.split('/')

    # read file to parser
    with open(path, 'r') as f:
        js = json.load(f)

    # change file
    pos = js
    while True:
        new_target = targets.pop(0)
        if not isinstance(pos, dict):
            break
        if new_target in pos and len(targets) > 0:
            # descend
            pos = pos[new_target]
        elif new_target in pos:
            # delete terminal target
            changed = True
            del(pos[new_target])
        else:
            # target not found
            break
        if 0 == len(targets):
            # target not found
            break

    if changed:
        from bleachbit.Options import options
        if options.get('shred'):
            delete(path, True)
        # write file
        with open(path, 'w') as f:
            json.dump(js, f)