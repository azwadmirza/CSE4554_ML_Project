    def load_array(filename):
        try:
            name = osp.splitext(osp.basename(filename))[0]
            data = np.load(filename)
            if hasattr(data, 'keys'):
                return data, None
            else:
                return {name: data}, None
        except Exception as error:
            return None, str(error)