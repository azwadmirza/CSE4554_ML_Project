def render_template(templatefile: str, arguments: dict = {}) -> str:

    from jinja2 import Environment, PackageLoader, select_autoescape

    env = Environment(
        loader=PackageLoader('freqtrade', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(templatefile)
    return template.render(**arguments)