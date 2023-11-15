    def __init__(self):
        """
        Create an instance of the job store. The instance will not be fully functional until
        either :meth:`.initialize` or :meth:`.resume` is invoked. Note that the :meth:`.destroy`
        method may be invoked on the object with or without prior invocation of either of these two
        methods.
        """
        self.__config = None