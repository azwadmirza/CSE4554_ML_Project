    def do_GET(self):
        """ Process each GET request and return a value (image or file path)"""
        mask_path = os.path.join(info.IMAGES_PATH, "mask.png")

        # Parse URL
        url_output = REGEX_THUMBNAIL_URL.match(self.path)
        if url_output and len(url_output.groups()) == 4:
            # Path is expected to have 3 matched components (third is optional though)
            #   /thumbnails/FILE-ID/FRAME-NUMBER/   or
            #   /thumbnails/FILE-ID/FRAME-NUMBER/path/  or
            #   /thumbnails/FILE-ID/FRAME-NUMBER/no-cache/  or
            #   /thumbnails/FILE-ID/FRAME-NUMBER/path/no-cache/
            self.send_response_only(200)
        else:
            self.send_error(404)
            return

        # Get URL parts
        file_id = url_output.group('file_id')
        file_frame = int(url_output.group('file_frame'))
        only_path = url_output.group('only_path')
        no_cache = url_output.group('no_cache')

        log.debug(
            "Processing thumbnail request for %s frame %d",
            file_id, file_frame)

        try:
            # Look up file data
            file = File.get(id=file_id)

            # Ensure file location is an absolute path
            file_path = file.absolute_path()
        except AttributeError:
            # Couldn't match file ID
            log.debug("No ID match, returning 404")
            self.send_error(404)
            return

        # Send headers
        if not only_path:
            self.send_header('Content-type', 'image/png')
        else:
            self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Locate thumbnail
        thumb_path = os.path.join(info.THUMBNAIL_PATH, file_id, "%s.png" % file_frame)
        if not os.path.exists(thumb_path) and file_frame == 1:
            # Try ID with no frame # (for backwards compatibility)
            thumb_path = os.path.join(info.THUMBNAIL_PATH, "%s.png" % file_id)
        if not os.path.exists(thumb_path) and file_frame != 1:
            # Try with ID and frame # in filename (for backwards compatibility)
            thumb_path = os.path.join(info.THUMBNAIL_PATH, "%s-%s.png" % (file_id, file_frame))

        if not os.path.exists(thumb_path) or no_cache:
            # Generate thumbnail (since we can't find it)

            # Determine if video overlay should be applied to thumbnail
            overlay_path = ""
            if file.data["media_type"] == "video":
                overlay_path = os.path.join(info.IMAGES_PATH, "overlay.png")

            # Create thumbnail image
            GenerateThumbnail(
                file_path,
                thumb_path,
                file_frame,
                98, 64,
                mask_path,
                overlay_path)

        # Send message back to client
        if os.path.exists(thumb_path):
            if not only_path:
                self.wfile.write(open(thumb_path, 'rb').read())
            else:
                self.wfile.write(bytes(thumb_path, "utf-8"))

        # Pause processing of request (since we don't currently use thread pooling, this allows
        # the threads to be processed without choking the CPU as much
        # TODO: Make HTTPServer work with a limited thread pool and remove this sleep() hack.
        time.sleep(0.01)