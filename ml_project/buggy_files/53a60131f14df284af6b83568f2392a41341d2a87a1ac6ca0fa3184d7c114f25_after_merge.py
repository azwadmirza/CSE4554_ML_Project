    def display(self, trans, history_content_id, history_id,
                preview=False, filename=None, to_ext=None, raw=False, **kwd):
        """
        GET /api/histories/{encoded_history_id}/contents/{encoded_content_id}/display
        Displays history content (dataset).

        The query parameter 'raw' should be considered experimental and may be dropped at
        some point in the future without warning. Generally, data should be processed by its
        datatype prior to display (the defult if raw is unspecified or explicitly false.
        """
        decoded_content_id = self.decode_id(history_content_id)
        raw = util.string_as_bool_or_none(raw)

        rval = ''
        try:
            hda = self.hda_manager.get_accessible(decoded_content_id, trans.user)
            if raw:
                if filename and filename != 'index':
                    object_store = trans.app.object_store
                    dir_name = hda.dataset.extra_files_path_name
                    file_path = object_store.get_filename(hda.dataset,
                                                          extra_dir=dir_name,
                                                          alt_name=filename)
                else:
                    file_path = hda.file_name
                rval = open(file_path, 'rb')
            else:
                display_kwd = kwd.copy()
                if 'key' in display_kwd:
                    del display_kwd["key"]
                rval = hda.datatype.display_data(trans, hda, preview, filename, to_ext, **display_kwd)
        except galaxy_exceptions.MessageException:
            raise
        except Exception as e:
            log.exception("Server error getting display data for dataset (%s) from history (%s)",
                          history_content_id, history_id)
            raise galaxy_exceptions.InternalServerError(f"Could not get display data for dataset: {util.unicodify(e)}")
        return rval