    def __init__(self, response):
        message = f"No permision to store the dataset at {response}"
        super().__init__(message=message)