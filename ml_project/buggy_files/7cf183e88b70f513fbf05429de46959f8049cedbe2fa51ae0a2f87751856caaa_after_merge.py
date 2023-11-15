def _ensure_workgroup(
    session: boto3.Session, workgroup: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if workgroup is not None:
        res: Dict[str, Any] = get_work_group(workgroup=workgroup, boto3_session=session)
        config: Dict[str, Any] = res["WorkGroup"]["Configuration"]["ResultConfiguration"]
        wg_s3_output: Optional[str] = config.get("OutputLocation")
        encrypt_config: Optional[Dict[str, str]] = config.get("EncryptionConfiguration")
        wg_encryption: Optional[str] = None if encrypt_config is None else encrypt_config.get("EncryptionOption")
        wg_kms_key: Optional[str] = None if encrypt_config is None else encrypt_config.get("KmsKey")
    else:
        wg_s3_output, wg_encryption, wg_kms_key = None, None, None
    return wg_s3_output, wg_encryption, wg_kms_key