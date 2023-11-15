def hashlib_new(context):
    if isinstance(context.call_function_name_qual, str):
        qualname_list = context.call_function_name_qual.split('.')
        func = qualname_list[-1]
        if 'hashlib' in qualname_list and func == 'new':
            args = context.call_args
            keywords = context.call_keywords
            name = args[0] if args else keywords['name']
            if isinstance(name, str) and name.lower() in ('md4', 'md5'):
                return bandit.Issue(
                    severity=bandit.MEDIUM,
                    confidence=bandit.HIGH,
                    text="Use of insecure MD4 or MD5 hash function.",
                    lineno=context.node.lineno,
                )