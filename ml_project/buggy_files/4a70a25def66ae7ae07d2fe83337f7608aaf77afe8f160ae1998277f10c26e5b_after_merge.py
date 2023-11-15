    def get_data(self):
        d = {
            'id': self.name,
            'create_time': self.instance.create_time,
            'status': self.status,
            'availability_zone': self.instance.availability_zone,
            'backup_retention': self.instance.backup_retention_period,
            'backup_window': self.instance.preferred_backup_window,
            'maintenance_window': self.instance.preferred_maintenance_window,
            'multi_zone': self.instance.multi_az,
            'instance_type': self.instance.instance_class,
            'username': self.instance.master_username,
            'iops': self.instance.iops
        }

        # Only assign an Endpoint if one is available
        if hasattr(self.instance, 'endpoint'):
            d["endpoint"] = self.instance.endpoint[0]
            d["port"] = self.instance.endpoint[1]
            if self.instance.vpc_security_groups is not None:
                d["vpc_security_groups"] = ','.join(x.vpc_group for x in self.instance.vpc_security_groups)
            else:
                d["vpc_security_groups"] = None
        else:
            d["endpoint"] = None
            d["port"] = None
            d["vpc_security_groups"] = None
        d['DBName'] = self.instance.DBName if hasattr(self.instance, 'DBName') else None
        # ReadReplicaSourceDBInstanceIdentifier may or may not exist
        try:
            d["replication_source"] = self.instance.ReadReplicaSourceDBInstanceIdentifier
        except Exception:
            d["replication_source"] = None
        return d