def pdf_preview(tmp_file_path, tmp_dir):
    if use_generic_pdf_cover:
        return None
    else:
        try:
            input1 = PdfFileReader(open(tmp_file_path, 'rb'), strict=False)
            page0 = input1.getPage(0)
            xObject = page0['/Resources']['/XObject'].getObject()

            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                    data = xObject[obj]._data # xObject[obj].getData()
                    if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                        mode = "RGB"
                    else:
                        mode = "P"
                    if '/Filter' in xObject[obj]:
                        if xObject[obj]['/Filter'] == '/FlateDecode':
                            img = Image.frombytes(mode, size, data)
                            cover_file_name = os.path.splitext(tmp_file_path)[0] + ".cover.png"
                            img.save(filename=os.path.join(tmp_dir, cover_file_name))
                            return cover_file_name
                            # img.save(obj[1:] + ".png")
                        elif xObject[obj]['/Filter'] == '/DCTDecode':
                            cover_file_name = os.path.splitext(tmp_file_path)[0] + ".cover.jpg"
                            img = open(cover_file_name, "wb")
                            img.write(data)
                            img.close()
                            return cover_file_name
                        elif xObject[obj]['/Filter'] == '/JPXDecode':
                            cover_file_name = os.path.splitext(tmp_file_path)[0] + ".cover.jp2"
                            img = open(cover_file_name, "wb")
                            img.write(data)
                            img.close()
                            return cover_file_name
                    else:
                        img = Image.frombytes(mode, size, data)
                        cover_file_name = os.path.splitext(tmp_file_path)[0] + ".cover.png"
                        img.save(filename=os.path.join(tmp_dir, cover_file_name))
                        return cover_file_name
                        # img.save(obj[1:] + ".png")
        except Exception as ex:
            print(ex)

        try:
            cover_file_name = os.path.splitext(tmp_file_path)[0] + ".cover.jpg"
            with Image(filename=tmp_file_path + "[0]", resolution=150) as img:
                img.compression_quality = 88
                img.save(filename=os.path.join(tmp_dir, cover_file_name))
            return cover_file_name
        except PolicyError as ex:
            logger.warning('Pdf extraction forbidden by Imagemagick policy: %s', ex)
            return None
        except Exception as ex:
            logger.warning('Cannot extract cover image, using default: %s', ex)
            return None