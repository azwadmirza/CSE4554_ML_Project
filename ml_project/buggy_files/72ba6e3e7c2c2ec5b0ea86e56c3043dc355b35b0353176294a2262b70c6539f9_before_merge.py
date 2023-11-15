    def wrapper(*args, **kwargs):
        queue = Queue()
        proc = Process(target=inner_f, args=(queue, func,), kwargs=kwargs)
        proc.start()
        proc.join()
        return queue.get()