    def __init__(self, name, source_code, position, filename=None,
            is_python_like=True, in_comment_or_string=False, **kwargs):
        self.__dict__.update(kwargs)
        self.name = name
        self.filename = filename
        self.source_code = source_code
        self.is_python_like = is_python_like
        self.in_comment_or_string = in_comment_or_string
        self.position = position

        # if in a comment, look for the previous definition
        if in_comment_or_string:
            # if this is a docstring, find it, set as our
            self.docstring = self._get_docstring()
            # backtrack and look for a line that starts with def or class
            while position:
                base = self.source_code[position: position + 6]
                if base.startswith('def ') or base.startswith('class '):
                    position += base.index(' ') + 1
                    break
                position -= 1
        else:
            self.docstring = ''

        self.position = position

        if position == 0:
            self.lines = []
            self.column = 0
            self.line_num = 0
            self.line = ''
            self.obj = ''
            self.full_obj = ''
        else:
            self._get_info()