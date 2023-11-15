    def report_progress(self, s):
        if s['status'] == 'finished':
            if self.params.get('noprogress', False):
                self.to_screen('[download] Download completed')
            else:
                if s.get('total_bytes') is not None:
                    s['_total_bytes_str'] = format_bytes(s['total_bytes'])
                    msg_template = '100%% of %(_total_bytes_str)s'
                else:
                    msg_template = 'Completed'
                if s.get('elapsed') is not None:
                    s['_elapsed_str'] = self.format_seconds(s['elapsed'])
                    msg_template += ' in %(_elapsed_str)s'
                self._report_progress_status(
                    msg_template % s, is_last_line=True)

        if self.params.get('noprogress'):
            return

        if s['status'] != 'downloading':
            return

        if s.get('eta') is not None:
            s['_eta_str'] = self.format_eta(s['eta'])
        else:
            s['_eta_str'] = 'Unknown ETA'

        if s.get('total_bytes') and s.get('downloaded_bytes') is not None:
            s['_percent_str'] = self.format_percent(100 * s['downloaded_bytes'] / s['total_bytes'])
        elif s.get('total_bytes_estimate') and s.get('downloaded_bytes') is not None:
            s['_percent_str'] = self.format_percent(100 * s['downloaded_bytes'] / s['total_bytes_estimate'])
        else:
            if s.get('downloaded_bytes') == 0:
                s['_percent_str'] = self.format_percent(0)
            else:
                s['_percent_str'] = 'Unknown %'

        if s.get('speed') is not None:
            s['_speed_str'] = self.format_speed(s['speed'])
        else:
            s['_speed_str'] = 'Unknown speed'

        if s.get('total_bytes') is not None:
            s['_total_bytes_str'] = format_bytes(s['total_bytes'])
            msg_template = '%(_percent_str)s of %(_total_bytes_str)s at %(_speed_str)s ETA %(_eta_str)s'
        elif s.get('total_bytes_estimate') is not None:
            s['_total_bytes_estimate_str'] = format_bytes(s['total_bytes_estimate'])
            msg_template = '%(_percent_str)s of ~%(_total_bytes_estimate_str)s at %(_speed_str)s ETA %(_eta_str)s'
        else:
            if s.get('downloaded_bytes') is not None:
                s['_downloaded_bytes_str'] = format_bytes(s['downloaded_bytes'])
                if s.get('elapsed'):
                    s['_elapsed_str'] = self.format_seconds(s['elapsed'])
                    msg_template = '%(_downloaded_bytes_str)s at %(_speed_str)s (%(_elapsed_str)s)'
                else:
                    msg_template = '%(_downloaded_bytes_str)s at %(_speed_str)s'
            else:
                msg_template = '%(_percent_str)s % at %(_speed_str)s ETA %(_eta_str)s'

        self._report_progress_status(msg_template % s)