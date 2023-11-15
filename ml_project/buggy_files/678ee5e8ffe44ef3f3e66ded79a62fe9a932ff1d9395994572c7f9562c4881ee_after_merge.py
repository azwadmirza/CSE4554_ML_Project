def declare_dependencies():
    for dep in DESCRIPTIONS:
        # Detect if dependency is optional
        if dep.get('optional', False):
            optional = True
        else:
            optional = False

        add(dep['modname'], dep['package_name'],
            dep['features'], dep['required_version'],
            optional=optional)