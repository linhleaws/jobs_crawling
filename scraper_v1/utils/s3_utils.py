from io import StringIO
import boto3
from datetime import date

date = date.today()
def write_to_s3(aws_key_id, aws_secret_key, aws_region, df, job_position, job_location, date=date):
    file_name = f"{job_position}_{job_location}_{date}.csv"
    bucket_name = 'linhltt-indeed-jobs'
    # Use credentials from environment
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_key_id,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
)

    # Convert to CSV in-memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # Upload to S3
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket_name, Key=f"staging/{file_name}", Body=csv_buffer.getvalue())