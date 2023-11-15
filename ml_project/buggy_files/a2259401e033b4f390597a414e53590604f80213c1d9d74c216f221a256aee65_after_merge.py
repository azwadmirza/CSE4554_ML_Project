    def _write_comment(self, filename, comment):
        """Write comment to file."""
        def write_header_line(fd, header_field, header_content):
            """Write comment header line."""
            if header_content is None:
                return
            header_content = unicode_str(header_content).replace('\n', ' ')
            line = '.. ' + header_field + ': ' + header_content + '\n'
            fd.write(line.encode('utf8'))

        with open(filename, "wb+") as fd:
            write_header_line(fd, "id", comment["id"])
            write_header_line(fd, "status", comment["status"])
            write_header_line(fd, "approved", comment["approved"])
            write_header_line(fd, "author", comment["author"])
            write_header_line(fd, "author_email", comment["email"])
            write_header_line(fd, "author_url", comment["url"])
            write_header_line(fd, "author_IP", comment["ip"])
            write_header_line(fd, "date_utc", comment["date"])
            write_header_line(fd, "parent_id", comment["parent"])
            write_header_line(fd, "wordpress_user_id", comment["user_id"])
            fd.write(('\n' + comment['content']).encode('utf8'))