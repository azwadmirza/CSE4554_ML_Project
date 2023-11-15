    def size_for_node(self, node, client):
        '''Given a docutils image node, returns the size the image should have
        in the PDF document, and what 'kind' of size that is.
        That involves lots of guesswork'''

        uri = str(node.get("uri"))
        if uri.split("://")[0].lower() not in ('http','ftp','https'):
            uri = os.path.join(client.basedir,uri)
        else:
            uri, _ = urlretrieve(uri)
            client.to_unlink.append(uri)

        srcinfo = client, uri
        # Extract all the information from the URI
        imgname, extension, options = self.split_uri(uri)

        if not os.path.isfile(imgname):
            imgname = missing

        scale = float(node.get('scale', 100))/100
        size_known = False

        # Figuring out the size to display of an image is ... annoying.
        # If the user provides a size with a unit, it's simple, adjustUnits
        # will return it in points and we're done.

        # However, often the unit wil be "%" (specially if it's meant for
        # HTML originally. In which case, we will use a percentage of
        # the containing frame.

        # Find the image size in pixels:
        kind = 'direct'
        xdpi, ydpi = client.styles.def_dpi, client.styles.def_dpi
        extension = imgname.split('.')[-1].lower()
        if extension in ['svg','svgz']:
            from .svgimage import SVGImage
            iw, ih = SVGImage(imgname, srcinfo=srcinfo).wrap(0, 0)
            # These are in pt, so convert to px
            iw = iw * xdpi / 72
            ih = ih * ydpi / 72

        elif extension == 'pdf':
            if VectorPdf is not None:
                xobj = VectorPdf.load_xobj(srcinfo)
                iw, ih = xobj.w, xobj.h
            else:
                reader = pdfinfo.PdfFileReader(open(imgname, 'rb'))
                box = [float(x) for x in reader.getPage(0)['/MediaBox']]
                iw, ih = x2 - x1, y2 - y1
            # These are in pt, so convert to px
            iw = iw * xdpi / 72.0
            ih = ih * ydpi / 72.0
            size_known = True  # Assume size from original PDF is OK

        else:
            keeptrying = True
            if PILImage:
                try:
                    img = PILImage.open(imgname)
                    img.load()
                    iw, ih = img.size
                    xdpi, ydpi = img.info.get('dpi', (xdpi, ydpi))
                    keeptrying = False
                except IOError: # PIL throws this when it's a broken/unknown image
                    pass
            if keeptrying:
                if extension not in ['jpg', 'jpeg']:
                    log.error("The image (%s, %s) is broken or in an unknown format"
                                , imgname, nodeid(node))
                    raise ValueError
                else:
                    # Can be handled by reportlab
                    log.warning("Can't figure out size of the image (%s, %s). Install PIL for better results."
                                , imgname, nodeid(node))
                    iw = 1000
                    ih = 1000

        # Try to get the print resolution from the image itself via PIL.
        # If it fails, assume a DPI of 300, which is pretty much made up,
        # and then a 100% size would be iw*inch/300, so we pass
        # that as the second parameter to adjustUnits
        #
        # Some say the default DPI should be 72. That would mean
        # the largest printable image in A4 paper would be something
        # like 480x640. That would be awful.
        #

        w = node.get('width')
        h = node.get('height')
        if h is None and w is None: # Nothing specified
            # Guess from iw, ih
            log.debug("Using image %s without specifying size."
                "Calculating based on image size at %ddpi [%s]",
                imgname, xdpi, nodeid(node))
            w = iw*inch/xdpi
            h = ih*inch/ydpi
        elif w is not None:
            # Node specifies only w
            # In this particular case, we want the default unit
            # to be pixels so we work like rst2html
            if w[-1] == '%':
                kind = 'percentage_of_container'
                w=int(w[:-1])
            else:
                # This uses default DPI setting because we
                # are not using the image's "natural size"
                # this is what LaTeX does, according to the
                # docutils mailing list discussion
                w = client.styles.adjustUnits(w, client.styles.tw,
                                            default_unit='px')

            if h is None:
                # h is set from w with right aspect ratio
                h = w*ih/iw
            else:
                h = client.styles.adjustUnits(h, ih*inch/ydpi, default_unit='px')
        elif h is not None and w is None:
            if h[-1] != '%':
                h = client.styles.adjustUnits(h, ih*inch/ydpi, default_unit='px')

                # w is set from h with right aspect ratio
                w = h*iw/ih
            else:
                log.error('Setting height as a percentage does **not** work. '\
                          'ignoring height parameter [%s]', nodeid(node))
                # Set both from image data
                w = iw*inch/xdpi
                h = ih*inch/ydpi

        # Apply scale factor
        w = w*scale
        h = h*scale

        # And now we have this probably completely bogus size!
        log.info("Image %s size calculated:  %fcm by %fcm [%s]",
            imgname, w/cm, h/cm, nodeid(node))

        return w, h, kind