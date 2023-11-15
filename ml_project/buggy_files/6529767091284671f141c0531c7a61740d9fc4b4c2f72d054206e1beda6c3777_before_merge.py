def get_book_cover(cover_path):
    if ub.config.config_use_google_drive:
        try:
            path=gd.get_cover_via_gdrive(cover_path)
            if path:
                return redirect(path)
            else:
                web.app.logger.error(cover_path + '/cover.jpg not found on Google Drive')
                return send_from_directory(os.path.join(os.path.dirname(__file__), "static"), "generic_cover.jpg")
        except Exception as e:
            web.app.logger.error("Error Message: "+e.message)
            web.app.logger.exception(e)
            # traceback.print_exc()
            return send_from_directory(os.path.join(os.path.dirname(__file__), "static"),"generic_cover.jpg")
    else:
        return send_from_directory(os.path.join(ub.config.config_calibre_dir, cover_path), "cover.jpg")