def setup_package():
    # Rewrite the version file every time
    write_version_py()

    cmdclass = {'sdist': sdist_checked}
    if HAVE_SPHINX:
        cmdclass['build_sphinx'] = ScipyBuildDoc

    # Figure out whether to add ``*_requires = ['numpy']``.
    # We don't want to do that unconditionally, because we risk updating
    # an installed numpy which fails too often.  Just if it's not installed, we
    # may give it a try.  See gh-3379.
    try:
        import numpy
    except ImportError:  # We do not have numpy installed
        build_requires = ['numpy>=1.13.3']
    else:
        # If we're building a wheel, assume there already exist numpy wheels
        # for this platform, so it is safe to add numpy to build requirements.
        # See gh-5184.
        build_requires = (['numpy>=1.13.3'] if 'bdist_wheel' in sys.argv[1:]
                          else [])

    install_requires = build_requires
    setup_requires = build_requires + ['pybind11>=2.2.4']

    metadata = dict(
        name='scipy',
        maintainer="SciPy Developers",
        maintainer_email="scipy-dev@python.org",
        description=DOCLINES[0],
        long_description="\n".join(DOCLINES[2:]),
        url="https://www.scipy.org",
        download_url="https://github.com/scipy/scipy/releases",
        project_urls={
            "Bug Tracker": "https://github.com/scipy/scipy/issues",
            "Documentation": "https://docs.scipy.org/doc/scipy/reference/",
            "Source Code": "https://github.com/scipy/scipy",
        },
        license='BSD',
        cmdclass=cmdclass,
        classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
        platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
        test_suite='nose.collector',
        setup_requires=setup_requires,
        install_requires=install_requires,
        python_requires='>=3.5',
    )

    if "--force" in sys.argv:
        run_build = True
        sys.argv.remove('--force')
    else:
        # Raise errors for unsupported commands, improve help output, etc.
        run_build = parse_setuppy_commands()

    # Disable OSX Accelerate, it has too old LAPACK
    os.environ['ACCELERATE'] = 'None'

    # This import is here because it needs to be done before importing setup()
    # from numpy.distutils, but after the MANIFEST removing and sdist import
    # higher up in this file.
    from setuptools import setup

    if run_build:
        from numpy.distutils.core import setup

        # Customize extension building
        cmdclass['build_ext'] = get_build_ext_override()

        cwd = os.path.abspath(os.path.dirname(__file__))
        if not os.path.exists(os.path.join(cwd, 'PKG-INFO')):
            # Generate Cython sources, unless building from source release
            generate_cython()

        metadata['configuration'] = configuration
    else:
        # Don't import numpy here - non-build actions are required to succeed
        # without NumPy for example when pip is used to install Scipy when
        # NumPy is not yet present in the system.

        # Version number is added to metadata inside configuration() if build
        # is run.
        metadata['version'] = get_version_info()[0]

    setup(**metadata)