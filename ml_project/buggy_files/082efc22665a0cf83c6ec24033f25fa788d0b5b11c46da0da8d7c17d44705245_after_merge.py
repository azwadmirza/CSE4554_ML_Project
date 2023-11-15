def dosetup(name, version, packages, datafiles, scripts, ext_modules=[]):
    description, long_description = __doc__.split("\n", 1)
    kwargs = {}
    if py2exe:
        kwargs["distclass"] = TranslateDistribution

    setup(
        name=name,
        version=version,
        license="GNU General Public License (GPL)",
        description=description,
        long_description=long_description,
        author="Translate",
        author_email="translate-devel@lists.sourceforge.net",
        url="http://toolkit.translatehouse.org/",
        download_url="https://github.com/translate/translate/releases/tag/" + version,
        project_urls={
            "Issue Tracker": "https://github.com/translate/translate/issues",
            "Documentation": "http://docs.translatehouse.org/projects/translate-toolkit/",
        },
        platforms=["any"],
        classifiers=classifiers,
        packages=packages,
        data_files=datafiles,
        entry_points={
            'console_scripts': translatescripts,
        },
        scripts=scripts,
        ext_modules=ext_modules,
        cmdclass=cmdclass,
        install_requires=parse_requirements('requirements/required.txt'),
        **kwargs
    )