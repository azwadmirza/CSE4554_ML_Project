def main():  # needed for console script
    if __package__ == '':
        # To be able to run 'python wheel-0.9.whl/wheel':
        import os.path
        path = os.path.dirname(os.path.dirname(__file__))
        sys.path[0:0] = [path]
    if "__PEX_UNVENDORED__" in __import__("os").environ:
      import wheel.tool  # vendor:skip
    else:
      import pex.third_party.wheel.tool, pex.third_party.wheel as wheel

    sys.exit(wheel.tool.main())