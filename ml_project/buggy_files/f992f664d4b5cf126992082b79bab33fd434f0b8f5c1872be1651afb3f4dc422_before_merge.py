def __exporter_from_file(template_file):
    """Create a template class from a file"""
    name = os.path.basename(template_file).replace(".template", "")
    template = Template.from_file(template_file)
    return type("{}Exporter".format(name.title()), (GenericTemplateExporter, ), {
        "names": [name],
        "extension": template.extension,
        "template": template
    })