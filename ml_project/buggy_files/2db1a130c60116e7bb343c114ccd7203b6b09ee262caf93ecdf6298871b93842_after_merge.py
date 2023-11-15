    def __init__(self, variable, access_type, location):
        self.variable = variable
        self.access_type = access_type
        self.location: 'CodeLocation' = location