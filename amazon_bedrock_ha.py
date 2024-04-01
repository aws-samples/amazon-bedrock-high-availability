import boto3, sys, json
from botocore.exceptions import ClientError

try:
    prompt = sys.argv[1]
    provisioned_model_arn = sys.argv[2]
except IndexError:
    raise ValueError("Prompt and Provisioned model ARN are required")

formatted_prompt = f"Human: {prompt}\n\nAssistant:"
print(f"Using prompt: {prompt}")

#Building request payload for Amazon Bedrock
body = json.dumps({
    "prompt": formatted_prompt,
    "max_tokens_to_sample": 200,
    "temperature": 0.5,
    "stop_sequences": ["\n\nHuman:"]
    })

# Set up Amazon Bedrock clients for Provisioned Throughput and on-demand throughput
bedrock_provisioned_client = boto3.client('bedrock-runtime', region_name='us-east-1')
bedrock_on_demand_client = boto3.client('bedrock-runtime', region_name='us-west-2')

# Function to call Amazon Bedrock Provisioned Throughput in region 1
def call_bedrock_provisioned(client_error):
    try:
        provisioned_response = bedrock_provisioned_client.invoke_model(body=body, 
                                                                       modelId=provisioned_model_arn, 
                                                                       accept='application/json', 
                                                                       contentType='application/json')
        if client_error:
            raise client_error
        
        provisioned_response_body = json.loads(provisioned_response.get('body').read())
        provisioned_response_text = f"From Provisioned Throughput in region 1: {provisioned_response_body.get('completion')}"

        return provisioned_response_text
    except ClientError as client_exception:
        if client_exception.response['Error']['Code'] == 'ThrottlingException':
            print("Throttling detected, retrying with on-demand...")
            on_demand_response = call_bedrock_on_demand()
            return on_demand_response
        else:
            raise client_exception

# Function to call Amazon Bedrock on-demand throughput in region 2
def call_bedrock_on_demand():
    try:
        on_demand_model_id="anthropic.claude-instant-v1"
        on_demand_response = bedrock_on_demand_client.invoke_model(body=body, 
                                                        modelId=on_demand_model_id,
                                                        accept='application/json', 
                                                        contentType='application/json')
        
        on_demand_response_body = json.loads(on_demand_response.get('body').read())
        on_demand_response_text = f"From on-demand in region 2: {on_demand_response_body.get('completion')}"

        return on_demand_response_text
    except ClientError as client_exception:
        print(f"Error calling Bedrock on-demand: {client_exception}")
        raise client_exception

if __name__ == "__main__":
    counter = 0
    client_error = None
    while counter < 10:
        if counter == 5:
            #Create dummy throttling exception error for testing purposes only
            client_error = ClientError(error_response={"Error":{"Code":"ThrottlingException"}}, operation_name="DummyOperation")
        elif counter == 9:
            client_error = None
        response = call_bedrock_provisioned(client_error)
        print(response)
        counter += 1
        
    
