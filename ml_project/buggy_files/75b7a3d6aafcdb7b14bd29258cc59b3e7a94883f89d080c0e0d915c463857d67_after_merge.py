    def set_items(self, data, new_items, indexes):
        if type(data) in [list, tuple]:
            data_out = data.copy() if isinstance(data, list) else list(data)
            params = list_match_func[self.list_match_local]([indexes, new_items])
            for ind, i in zip(*params):
                if self.replace and len(data_out) > ind:
                    data_out.pop(ind)
                data_out.insert(ind, i)
            return data_out
        elif type(data) == np.ndarray:
            out_data = np.array(data)
            ind, items = list_match_func[self.list_match_local]([indexes, new_items])
            if self.replace:
                out_data[ind] = items

            else:
                for i, item in zip(ind, items):
                    out_data = np.concatenate([data[:i], [item], data[i:]])

            return out_data
        elif type(data) == str:
            ind, items = list_match_func[self.list_match_local]([indexes, new_items])

            add_one = 1 if self.replace else 0
            out_data = data
            for i, item in zip(ind, items):
                out_data = out_data[:i]+ str(item) + out_data[i+add_one:]
            return out_data
        return None