    def train_dataloader(self):
        normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        )

        train_dir = os.path.join(self.hparams.data, 'train')
        train_dataset = datasets.ImageFolder(
            train_dir,
            transforms.Compose([
                transforms.RandomResizedCrop(224),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                normalize,
            ]))

        if self.use_ddp:
            train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset)
        else:
            train_sampler = None

        train_loader = torch.utils.data.DataLoader(
            dataset=train_dataset,
            batch_size=self.hparams.batch_size,
            shuffle=(train_sampler is None),
            num_workers=0,
            sampler=train_sampler
        )
        return train_loader