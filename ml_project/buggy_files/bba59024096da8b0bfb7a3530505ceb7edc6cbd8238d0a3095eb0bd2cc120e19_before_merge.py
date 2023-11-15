def get_docstring(filename, verbose=False):
    """
    Search for assignment of the DOCUMENTATION and EXAMPLES variables
    in the given file.
    Parse DOCUMENTATION from YAML and return the YAML doc or None
    together with EXAMPLES, as plain text.

    DOCUMENTATION can be extended using documentation fragments
    loaded by the PluginLoader from the module_docs_fragments
    directory.
    """

    doc = None
    plainexamples = None
    returndocs = None

    try:
        # Thank you, Habbie, for this bit of code :-)
        M = ast.parse(''.join(open(filename)))
        for child in M.body:
            if isinstance(child, ast.Assign):
                for t in child.targets:
                    try:
                        theid = t.id
                    except AttributeError as e:
                        # skip errors can happen when trying to use the normal code
                        continue

                    if 'DOCUMENTATION' in theid:
                        doc = yaml.safe_load(child.value.s)
                        fragments = doc.get('extends_documentation_fragment', [])

                        if isinstance(fragments, basestring):
                            fragments = [ fragments ]

                        # Allow the module to specify a var other than DOCUMENTATION
                        # to pull the fragment from, using dot notation as a separator
                        for fragment_slug in fragments:
                            fragment_slug = fragment_slug.lower()
                            if '.' in fragment_slug:
                                fragment_name, fragment_var = fragment_slug.split('.', 1)
                                fragment_var = fragment_var.upper()
                            else:
                                fragment_name, fragment_var = fragment_slug, 'DOCUMENTATION'

                            fragment_class = fragment_loader.get(fragment_name)
                            assert fragment_class is not None

                            fragment_yaml = getattr(fragment_class, fragment_var, '{}')
                            fragment = yaml.safe_load(fragment_yaml)

                            if fragment.has_key('notes'):
                                notes = fragment.pop('notes')
                                if notes:
                                    if not doc.has_key('notes'):
                                        doc['notes'] = []
                                    doc['notes'].extend(notes)

                            if 'options' not in fragment.keys():
                                raise Exception("missing options in fragment, possibly misformatted?")

                            for key, value in fragment.items():
                                if not doc.has_key(key):
                                    doc[key] = value
                                else:
                                    if isinstance(doc[key], MutableMapping):
                                        doc[key].update(value)
                                    elif isinstance(doc[key], MutableSet):
                                        doc[key].add(value)
                                    elif isinstance(doc[key], MutableSequence):
                                        doc[key] = sorted(frozenset(doc[key] + value))
                                    else:
                                        raise Exception("Attempt to extend a documentation fragement of unknown type")

                    elif 'EXAMPLES' in theid:
                        plainexamples = child.value.s[1:]  # Skip first empty line

                    elif 'RETURN' in theid:
                        returndocs = child.value.s[1:]
    except:
        display.error("unable to parse %s" % filename)
        if verbose == True:
            raise
    return doc, plainexamples, returndocs