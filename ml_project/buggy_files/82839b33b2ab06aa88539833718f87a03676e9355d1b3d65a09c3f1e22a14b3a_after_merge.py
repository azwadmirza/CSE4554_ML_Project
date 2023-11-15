def embed_code_links(app, exception):
    """Embed hyperlinks to documentation into example code"""
    try:
        if exception is not None:
            return
        print('Embedding documentation hyperlinks in examples..')

        # Add resolvers for the packages for which we want to show links
        doc_resolvers = {}
        doc_resolvers['sklearn'] = SphinxDocLinkResolver(app.builder.outdir,
                                                         relative=True)

        doc_resolvers['matplotlib'] = SphinxDocLinkResolver(
            'http://matplotlib.org')

        doc_resolvers['numpy'] = SphinxDocLinkResolver(
            'http://docs.scipy.org/doc/numpy-1.6.0')

        doc_resolvers['scipy'] = SphinxDocLinkResolver(
            'http://docs.scipy.org/doc/scipy-0.11.0/reference')

        example_dir = os.path.join(app.builder.srcdir, 'auto_examples')
        html_example_dir = os.path.abspath(os.path.join(app.builder.outdir,
                                                        'auto_examples'))

        # patterns for replacement
        link_pattern = '<a href="%s">%s</a>'
        orig_pattern = '<span class="n">%s</span>'
        period = '<span class="o">.</span>'

        for dirpath, _, filenames in os.walk(html_example_dir):
            for fname in filenames:
                print('\tprocessing: %s' % fname)
                full_fname = os.path.join(html_example_dir, dirpath, fname)
                subpath = dirpath[len(html_example_dir) + 1:]
                pickle_fname = os.path.join(example_dir, subpath,
                                            fname[:-5] + '_codeobj.pickle')

                if os.path.exists(pickle_fname):
                    # we have a pickle file with the objects to embed links for
                    with open(pickle_fname, 'rb') as fid:
                        example_code_obj = pickle.load(fid)
                    fid.close()
                    str_repl = {}
                    # generate replacement strings with the links
                    for name, cobj in example_code_obj.items():
                        this_module = cobj['module'].split('.')[0]

                        if this_module not in doc_resolvers:
                            continue

                        link = doc_resolvers[this_module].resolve(cobj,
                                                                  full_fname)
                        if link is not None:
                            parts = name.split('.')
                            name_html = period.join(orig_pattern % part
                                                    for part in parts)
                            str_repl[name_html] = link_pattern % (link, name_html)
                    # do the replacement in the html file

                    # ensure greediness
                    names = sorted(str_repl, key=len, reverse=True)
                    expr = re.compile(r'(?<!\.)\b' +  # don't follow . or word
                                      '|'.join(re.escape(name)
                                               for name in names))

                    def substitute_link(match):
                        return str_repl[match.group()]

                    if len(str_repl) > 0:
                        with open(full_fname, 'rb') as fid:
                            lines_in = fid.readlines()
                        with open(full_fname, 'wb') as fid:
                            for line in lines_in:
                                line = line.decode('utf-8')
                                line = expr.sub(substitute_link, line)
                                fid.write(line.encode('utf-8'))
    except HTTPError as e:
        print("The following HTTP Error has occurred:\n")
        print(e.code)
    except URLError as e:
        print("\n...\n"
              "Warning: Embedding the documentation hyperlinks requires "
              "internet access.\nPlease check your network connection.\n"
              "Unable to continue embedding due to a URL Error: \n")
        print(e.args)
    print('[done]')