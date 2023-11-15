def generate(d, overwrite=True, silent=False, templatedir=None):
    # type: (Dict, bool, bool, unicode) -> None
    """Generate project based on values in *d*."""
    template = QuickstartRenderer(templatedir=templatedir)

    texescape.init()
    indent = ' ' * 4

    if 'mastertoctree' not in d:
        d['mastertoctree'] = ''
    if 'mastertocmaxdepth' not in d:
        d['mastertocmaxdepth'] = 2

    d['PY3'] = PY3
    d['project_fn'] = make_filename(d['project'])
    d['project_url'] = urlquote(d['project'].encode('idna'))
    d['project_manpage'] = d['project_fn'].lower()
    d['now'] = time.asctime()
    d['project_underline'] = column_width(d['project']) * '='
    d.setdefault('extensions', [])
    for name in EXTENSIONS:
        if d.get('ext_' + name):
            d['extensions'].append('sphinx.ext.' + name)
    d['extensions'] = (',\n' + indent).join(repr(name) for name in d['extensions'])
    d['copyright'] = time.strftime('%Y') + ', ' + d['author']
    d['author_texescaped'] = text_type(d['author']).\
        translate(texescape.tex_escape_map)
    d['project_doc'] = d['project'] + ' Documentation'
    d['project_doc_texescaped'] = text_type(d['project'] + ' Documentation').\
        translate(texescape.tex_escape_map)

    # escape backslashes and single quotes in strings that are put into
    # a Python string literal
    for key in ('project', 'project_doc', 'project_doc_texescaped',
                'author', 'author_texescaped', 'copyright',
                'version', 'release', 'master'):
        d[key + '_str'] = d[key].replace('\\', '\\\\').replace("'", "\\'")

    if not path.isdir(d['path']):
        mkdir_p(d['path'])

    srcdir = d['sep'] and path.join(d['path'], 'source') or d['path']

    mkdir_p(srcdir)
    if d['sep']:
        builddir = path.join(d['path'], 'build')
        d['exclude_patterns'] = ''
    else:
        builddir = path.join(srcdir, d['dot'] + 'build')
        exclude_patterns = map(repr, [
            d['dot'] + 'build',
            'Thumbs.db', '.DS_Store',
        ])
        d['exclude_patterns'] = ', '.join(exclude_patterns)
    mkdir_p(builddir)
    mkdir_p(path.join(srcdir, d['dot'] + 'templates'))
    mkdir_p(path.join(srcdir, d['dot'] + 'static'))

    def write_file(fpath, content, newline=None):
        # type: (unicode, unicode, unicode) -> None
        if overwrite or not path.isfile(fpath):
            if 'quiet' not in d:
                print('Creating file %s.' % fpath)
            with open(fpath, 'wt', encoding='utf-8', newline=newline) as f:
                f.write(content)
        else:
            if 'quiet' not in d:
                print('File %s already exists, skipping.' % fpath)

    conf_path = os.path.join(templatedir, 'conf.py_t') if templatedir else None
    if not conf_path or not path.isfile(conf_path):
        conf_path = os.path.join(package_dir, 'templates', 'quickstart', 'conf.py_t')
    with open(conf_path) as f:
        conf_text = convert_python_source(f.read())

    write_file(path.join(srcdir, 'conf.py'), template.render_string(conf_text, d))

    masterfile = path.join(srcdir, d['master'] + d['suffix'])
    write_file(masterfile, template.render('quickstart/master_doc.rst_t', d))

    if d.get('make_mode') is True:
        makefile_template = 'quickstart/Makefile.new_t'
        batchfile_template = 'quickstart/make.bat.new_t'
    else:
        makefile_template = 'quickstart/Makefile_t'
        batchfile_template = 'quickstart/make.bat_t'

    if d['makefile'] is True:
        d['rsrcdir'] = d['sep'] and 'source' or '.'
        d['rbuilddir'] = d['sep'] and 'build' or d['dot'] + 'build'
        # use binary mode, to avoid writing \r\n on Windows
        write_file(path.join(d['path'], 'Makefile'),
                   template.render(makefile_template, d), u'\n')

    if d['batchfile'] is True:
        d['rsrcdir'] = d['sep'] and 'source' or '.'
        d['rbuilddir'] = d['sep'] and 'build' or d['dot'] + 'build'
        write_file(path.join(d['path'], 'make.bat'),
                   template.render(batchfile_template, d), u'\r\n')

    if silent:
        return
    print()
    print(bold('Finished: An initial directory structure has been created.'))
    print('''
You should now populate your master file %s and create other documentation
source files. ''' % masterfile + ((d['makefile'] or d['batchfile']) and '''\
Use the Makefile to build the docs, like so:
   make builder
''' or '''\
Use the sphinx-build command to build the docs, like so:
   sphinx-build -b builder %s %s
''' % (srcdir, builddir)) + '''\
where "builder" is one of the supported builders, e.g. html, latex or linkcheck.
''')