import boto3, sys, json, re
from botocore.exceptions import ClientError

# CONSTANTS
ON_DEMAND_MODEL_ID="anthropic.claude-instant-v1"
REGION1 = 'us-east-1'
REGION2 = 'us-west-2'

# prompt = "what is the largest city in the world?" 

def valid_region(region):
    """
    Validate an AWS region code.
    Args:
        region (str): The AWS region code to validate.
    Returns:
        bool: True if the region code is valid, False otherwise.
    """
    # Define the regex pattern for a valid AWS region code
    pattern = "us-east-[12]|us-west-[12]|af-south-1|ap-east-1|ap-south-1|ap-northeast-[123]|ap-southeast-[123]|ca-central-1|cn-north-1|cn-northwest-1|eu-central-1|eu-north-1|eu-south-1|eu-west-[123]|gov-west-1|me-south-1|sa-east-1"
    
    # Compile the regex pattern
    regex = re.compile(pattern)
    
    # Test the region against the regex pattern
    if regex.match(region):
        return True
    return False

def call_bedrock_primary(client_error):
    """ Function to call Amazon Bedrock Provisioned Throughput in region 1"""
    try:
        primary_response = bedrock_primary_client.invoke_model(body=body, 
                                                                       modelId=provisioned_model_arn, 
                                                                       accept='application/json', 
                                                                       contentType='application/json')
        if client_error:
            raise client_error
        
        primary_response_body = json.loads(primary_response.get('body').read())
        primary_response_text = f"From primary in {REGION1}: {primary_response_body.get('completion')}"

        return primary_response_text
    except NameError as name_error:
        try:
            # print(f"Calling Bedrock Provisioned Throughput: {name_error}")
            primary_response = bedrock_primary_client.invoke_model(body=body, 
                                                                modelId=ON_DEMAND_MODEL_ID,
                                                                accept='application/json', 
                                                                contentType='application/json')
            if client_error:
                raise client_error
            
            primary_response_body = json.loads(primary_response.get('body').read())
            primary_response_text = f"From primary in {REGION1}: {primary_response_body.get('completion')}"
            return primary_response_text
        
        except ClientError as client_exception:
           
            if client_exception.response['Error']['Code'] == 'ThrottlingException':
                print("Throttling detected, retrying with on-demand...")
                secondary_response = call_bedrock_secondary()
                return secondary_response
            # else:
            # raise client_exception
            raise name_error
            
    except ClientError as client_exception:
        if client_exception.response['Error']['Code'] == 'ThrottlingException':
            print("Throttling detected, retrying with on-demand...")
            secondary_response = call_bedrock_secondary()
            return secondary_response
        else:
            raise client_exception


def call_bedrock_secondary():
    """ Function to call Amazon Bedrock on-demand throughput in region 2"""
    try:
        
        on_demand_response = bedrock_secondary_client.invoke_model(body=body, 
                                                        modelId=ON_DEMAND_MODEL_ID,
                                                        accept='application/json', 
                                                        contentType='application/json')
        
        on_demand_response_body = json.loads(on_demand_response.get('body').read())
        on_demand_response_text = f"From on-demand in {REGION2}: {on_demand_response_body.get('completion')}"

        return on_demand_response_text
    except ClientError as client_exception:
        print(f"Error calling Bedrock on-demand: {client_exception}")
        raise client_exception


print(f"sys.argv has {len(sys.argv)} arguments")
for i, arg in enumerate(sys.argv):
    print(f"Argument {i}: {arg}")

if len(sys.argv) == 3:
    try:
        provisioned_model_arn = sys.argv[1]
        prompt = sys.argv[2]
    except IndexError:
        raise ValueError("Prompt and Provisioned model ARN are required if two parameters are passed")

elif len(sys.argv) == 2:
    try:
        prompt = sys.argv[1]
        print(f"Using Regions: {REGION1} and {REGION2}")
        assert valid_region(REGION1)
        assert valid_region(REGION2)
    except IndexError:
        raise ValueError("Using default regions. A Prompt is required if one parameter is passed")

elif len(sys.argv) == 4:
    try:
        REGION1 = sys.argv[1]
        REGION2 = sys.argv[2]
        prompt = sys.argv[3]
        print(f"Using Regions: {REGION1} and {REGION2}")
        assert valid_region(REGION1)
        assert valid_region(REGION2) 
    except IndexError:
        raise ValueError("Prompt, Provisioned model ARN, and Region are required if three parameters are passed")

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
bedrock_primary_client = boto3.client('bedrock-runtime', region_name=REGION1)
bedrock_secondary_client = boto3.client('bedrock-runtime', region_name=REGION2)

if __name__ == "__main__":
    
    for counter in range(5):
        if counter == 3:
            #Create dummy throttling exception error for testing purposes only
            client_error = ClientError(error_response={"Error":{"Code":"ThrottlingException"}}, operation_name="DummyOperation")
        else:
            client_error = None
        response = call_bedrock_primary(client_error)
        # response_body = json.loads(response.get('body').read())
        print(f"{counter}: {response}")
        
    
