        def __deepcopy__(self, memo):
            cls = self.__class__
            result = cls.__new__(cls, self.start_mark, self.end_mark)
            memo[id(self)] = result
            for k, v in self.items():
                result[deepcopy(k)] = deepcopy(v, memo)

            return result