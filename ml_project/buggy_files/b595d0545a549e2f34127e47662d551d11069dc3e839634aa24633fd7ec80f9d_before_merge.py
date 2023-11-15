  def AddEventObjects(self, event_objects):
    """Adds an event objects to the storage.

    Args:
      event_objects: a list or generator of event objects (instances of
                     EventObject).
    """
    for event_object in event_objects:
      self.AddEventObject(event_object)