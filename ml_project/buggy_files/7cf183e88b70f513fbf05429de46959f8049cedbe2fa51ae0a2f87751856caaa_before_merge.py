def _ensure_workgroup(
    session: boto3.Session, workgroup: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if workgroup:
        res: Dict[str, Any] = get_work_group(workgroup=workgroup, boto3_session=session)
        config: Dict[str, Any] = res["WorkGroup"]["Configuration"]["ResultConfiguration"]
        wg_s3_output: Optional[str] = config.get("OutputLocation")
        wg_encryption: Optional[str] = config["EncryptionConfiguration"].get("EncryptionOption")
        wg_kms_key: Optional[str] = config["EncryptionConfiguration"].get("KmsKey")
    else:
        wg_s3_output, wg_encryption, wg_kms_key = None, None, None
    return wg_s3_output, wg_encryption, wg_kms_key