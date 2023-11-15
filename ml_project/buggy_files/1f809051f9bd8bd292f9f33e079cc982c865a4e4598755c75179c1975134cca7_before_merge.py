  def print_prediction(self, prediction, params=None, stream=None):
    tags = prediction["tags"][:prediction["length"]]
    sent = b" ".join(tags)
    print(sent.decode("utf-8"), file=stream)