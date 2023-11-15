  def AddStorageMediaImageOptions(self, argument_group):
    """Adds the storage media image options to the argument group.

    Args:
      argument_group: The argparse argument group (instance of
                      argparse._ArgumentGroup).
    """
    argument_group.add_argument(
        u'--partition', dest=u'partition_number', action=u'store', type=int,
        default=None, help=(
            u'Choose a partition number from a disk image. This partition '
            u'number should correspond to the partion number on the disk '
            u'image, starting from partition 1.'))

    argument_group.add_argument(
        u'-o', u'--offset', dest=u'image_offset', action=u'store', default=None,
        type=int, help=(
            u'The offset of the volume within the storage media image in '
            u'number of sectors. A sector is {0:d} bytes in size by default '
            u'this can be overwritten with the --sector_size option.').format(
                self._DEFAULT_BYTES_PER_SECTOR))

    argument_group.add_argument(
        u'--sector_size', u'--sector-size', dest=u'bytes_per_sector',
        action=u'store', type=int, default=self._DEFAULT_BYTES_PER_SECTOR,
        help=(
            u'The number of bytes per sector, which is {0:s} by '
            u'default.').format(self._DEFAULT_BYTES_PER_SECTOR))

    argument_group.add_argument(
        u'--ob', u'--offset_bytes', u'--offset_bytes',
        dest=u'image_offset_bytes', action=u'store', default=None, type=int,
        help=(
            u'The offset of the volume within the storage media image in '
            u'number of bytes.'))