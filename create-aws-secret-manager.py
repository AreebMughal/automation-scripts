import json
import os

import boto3
from dotenv import load_dotenv

# Load AWS credentials from .env file

load_dotenv()

APP_MODE = os.getenv("APP_MODE")

SERVICE_NAMES = [
    'admin',
    'appointment',
    'charting',
    'communication-manager',
    'medication',
    'notification',
    'patients',
    'payments',
    'reports',
    'tasks',
    'therapies',
    'tickets'
]

VERSION = os.getenv("VERSION")

IGNORE_AWS_KEYS = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION', 'AWS_SECRET_NAME']
ADD_AWS_KEYS_FOR_SERVICE = ['patients']


def get_secret_name(service_name):
    app_mode = f"-{APP_MODE}" if APP_MODE != 'prod' else ''

    return f'{service_name}-{VERSION}{app_mode}'


def read_env_file(env_file_path, service_name):
    """Reads an .env file and returns a dictionary of key-value pairs."""
    print(f'Loading ENV: {env_file_path}')
    env_vars = {}
    with open(env_file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):  # Ignore empty lines and comments
                key, value = line.split("=", 1)

                # do not add AWS keys to the secret manager
                if key not in IGNORE_AWS_KEYS or service_name in ADD_AWS_KEYS_FOR_SERVICE:
                    env_vars[key.strip()] = value.strip().replace('\'', '').replace('\"', '')
    return env_vars


def create_or_update_secret(secret_name, secret_values, region_name):
    """Creates or updates a secret in AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        # Check if secret already exists
        client.get_secret_value(SecretId=secret_name)
        print(f"Secret '{secret_name}' already exists. Updating it...")
        client.update_secret(SecretId=secret_name, SecretString=str(secret_values))
    except client.exceptions.ResourceNotFoundException:
        print(f"Creating new secret '{secret_name}'...")
        client.create_secret(Name=secret_name, SecretString=str(secret_values))

    print(f"Secret `{secret_name}` successfully stored!")


def main():
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    print(aws_region, aws_access_key, aws_secret_key)

    if not aws_access_key or not aws_secret_key:
        print("Error: AWS credentials are missing in the .env file.")
        return

    # Set AWS credentials manually for boto3
    boto3.setup_default_session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    for service_name in SERVICE_NAMES:
        print(f'----> Creating or Updating AWS Secret Manager for {service_name}...')
        env_name = f"{f".{APP_MODE}" if APP_MODE != 'prod' else ""}.env"
        env_file_path = os.path.join("envs", service_name, env_name)

        if not os.path.exists(env_file_path):
            print(f"Warning: {env_file_path} file not found. Skipping...")
            continue  # Skip this iteration and proceed to the next service

        secret_values = read_env_file(env_file_path, service_name)
        secret_name = get_secret_name(service_name)
        # Convert secret_values to a properly formatted JSON string
        secret_values_json = json.dumps(secret_values, indent=4)

        create_or_update_secret(secret_name, secret_values_json, aws_region)


if __name__ == "__main__":
    main()
