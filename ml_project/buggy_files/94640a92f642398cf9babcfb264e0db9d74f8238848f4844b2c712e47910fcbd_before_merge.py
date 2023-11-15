def from_environment(name, prefix, no_builds=False, ignore_channels=False):
    installed = install.linked(prefix, ignore_channels=ignore_channels)
    conda_pkgs = copy(installed)
    # json=True hides the output, data is added to installed
    add_pip_installed(prefix, installed, json=True)

    pip_pkgs = sorted(installed - conda_pkgs)

    if no_builds:
        dependencies = ['='.join(a.rsplit('-', 2)[0:2]) for a in sorted(conda_pkgs)]
    else:
        dependencies = ['='.join(a.rsplit('-', 2)) for a in sorted(conda_pkgs)]
    if len(pip_pkgs) > 0:
        dependencies.append({'pip': ['=='.join(a.rsplit('-', 2)[:2]) for a in pip_pkgs]})
    # conda uses ruamel_yaml which returns a ruamel_yaml.comments.CommentedSeq
    # this doesn't dump correctly using pyyaml
    channels = context.channels

    return Environment(name=name, dependencies=dependencies, channels=channels, prefix=prefix)