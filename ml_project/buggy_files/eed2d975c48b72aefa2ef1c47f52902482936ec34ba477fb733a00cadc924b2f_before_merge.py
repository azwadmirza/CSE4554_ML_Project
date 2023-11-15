def infer_enum_class(node):
    """ Specific inference for enums. """
    names = set(('Enum', 'IntEnum', 'enum.Enum', 'enum.IntEnum'))
    for basename in node.basenames:
        # TODO: doesn't handle subclasses yet. This implementation
        # is a hack to support enums.
        if basename not in names:
            continue
        if node.root().name == 'enum':
            # Skip if the class is directly from enum module.
            break
        for local, values in node.locals.items():
            if any(not isinstance(value, nodes.AssignName)
                   for value in values):
                continue

            stmt = values[0].statement()
            if isinstance(stmt.targets[0], nodes.Tuple):
                targets = stmt.targets[0].itered()
            else:
                targets = stmt.targets

            new_targets = []
            for target in targets:
                # Replace all the assignments with our mocked class.
                classdef = dedent('''
                class %(name)s(%(types)s):
                    @property
                    def value(self):
                        # Not the best return.
                        return None
                    @property
                    def name(self):
                        return %(name)r
                ''' % {'name': target.name, 'types': ', '.join(node.basenames)})
                fake = AstroidBuilder(MANAGER).string_build(classdef)[target.name]
                fake.parent = target.parent
                for method in node.mymethods():
                    fake.locals[method.name] = [method]
                new_targets.append(fake.instantiate_class())
            node.locals[local] = new_targets
        break
    return node