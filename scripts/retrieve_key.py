import boto3
from botocore.exceptions import ClientError
from pathlib import Path


parentdir = Path(__file__).resolve().parent.parent
pathansible = Path(f'{parentdir}/ansible/config').resolve()

def get_secret():
    secret_name = "keys/ec2.pem"
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    
    # Write the secret key to a file with proper newlines
    with open(f'{pathansible}/ec2.pem', 'w') as key_file:
        key_file.write(secret)

    return secret

if __name__ == "__main__":
    secret = get_secret()
    print("Secret key retrieved and written to ec2.pem")