    def _load(cls, leaderPath):
        bytesIO = BytesIO()
        with ZipFile(file=bytesIO, mode='w') as zipFile:
            for dirPath, fileNames, dirNames in os.walk(leaderPath):
                assert dirPath.startswith(leaderPath)
                for fileName in fileNames:
                    filePath = os.path.join(dirPath, fileName)
                    assert filePath.encode('ascii') == filePath
                    relativeFilePath = os.path.relpath(filePath, leaderPath)
                    assert not relativeFilePath.startswith(os.path.sep)
                    zipFile.write(filePath, relativeFilePath)
        bytesIO.seek(0)
        return bytesIO