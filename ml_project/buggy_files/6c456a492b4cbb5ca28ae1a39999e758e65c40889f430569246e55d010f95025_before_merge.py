def run_setup():
    setup(name='bleachbit',
          version=bleachbit.APP_VERSION,
          description="Free space and maintain privacy",
          long_description="BleachBit frees space and maintains privacy by quickly wiping files you don't need and didn't know you had. Supported applications include Firefox, Flash, Internet Explorer, Java, Opera, Safari, GNOME, and many others.",
          author="Andrew Ziem",
          author_email="andrew@bleachbit.org",
          download_url="https://www.bleachbit.org/download",
          license="GPLv3",
          url=bleachbit.APP_URL,
          platforms='Linux and Windows; Python v2.6 and 2.7; GTK v3.12+',
          packages=['bleachbit'],
          **args)