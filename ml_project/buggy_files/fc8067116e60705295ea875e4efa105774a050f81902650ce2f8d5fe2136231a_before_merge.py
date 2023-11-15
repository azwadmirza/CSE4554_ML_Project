    def __repr__(self):
        string = (
            f'{self.__class__.__name__}'
            f'(Keys: {tuple(self.keys())}; images: {len(self.images)})'
        )
        return string