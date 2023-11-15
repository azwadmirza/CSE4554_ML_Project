    def to_pytorch(self, transform=None, max_text_len=30):
        """
        Transforms into pytorch dataset

        Parameters
        ----------
        transform: func
            any transform that takes input a dictionary of a sample and returns transformed dictionary
        max_text_len: integer
            the maximum length of text strings that would be stored. Strings longer than this would be snipped
        """
        try:
            import torch

            global torch
        except ImportError:
            pass
        return TorchDataset(self, transform, max_text_len)