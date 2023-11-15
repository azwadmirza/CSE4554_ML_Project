def load_s3_buckets(neo4j_session, data, current_aws_account_id, aws_update_tag):
    ingest_bucket = """
    MERGE (bucket:S3Bucket{id:{BucketName}})
    ON CREATE SET bucket.firstseen = timestamp(), bucket.creationdate = {CreationDate}
    SET bucket.name = {BucketName}, bucket.arn = {Arn}, bucket.lastupdated = {aws_update_tag}
    WITH bucket
    MATCH (owner:AWSAccount{id: {AWS_ACCOUNT_ID}})
    MERGE (owner)-[r:RESOURCE]->(bucket)
    ON CREATE SET r.firstseen = timestamp()
    SET r.lastupdated = {aws_update_tag}
    """

    # The owner data returned by the API maps to the aws account nickname and not the IAM user
    # there doesn't seem to be a way to retreive the mapping but we can get the current context account
    # so we map to that directly

    for bucket in data["Buckets"]:
        arn = "arn:aws:s3:::" + bucket["Name"]
        neo4j_session.run(
            ingest_bucket,
            BucketName=bucket["Name"],
            Arn=arn,
            CreationDate=str(bucket["CreationDate"]),
            AWS_ACCOUNT_ID=current_aws_account_id,
            aws_update_tag=aws_update_tag,
        )