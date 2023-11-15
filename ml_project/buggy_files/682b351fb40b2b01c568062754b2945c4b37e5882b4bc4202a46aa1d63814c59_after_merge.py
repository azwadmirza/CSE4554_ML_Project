def render_template(template, destination, **kwargs):
    template = os.path.join(HERE, template)

    folder = os.path.dirname(destination)
    os.makedirs(folder)

    with codecs.open(template, 'r', encoding='utf-8') as f:
        raw_template = f.read()
        rendered = raw_template.format(**kwargs)
        with codecs.open(destination, 'w+', encoding='utf-8') as output:
            output.write(rendered)