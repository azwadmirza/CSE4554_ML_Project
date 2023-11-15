def get_mailer_requirements():
    deps = ['azure-keyvault', 'azure-storage-queue',
            'azure-storage-blob', 'sendgrid'] + list(CORE_DEPS)
    requirements = generate_requirements(
        deps, ignore=['boto3', 'botocore', 'pywin32'],
        exclude=['pkg_resources'],
        include_self=True)
    return requirements