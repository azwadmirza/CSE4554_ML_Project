    def get_snapshots(self, ec2, snap_ids):
        """get snapshots corresponding to id, but tolerant of invalid id's."""
        while snap_ids:
            try:
                result = ec2.describe_snapshots(SnapshotIds=snap_ids)
            except ClientError as e:
                bad_snap = NotEncryptedFilter.get_bad_snapshot(e)
                if bad_snap:
                    snap_ids.remove(bad_snap)
                    continue
                raise
            else:
                return result.get('Snapshots', ())
        return ()