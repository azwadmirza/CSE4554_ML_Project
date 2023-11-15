    def __init__(self, s3_object):
        self.position = 0
        self._object = s3_object
        self._body = s3_object.get()['Body']