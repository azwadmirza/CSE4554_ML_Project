    def __init__(self, s3_object):
        self.position = 0
        self._object = s3_object
        self._content_length = self._object.content_length