            def on_header(hdr):
                if write_body[1] is not False and write_body[2] is None:
                    # Try to find out what content type encoding is used if this is a text file
                    write_body[1].parse_line(hdr)  # pylint: disable=no-member
                    if 'Content-Type' in write_body[1]:
                        content_type = write_body[1].get('Content-Type')  # pylint: disable=no-member
                        if not content_type.startswith('text'):
                            write_body[1] = write_body[2] = False
                        else:
                            encoding = 'utf-8'
                            fields = content_type.split(';')
                            for field in fields:
                                if 'encoding' in field:
                                    encoding = field.split('encoding=')[-1]
                            write_body[2] = encoding
                            # We have found our encoding. Stop processing headers.
                            write_body[1] = False

                if write_body[0] is not None:
                    # We already parsed the first line. No need to run the code below again
                    return

                try:
                    hdr = parse_response_start_line(hdr)
                except HTTPInputError:
                    # Not the first line, do nothing
                    return
                write_body[0] = hdr.code not in [301, 302, 303, 307]
                write_body[1] = HTTPHeaders()