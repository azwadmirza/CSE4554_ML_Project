    def _handle_object_info_reply(self, rep):
        """ Handle replies for call tips.
        """
        cursor = self._get_cursor()
        info = self._request_info.get('call_tip')
        if info and info.id == rep['parent_header']['msg_id'] and \
                info.pos == cursor.position():
            # Get the information for a call tip.  For now we format the call
            # line as string, later we can pass False to format_call and
            # syntax-highlight it ourselves for nicer formatting in the
            # calltip.
            if rep['content']['ismagic']:
                # Don't generate a call-tip for magics. Ideally, we should
                # generate a tooltip, but not on ( like we do for actual
                # callables.
                call_info, doc = None, None
            else:
                call_info, doc = call_tip(rep['content'], format_call=True)
            if call_info or doc:
                self._call_tip_widget.show_call_info(call_info, doc)