from io import StringIO
import boto3
import os
from datetime import date

date = date.today()
def write_to_s3(df, job_position, job_location, date=date):
    file_name = f"{job_position}_{job_location}_{date}.csv"
    bucket_name = 'linhltt-indeed-jobs'
    # Use credentials from environment
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION")
)

    # Convert to CSV in-memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # Upload to S3
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket_name, Key=f"staging/{file_name}", Body=csv_buffer.getvalue())