from dotenv import load_dotenv
import os
import boto3
from io import StringIO
import pandas as pd

# Load environment variables from .env file
load_dotenv()
bucket_name = 'linhltt-indeed-jobs'
# Use credentials from environment
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

# Read CSV with pandas
df = pd.read_csv("./data/data engineer_ho+chi+minh+city.csv")

# Convert to CSV in-memory
csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)

# Upload to S3
s3 = boto3.client("s3")
s3.put_object(Bucket=bucket_name, Key="uploads/data engineer_ho+chi+minh+city.csv", Body=csv_buffer.getvalue())

