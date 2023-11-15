  def __init__(self, num_classes, **kwargs):
    self.num_classes = num_classes
    if 'version' not in kwargs:
      kwargs['version'] = tfds.core.Version('1.1.0')
    super(VisualDomainDecathlonConfig, self).__init__(**kwargs)