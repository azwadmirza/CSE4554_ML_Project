def main(args, error):
    """ CLI entry point for single file conversions """
    del error  # unused

    drspath = Path(args.drs.name)
    outputpath = Path(args.output)

    if args.interfac:
        interfacfile = args.interfac
    else:
        # if no interfac was given, assume
        # the same path of the drs archive.

        interfacfile = drspath.with_name("interfac.drs").open("rb")  # pylint: disable=no-member

    # here, try opening slps from interfac or whereever
    info("opening slp in drs '%s:%s'..." % (drspath, args.slp))
    slpfile = DRS(args.drs).root[args.slp].open("rb")

    # import here to prevent that the __main__ depends on SLP
    # just by importing this singlefile.py.
    from .slp import SLP

    # parse the slp image
    info("parsing slp image...")
    slpimage = SLP(slpfile.read())

    # open color palette
    info("opening palette in drs '%s:%s.bina'..." % (interfacfile.name, args.palette))
    palettefile = DRS(interfacfile).root["%s.bina" % args.palette].open("rb")

    info("parsing palette data...")
    palette = ColorTable(palettefile.read())

    # create texture
    info("packing texture...")
    tex = Texture(slpimage, palette)

    # to save as png:
    tex.save(Directory(outputpath.parent).root, outputpath.name)