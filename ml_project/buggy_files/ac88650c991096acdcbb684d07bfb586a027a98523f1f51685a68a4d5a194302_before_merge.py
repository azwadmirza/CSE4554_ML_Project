        def __deepcopy__(self, memo):
            cls = self.__class__
            result = cls.__new__(cls, self.start_mark, self.end_mark)
            memo[id(self)] = result
            for _, v in enumerate(self):
                result.append(deepcopy(v, memo))

            return result