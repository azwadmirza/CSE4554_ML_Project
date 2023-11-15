    def caller_attributes(cls, module_name: str = '') -> Tuple[str, str, str]:
        """
        Determine extra or changed fields for the caller.

        1. qualname finds the relevant object and its __qualname__
        2. caller_class_names is just the full class names of the calling
         class if relevant.
        3. module is munged if we detect the caller is an EDMC plugin,
         whether internal or found.
        """
        frame = cls.find_caller_frame()

        caller_qualname = caller_class_names = ''
        if frame:
            # <https://stackoverflow.com/questions/2203424/python-how-to-retrieve-class-information-from-a-frame-object#2220759>
            frame_info = inspect.getframeinfo(frame)
            args, _, _, value_dict = inspect.getargvalues(frame)
            if len(args) and args[0] in ('self', 'cls'):
                frame_class: 'object' = value_dict[args[0]]

                if frame_class:
                    # See https://en.wikipedia.org/wiki/Name_mangling#Python for how name mangling works.
                    name = frame_info.function
                    if name.startswith("__") and not name.endswith("__"):
                        name = f'_{frame_class.__class__.__name__}{frame_info.function}'

                    # Find __qualname__ of the caller
                    fn = getattr(frame_class, name, None)
                    if fn and fn.__qualname__:
                        caller_qualname = fn.__qualname__

                    # Find containing class name(s) of caller, if any
                    if frame_class.__class__ and frame_class.__class__.__qualname__:
                        caller_class_names = frame_class.__class__.__qualname__

            # It's a call from the top level module file
            elif frame_info.function == '<module>':
                caller_class_names = '<none>'
                caller_qualname = value_dict['__name__']

            elif frame_info.function != '':
                caller_class_names = '<none>'
                caller_qualname = frame_info.function

            module_name = cls.munge_module_name(frame_info, module_name)

            # https://docs.python.org/3.7/library/inspect.html#the-interpreter-stack
            del frame

        if caller_qualname == '':
            print('ALERT!  Something went wrong with finding caller qualname for logging!')
            caller_qualname = '<ERROR in EDMCLogging.caller_class_and_qualname() for "qualname">'

        if caller_class_names == '':
            print('ALERT!  Something went wrong with finding caller class name(s) for logging!')
            caller_class_names = '<ERROR in EDMCLogging.caller_class_and_qualname() for "class">'

        return caller_class_names, caller_qualname, module_name