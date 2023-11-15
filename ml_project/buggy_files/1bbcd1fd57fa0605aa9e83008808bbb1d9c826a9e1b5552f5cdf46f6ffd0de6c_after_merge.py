def pdf_preview(tmp_file_path, tmp_dir):
    if use_generic_pdf_cover:
        return None
    else:
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