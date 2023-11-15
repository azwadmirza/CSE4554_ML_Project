    def from_content_disposition(self, content_disposition):
        try:
            filename = to_native_str(content_disposition,
                encoding='latin-1', errors='replace').split(';')[1].split('=')[1]
            filename = filename.strip('"\'')
            return self.from_filename(filename)
        except IndexError:
            return Response