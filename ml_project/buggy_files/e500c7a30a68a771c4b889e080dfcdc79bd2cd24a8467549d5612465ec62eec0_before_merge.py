    def __init__(self, celery_executor, kubernetes_executor):
        super().__init__()
        self.celery_executor = celery_executor
        self.kubernetes_executor = kubernetes_executor