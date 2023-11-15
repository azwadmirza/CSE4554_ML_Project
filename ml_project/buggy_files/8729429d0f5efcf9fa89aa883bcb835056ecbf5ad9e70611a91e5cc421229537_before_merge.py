        def write_header_line(fd, header_field, header_content):
            """Write comment header line."""
            if header_content is None:
                return
            header_content = str(header_content).replace('\n', ' ')
            line = '.. ' + header_field + ': ' + header_content + '\n'
            fd.write(line.encode('utf8'))