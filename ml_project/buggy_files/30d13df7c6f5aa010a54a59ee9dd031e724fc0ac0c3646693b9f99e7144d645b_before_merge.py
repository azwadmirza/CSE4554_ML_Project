def cmp(rpin, rpout):
    """True if rpin has the same data as rpout

    cmp does not compare file ownership, permissions, or times, or
    examine the contents of a directory.

    """
    check_for_files(rpin, rpout)
    if rpin.isreg():
        if not rpout.isreg():
            return None
        fp1, fp2 = rpin.open("rb"), rpout.open("rb")
        result = cmpfileobj(fp1, fp2)
        if fp1.close() or fp2.close():
            raise RPathException("Error closing file")
        return result
    elif rpin.isdir():
        return rpout.isdir()
    elif rpin.issym():
        return rpout.issym() and (rpin.readlink() == rpout.readlink())
    elif rpin.ischardev():
        return rpout.ischardev() and (rpin.getdevnums() == rpout.getdevnums())
    elif rpin.isblkdev():
        return rpout.isblkdev() and (rpin.getdevnums() == rpout.getdevnums())
    elif rpin.isfifo():
        return rpout.isfifo()
    elif rpin.issock():
        return rpout.issock()
    else:
        raise RPathException("File %s has unknown type" % rpin.get_safepath())