    def __init__(self):
        super(LambdaExecutorSeparateContainers, self).__init__()
        self.next_port = 1
        self.max_port = LAMBDA_API_UNIQUE_PORTS
        self.port_offset = LAMBDA_API_PORT_OFFSET