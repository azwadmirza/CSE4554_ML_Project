    def read_mda(attribute):
        """Read HDFEOS metadata and return a dict with all the key/value pairs."""
        lines = attribute.split('\n')
        mda = {}
        current_dict = mda
        path = []
        prev_line = None
        for line in lines:
            if not line:
                continue
            if line == 'END':
                break
            if prev_line:
                line = prev_line + line
            key, val = line.split('=')
            key = key.strip()
            val = val.strip()
            try:
                val = eval(val)
            except NameError:
                pass
            except SyntaxError:
                prev_line = line
                continue
            prev_line = None
            if key in ['GROUP', 'OBJECT']:
                new_dict = {}
                path.append(val)
                current_dict[val] = new_dict
                current_dict = new_dict
            elif key in ['END_GROUP', 'END_OBJECT']:
                if val != path[-1]:
                    raise SyntaxError
                path = path[:-1]
                current_dict = mda
                for item in path:
                    current_dict = current_dict[item]
            elif key in ['CLASS', 'NUM_VAL']:
                pass
            else:
                current_dict[key] = val
        return mda