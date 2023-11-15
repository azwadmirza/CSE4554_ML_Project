    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(parent)

        # Populate dropdowns
        self.repoSelector.model().item(0).setEnabled(False)
        self.repoSelector.addItem(self.tr('+ Initialize New Repository'), 'new')
        self.repoSelector.addItem(self.tr('+ Add Existing Repository'), 'existing')
        self.repoSelector.insertSeparator(3)
        for repo in RepoModel.select():
            self.repoSelector.addItem(repo.url, repo.id)

        self.repoSelector.currentIndexChanged.connect(self.repo_select_action)
        self.repoRemoveToolbutton.clicked.connect(self.repo_unlink_action)

        # note: it is hard to describe these algorithms with attributes like low/medium/high
        # compression or speed on a unified scale. this is not 1-dimensional and also depends
        # on the input data. so we just tell what we know for sure.
        # "auto" is used for some slower / older algorithms to avoid wasting a lot of time
        # on uncompressible data.
        self.repoCompression.addItem(self.tr('LZ4 (modern, default)'), 'lz4')
        self.repoCompression.addItem(self.tr('Zstandard Level 3 (modern)'), 'zstd,3')
        self.repoCompression.addItem(self.tr('Zstandard Level 8 (modern)'), 'zstd,8')

        # zlib and lzma come from python stdlib and are there (and in borg) since long.
        # but maybe not much reason to start with these nowadays, considering zstd supports
        # a very wide range of compression levels and has great speed. if speed is more
        # important than compression, lz4 is even a little better.
        self.repoCompression.addItem(self.tr('ZLIB Level 6 (auto, legacy)'), 'auto,zlib,6')
        self.repoCompression.addItem(self.tr('LZMA Level 6 (auto, legacy)'), 'auto,lzma,6')
        self.repoCompression.addItem(self.tr('No Compression'), 'none')
        self.repoCompression.currentIndexChanged.connect(self.compression_select_action)

        self.toggle_available_compression()
        self.repoCompression.currentIndexChanged.connect(self.compression_select_action)

        self.init_ssh()
        self.sshComboBox.currentIndexChanged.connect(self.ssh_select_action)
        self.sshKeyToClipboardButton.clicked.connect(self.ssh_copy_to_clipboard_action)

        self.init_repo_stats()
        self.populate_from_profile()
        self.set_icons()