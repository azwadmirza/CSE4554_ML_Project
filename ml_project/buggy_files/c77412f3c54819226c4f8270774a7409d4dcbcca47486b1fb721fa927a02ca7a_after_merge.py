def bootstrap():
    # This function is called when setuptools*.egg is run using /bin/sh
    if "__PEX_UNVENDORED__" in __import__("os").environ:
      import setuptools  # vendor:skip
    else:
      import pex.third_party.setuptools as setuptools


    argv0 = os.path.dirname(setuptools.__path__[0])
    sys.argv[0] = argv0
    sys.argv.append(argv0)
    main()