    def __init__(self, clips):
        self.clips = clips
        self.nchannels = max(clip.nchannels for clip in self.clips)

        # self.duration is setted at AudioClip
        duration = None
        for end in self.ends:
            if end is None:
                break
            duration = max(end, duration or 0)

        # self.fps is setted at AudioClip
        fps = None
        for clip in self.clips:
            if hasattr(clip, "fps") and isinstance(clip.fps, numbers.Number):
                fps = max(clip.fps, fps or 0)

        super().__init__(duration=duration, fps=fps)