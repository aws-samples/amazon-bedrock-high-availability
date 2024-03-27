import boto3, sys, json
from botocore.exceptions import ClientError

prompt = sys.argv[1]
provisioned_model_arn = sys.argv[2]
if provisioned_model_arn is None:
    raise ValueError("Provisioned model ARN is required")

body = json.dumps({"prompt": f"\n\nHuman: {prompt}\n\nAssistant:"})
print(f"Using prompt: {prompt}")

# Set up Amazon Bedrock clients for Provisioned Throughput and on-demand throughput
bedrock_provisioned_client = boto3.client('bedrock', region_name='us-east-1')
bedrock_on_demand_client = boto3.client('bedrock', region_name='us-west-2')

# Function to call Amazon Bedrock Provisioned Throughput in region 1
def call_bedrock_provisioned(data, client_error):
    try:
        provisioned_response = bedrock_provisioned_client.some_operation(Data=data)
        if client_error:
            raise client_error
        return provisioned_response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ThrottlingException':
            print("Throttling detected, retrying with on-demand...")
            on_demand_response = call_bedrock_on_demand(data)
            return on_demand_response
    raise e

# Function to call Amazon Bedrock on-demand throughput in region 2
def call_bedrock_on_demand(data):
    try:
        response = bedrock_on_demand_client.some_operation(Data=data)
        return response
    except ClientError as e:
        print(f"Error calling Bedrock on-demand: {e}")
    raise e

if __name__ == "__main__":
    counter = 0
    client_error = None
    while counter < 10:
        if counter == 5:
            #Create dummy throttling exception error for testing purposes only
            client_error = ClientError(error_response={"Error":{"Code":"ThrottlingException"}}, operation_name="DummyOperation")
        response = call_bedrock_provisioned(prompt, client_error)
        print(response)
        counter += 1
    
