    def get_system_facts(self):
        sn = 'NA'
        for info in self.host.hardware.systemInfo.otherIdentifyingInfo:
            if info.identifierType.key == 'ServiceTag':
                sn = info.identifierValue
        facts = {
            'ansible_distribution': self.host.config.product.name,
            'ansible_distribution_version': self.host.config.product.version,
            'ansible_distribution_build': self.host.config.product.build,
            'ansible_os_type': self.host.config.product.osType,
            'ansible_system_vendor': self.host.hardware.systemInfo.vendor,
            'ansible_hostname': self.host.summary.config.name,
            'ansible_product_name': self.host.hardware.systemInfo.model,
            'ansible_product_serial': sn,
            'ansible_bios_date': self.host.hardware.biosInfo.releaseDate,
            'ansible_bios_version': self.host.hardware.biosInfo.biosVersion,
        }
        return facts