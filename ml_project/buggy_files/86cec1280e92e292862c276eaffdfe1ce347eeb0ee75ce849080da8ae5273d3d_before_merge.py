    def export_archive(self, trans, id=None, gzip=True, include_hidden=False, include_deleted=False, preview=False):
        """ Export a history to an archive. """
        #
        # Get history to export.
        #
        if id:
            history = self.history_manager.get_accessible(self.decode_id(id), trans.user, current_history=trans.history)
        else:
            # Use current history.
            history = trans.history
            id = trans.security.encode_id(history.id)
        if not history:
            return trans.show_error_message("This history does not exist or you cannot export this history.")
        # If history has already been exported and it has not changed since export, stream it.
        jeha = history.latest_export
        if jeha and jeha.up_to_date:
            if jeha.ready:
                if preview:
                    url = url_for(controller='history', action="export_archive", id=id, qualified=True)
                    return trans.show_message("History Ready: '%(n)s'. Use this link to download "
                                              "the archive or import it to another Galaxy server: "
                                              "<a href='%(u)s'>%(u)s</a>" % ({'n': history.name, 'u': url}))
                else:
                    return self.serve_ready_history_export(trans, jeha)
            elif jeha.preparing:
                return trans.show_message("Still exporting history %(n)s; please check back soon. Link: <a href='%(s)s'>%(s)s</a>"
                                          % ({'n': history.name, 's': url_for(controller='history', action="export_archive", id=id, qualified=True)}))
        self.queue_history_export(trans, history, gzip=gzip, include_hidden=include_hidden, include_deleted=include_deleted)
        url = url_for(controller='history', action="export_archive", id=id, qualified=True)
        return trans.show_message("Exporting History '%(n)s'. You will need to <a href='%(share)s'>make this history 'accessible'</a> in order to import this to another galaxy sever. <br/>"
                                  "Use this link to download the archive or import it to another Galaxy server: "
                                  "<a href='%(u)s'>%(u)s</a>" % ({'share': url_for(controller='history', action='sharing'), 'n': history.name, 'u': url}))