    def parse(self):
        """Parses the information returned by FFmpeg in stderr executing their binary
        for a file with ``-i`` option and returns a dictionary with all data needed
        by MoviePy.
        """
        result = {
            "video_found": False,
            "audio_found": False,
            "metadata": {},
            "inputs": [],
        }
        # chapters by input file
        input_chapters = []

        for line in self.infos.splitlines()[1:]:
            if (
                self.duration_tag_separator == "time="
                and self.check_duration
                and "time=" in line
            ):
                # parse duration using file decodification
                result["duration"] = self.parse_duration(line)
            elif self._inside_output or line[0] != " ":
                if self.duration_tag_separator == "time=" and not self._inside_output:
                    self._inside_output = True
                # skip lines like "At least one output file must be specified"
            elif not self._inside_file_metadata and line.startswith("  Metadata:"):
                # enter "  Metadata:" group
                self._inside_file_metadata = True
            elif line.startswith("  Duration:"):
                # exit "  Metadata:" group
                self._inside_file_metadata = False
                if self.check_duration and self.duration_tag_separator == "Duration: ":
                    result["duration"] = self.parse_duration(line)

                # parse global bitrate (in kb/s)
                bitrate_match = re.search(r"bitrate: (\d+) kb/s", line)
                result["bitrate"] = (
                    int(bitrate_match.group(1)) if bitrate_match else None
                )

                # parse start time (in seconds)
                start_match = re.search(r"start: (\d+\.?\d+)", line)
                result["start"] = float(start_match.group(1)) if start_match else None
            elif self._inside_file_metadata:
                # file metadata line
                field, value = self.parse_metadata_field_value(line)
                result["metadata"].update({field: value})
            elif line.startswith("    Stream "):
                # exit stream "    Metadata:"
                if self._current_stream:
                    self._current_input_file["streams"].append(self._current_stream)

                # get input number, stream number, language and type
                main_info_match = re.search(
                    r"^\s{4}Stream\s#(\d+):(\d+)\(?(\w+)?\)?:\s(\w+):", line
                )
                (
                    input_number,
                    stream_number,
                    language,
                    stream_type,
                ) = main_info_match.groups()
                input_number = int(input_number)
                stream_number = int(stream_number)
                stream_type_lower = stream_type.lower()

                # start builiding the current stream
                self._current_stream = {
                    "input_number": input_number,
                    "stream_number": stream_number,
                    "stream_type": stream_type_lower,
                    "language": language if language != "und" else None,
                    "default": not self._default_stream_found
                    or line.endswith("(default)"),
                }
                self._default_stream_found = True

                # for default streams, set their numbers globally, so it's
                # easy to get without iterating all
                if self._current_stream["default"]:
                    result[f"default_{stream_type_lower}_input_number"] = input_number
                    result[f"default_{stream_type_lower}_stream_number"] = stream_number

                # exit chapter
                if self._current_chapter:
                    input_chapters[input_number].append(self._current_chapter)
                    self._current_chapter = None

                if "input_number" not in self._current_input_file:
                    # first input file
                    self._current_input_file["input_number"] = input_number
                elif self._current_input_file["input_number"] != input_number:
                    # new input file

                    # include their chapters if there are for this input file
                    if len(input_chapters) >= input_number + 1:
                        self._current_input_file["chapters"] = input_chapters[
                            input_number
                        ]

                    # add new input file to result
                    result["inputs"].append(self._current_input_file)
                    self._current_input_file = {"input_number": input_number}

                # parse relevant data by stream type
                try:
                    global_data, stream_data = self.parse_data_by_stream_type(
                        stream_type, line
                    )
                except NotImplementedError as exc:
                    warnings.warn(
                        f"{str(exc)}\nffmpeg output:\n\n{self.infos}", UserWarning
                    )
                else:
                    result.update(global_data)
                    self._current_stream.update(stream_data)
            elif line.startswith("    Metadata:"):
                # enter group "    Metadata:"
                continue
            elif self._current_stream:
                # stream metadata line
                if "metadata" not in self._current_stream:
                    self._current_stream["metadata"] = {}

                field, value = self.parse_metadata_field_value(line)
                if self._current_stream["stream_type"] == "video":
                    field, value = self.video_metadata_type_casting(field, value)
                    if field == "rotate":
                        result["video_rotation"] = value
                self._current_stream["metadata"][field] = value
            elif line.startswith("    Chapter"):
                # Chapter data line
                if self._current_chapter:
                    # there is a previews chapter?
                    if len(input_chapters) < self._current_chapter["input_number"] + 1:
                        input_chapters.append([])
                    # include in the chapters by input matrix
                    input_chapters[self._current_chapter["input_number"]].append(
                        self._current_chapter
                    )

                # extract chapter data
                chapter_data_match = re.search(
                    r"^    Chapter #(\d+):(\d+): start (\d+\.?\d+?), end (\d+\.?\d+?)",
                    line,
                )
                input_number, chapter_number, start, end = chapter_data_match.groups()

                # start building the chapter
                self._current_chapter = {
                    "input_number": int(input_number),
                    "chapter_number": int(chapter_number),
                    "start": float(start),
                    "end": float(end),
                }
            elif self._current_chapter:
                # inside chapter metadata
                if "metadata" not in self._current_chapter:
                    self._current_chapter["metadata"] = {}
                field, value = self.parse_metadata_field_value(line)
                self._current_chapter["metadata"][field] = value

        # last input file, must be included in the result
        if self._current_input_file:
            self._current_input_file["streams"].append(self._current_stream)
            # include their chapters, if there are
            if len(input_chapters) == self._current_input_file["input_number"] + 1:
                self._current_input_file["chapters"] = input_chapters[
                    self._current_input_file["input_number"]
                ]
            result["inputs"].append(self._current_input_file)

        # some video duration utilities
        if result["video_found"] and self.check_duration:
            result["video_n_frames"] = int(result["duration"] * result["video_fps"])
            result["video_duration"] = result["duration"]
        else:
            result["video_n_frames"] = 1
            result["video_duration"] = None
        # We could have also recomputed duration from the number of frames, as follows:
        # >>> result['video_duration'] = result['video_n_frames'] / result['video_fps']

        # reset state of the parser
        self._reset_state()

        return result