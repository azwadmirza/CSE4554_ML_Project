def main():
    version = sys.version_info[:2]
    virtualenv_open = ['virtualenv>=1.11.2']
    virtualenv_capped = ['virtualenv>=1.11.2,<14']
    install_requires = ['py>=1.4.17', 'pluggy>=0.3.0,<1.0', 'six']
    extras_require = {}
    if has_environment_marker_support():
        extras_require[':python_version=="2.6"'] = ['argparse']
        extras_require[':python_version=="3.2"'] = virtualenv_capped
        extras_require[':python_version!="3.2"'] = virtualenv_open
    else:
        if version < (2, 7):
            install_requires += ['argparse']
        install_requires += (
            virtualenv_capped if version == (3, 2) else virtualenv_open
        )
    setuptools.setup(
        name='tox',
        description='virtualenv-based automation of test activities',
        long_description=get_long_description(),
        url='https://tox.readthedocs.org/',
        use_scm_version=True,
        license='http://opensource.org/licenses/MIT',
        platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
        author='holger krekel',
        author_email='holger@merlinux.eu',
        packages=['tox'],
        entry_points={'console_scripts': 'tox=tox:cmdline\ntox-quickstart=tox._quickstart:main'},
        setup_requires=['setuptools_scm'],
        install_requires=install_requires,
        extras_require=extras_require,
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: MacOS :: MacOS X',
            'Topic :: Software Development :: Testing',
            'Topic :: Software Development :: Libraries',
            'Topic :: Utilities'] + [
                ('Programming Language :: Python :: %s' % x) for x in
                '2 2.6 2.7 3 3.3 3.4 3.5 3.6'.split()]
    )