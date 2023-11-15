    def _select_mixer_track(self, mixer, track_label):
        # Look for track with label == MIXER_TRACK, otherwise fallback to
        # master track which is also an output.
        for track in mixer.list_tracks():
            if track_label:
                if track.label == track_label:
                    return track
            elif track.flags & (gst.interfaces.MIXER_TRACK_MASTER |
                                gst.interfaces.MIXER_TRACK_OUTPUT):
                return track