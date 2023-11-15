    def _reset_state(self):
        """Reinitializes the state of the parser. Used internally at
        initialization and at the end of the parsing process.
        """
        # could be 2 possible types of metadata:
        #   - file_metadata: Metadata of the container. Here are the tags setted
        #     by the user using `-metadata` ffmpeg option
        #   - stream_metadata: Metadata for each stream of the container.
        self._inside_file_metadata = False

        # this state is neeeded if `duration_tag_separator == "time="` because
        # execution of ffmpeg decoding the whole file using `-f null -` appends
        # to the output a the blocks "Stream mapping:" and "Output:", which
        # should be ignored
        self._inside_output = False

        # flag which indicates that a default stream has not been found yet
        self._default_stream_found = False

        # current input file, stream and chapter, which will be built at runtime
        self._current_input_file = {"streams": []}
        self._current_stream = None
        self._current_chapter = None

        # resulting data of the parsing process
        self.result = {
            "video_found": False,
            "audio_found": False,
            "metadata": {},
            "inputs": [],
        }