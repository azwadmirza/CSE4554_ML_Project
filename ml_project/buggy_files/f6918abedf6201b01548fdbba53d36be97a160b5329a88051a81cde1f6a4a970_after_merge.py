    def __init__(self, package, **kwargs):
        package_message = ""
        if package is not None:
            package_message = crayons.normal("Couldn't install package {0}\n".format(
                crayons.white(package, bold=True)
            ))
        message = "{0} {1} {2}".format(
            crayons.red("ERROR:", bold=True),
            package_message,
            crayons.yellow("Package installation failed...")
        )
        extra = kwargs.pop("extra", [])
        PipenvException.__init__(self, message=decode_for_output(message), extra=extra, **kwargs)