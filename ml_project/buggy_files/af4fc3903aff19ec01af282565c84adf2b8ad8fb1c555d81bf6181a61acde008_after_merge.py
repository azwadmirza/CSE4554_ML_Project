    def __iter__(self):
      raise self.make_type_error("datatype object is not iterable")