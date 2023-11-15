  def print_prediction(self, prediction, params=None, stream=None):
    print(prediction["classes"], file=stream)