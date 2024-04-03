## Designing highly available Generative AI applications using Amazon Bedrock

## Introduction
In this repository, we'll explore how to set up high availability with Amazon Bedrock, a fully managed service that simplifies building and running applications on AWS. More specifically, we'll focus on leveraging Amazon Bedrock's provisioned throughput as our primary endpoint and using Amazon Bedrock on-demand as our secondary endpoint. Additionally, we'll demonstrate how to switch between regions using the same concept.

**NOTE) The architecture in this repository is for development purposes only and will incur costs.**

## Walkthrough
For the demonstration in this repository, you will see an approach for using Amazon Bedrock in a high-available manner using [Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) and [on-demand throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html). The following is a detailed outline of the architecture in this repository:
1. Requests are sent to a model on Amazon Bedrock that is configured to use Provisioned Throughput in region 1
2. A throttling exception will occur, triggering requests to be sent to a model on Amazon Bedrock in region 2 using on-demand throughput
   
The illustration below details what this solution will look like once fully implemented.

<img src="images/Solution Overview.png">

<br /> 

### Prerequisites
To follow through this repository, you will need an <a href="https://console.aws.amazon.com/" >AWS account</a>, an <a href="https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/" >Amazon Bedrock supported region</a>, access to [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/setting-up.html) and access to the <a href="https://aws.amazon.com/cli/">AWS CLI</a>. In addition, you will need [Python 3](https://www.python.org/downloads/) installed locally. We also assume you have familiar with the basics of Linux bash commands.

**NOTE) Although the assets in this repository work mainly around the Anthropic Claude Instant model, they can be applied to work with any model in Amazon Bedrock that supports Provisioned Throughput and is available in both regions.**

### Step 1: Grant model access for Anthropic Claude Instant in Amazon Bedrock (AWS Console)
1. Ensure you have [granted model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html#model-access-add) to the ```Anthropic Claude Instant``` model in Amazon Bedrock.

### Step 2: Create Provisioned Throughput for Anthropic Claude Instant in Amazon Bedrock (AWS CLI)
1. Run the following command to create Provisioned Throughput for ```Anthropic Claude Instant```
   
**NOTE) The following command is a no commitment purchase for Provisioned Throughput. Once it is executed, billing will end only when you delete the Provisioned Throughput. For more information, please review [Provisioned Throughput for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)**

```
aws bedrock create-provisioned-model-throughput \
   --model-units 1 \
   --provisioned-model-name ha-test-model \
   --model-id arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-instant-v1:2:100k

   #ENSURE TO RECORD THE "provisionedModelArn" VALUE FROM THE OUTPUT OF THE COMMAND ABOVE  
```
1. Run the following command to check the status of the Provisioned Throughput. Proceed to the next step only when the status is ```Created```
```
aws bedrock get-provisioned-model-throughput \
    --provisioned-model-id ha-test-model
```

### Step 3: Run the amazon_bedrock_ha.py Python script (Python 3)
1. Run the following command to execute the amazon_bedrock_ha.py Python script
```
python3 amazon_bedrock_ha.py <REPLACE_ME_WITH_PROVISIONED_MODEL_ARN> <REPLACE_ME_WITH_PROMPT>  
```

**NOTE) Without the throttling exception error-handling provided in the amazon_bedrock_ha.py script, the boto3 SDK would return an unhandled BedrockRuntime.Client.exceptions.ThrottlingException exception similar to ```botocore.exceptions.ClientError: An error occurred (ThrottlingException) when calling the DummyOperation operation: Unknown```. This error would continue to occur until throttling has stopped for the client.**

## Cleaning up
Be sure to remove the resources created in this repository to avoid charges. Run the following commands to delete these resources:
1. ``` aws bedrock delete-provisioned-model-throughput --provisioned-model-id ha-test-model ```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

