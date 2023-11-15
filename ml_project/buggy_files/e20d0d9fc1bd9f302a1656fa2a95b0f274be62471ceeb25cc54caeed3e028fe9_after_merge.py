    def __setattr__(self, key, value):
        # 内建属性不放入 key 中
        if key.startswith('__') and key.endswith('__'):
            super().__setattr__(key, value)
        else:
            self[key] = value