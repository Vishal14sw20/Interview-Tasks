from datetime import datetime
import boto3
import json
import io
import pandas as pd

s3 = boto3.client('s3')


def lambda_handler(event, context):
    for record in event['Records']:
        # Decode and parse the Kinesis record
        payload = json.loads(record['kinesis']['data'])

        # Check if the event already exists in S3
        event_uuid = payload['event_uuid']
        bucket_name = 'babbel-data-lake-bucket'
        prefix = f"{payload['event_type']}/{payload['event_subtype']}/"

        # List objects with the given prefix
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        for obj in response.get('Contents', []):
            # Check if the object key matches the event_uuid
            if event_uuid in obj['Key']:
                # Delete the duplicate event
                s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
                print(f"Deleted duplicate event: {obj['Key']}")
                break  # Assuming only one duplicate is possible

        # Enrich the event with additional fields
        payload['created_datetime'] = datetime.fromtimestamp(payload['created_at']).isoformat()
        event_parts = payload['event_name'].split(':')
        payload['event_type'] = event_parts[0]
        payload['event_subtype'] = event_parts[1] if len(event_parts) > 1 else None

        # Convert payload to pandas DataFrame
        df = pd.DataFrame([payload])

        # Convert DataFrame to Parquet and save to S3
        buf = io.BytesIO()
        df.to_parquet(buf, engine='pyarrow')
        buf.seek(0)

        print("Data being saved:")
        print(df.to_string(index=False))

        s3.put_object(
            Bucket=bucket_name,
            Key=f"{prefix}{event_uuid}.parquet",
            Body=buf.getvalue()
        )

