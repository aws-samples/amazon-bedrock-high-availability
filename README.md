# Designing highly available Generative AI applications using Amazon Bedrock

## Introduction

Amazon Bedrock Provisioned Throughput enables you to provision a higher level of throughput for a model at a fixed cost so your Generative AI applications have a guranteed number of input and output tokens it can process. However, what happens if you have a usage spike you didn't plan for? You could increase your Provisioned Throughput, but with that comes downtime of your application as resources are provisioned and additional hourly or monthly costs. Instead, we recommend using Amazon Bedrock on-demand throughput either in the same or secondary region during these usage spikes. This allows your Generative AI applications to continue handling requests until the usage spike is over. 

In this repository, we'll explore how to set up this approach with Amazon Bedrock with a focus on leveraging Amazon Bedrock's Provisioned Throughput as our primary endpoint and using Amazon Bedrock on-demand as our secondary endpoint. 

**NOTE) The architecture in this repository is for development purposes only and will incur costs. A  production implementation of this solution should include additional features such as retry logic, observability, an API gateway, etc. For more information, please review the [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html).**

## Walkthrough

For the demonstration in this repository, you will see an approach for using Amazon Bedrock in a high-available manner using [Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) and [on-demand throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html). The following is a detailed outline of the architecture in this repository:

1. Requests are sent to a model on Amazon Bedrock that is configured to use Provisioned Throughput in region 1
2. A throttling exception will occur, triggering requests to be sent to a model on Amazon Bedrock in region 2 using on-demand throughput

The illustration below details what this solution will look like once fully implemented.

<img src="images/Solution Overview.png">

<br />

### Prerequisites

To follow through this repository, you will need an <a href="https://console.aws.amazon.com/" >AWS account</a>, an <a href="https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/" >Amazon Bedrock supported region</a>, access to [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/setting-up.html) and access to the <a href="https://aws.amazon.com/cli/">AWS CLI</a>. In addition, you will need [Python 3](https://www.python.org/downloads/) installed locally. We also assume you have familiar with the basics of Linux bash commands.

**NOTE) Although the assets in this repository work mainly around the [Anthropic Claude 3 Haiku](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) model, they can be applied to work with any model in Amazon Bedrock that supports Provisioned Throughput and is available in both regions.**

### Step 1: Grant model access for Anthropic Claude 3 Haiku in Amazon Bedrock (AWS Console)

1. Ensure you have [granted model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html#model-access-add) to the ```Anthropic Claude 3 Haiku``` model in Amazon Bedrock.

### Step 2: Create Provisioned Throughput for Anthropic Claude 3 Haiku in Amazon Bedrock (AWS CLI)

1. Run the following command to create Provisioned Throughput for ```Anthropic Claude 3 Haiku```

**NOTE) The following command is a no commitment purchase for Provisioned Throughput. Once it is executed, billing will end only when you delete the Provisioned Throughput and you will be billed for a minumum of one hour. For more information, please review [Provisioned Throughput for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) and [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)**

```bash
aws bedrock create-provisioned-model-throughput \
   --model-units 1 \
   --provisioned-model-name ha-test-model \
   --model-id arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0:48k

   #ENSURE TO RECORD THE "provisionedModelArn" VALUE FROM THE OUTPUT OF THE COMMAND ABOVE  
```

1. Run the following command to check the status of the Provisioned Throughput. Proceed to the next step only when the status is ```Created```

```bash
aws bedrock get-provisioned-model-throughput \
    --provisioned-model-id ha-test-model
```

### Step 3: Run the amazon_bedrock_ha.py Python script (Python 3)

1. Run the following command to execute the amazon_bedrock_ha.py Python script

```bash
#Using default region values
python3 amazon_bedrock_ha.py <REPLACE_ME_WITH_PROVISIONED_MODEL_ARN> <REPLACE_ME_WITH_PROMPT>  

#Using provided region 2 value 
python3 amazon_bedrock_ha.py <REPLACE_ME_WITH_ON_DEMAND_REGION>  <REPLACE_ME_WITH_PROVISIONED_MODEL_ARN> <REPLACE_ME_WITH_PROMPT> 
```

Below is an example execution of the amazon_bedrock_ha.py Python script using **us-west-2** as region 2 

```bash
python3 amazon_bedrock_ha.py us-west-2 arn:aws:bedrock:us-east-1:AWSACCOUNTID:provisioned-model/PTMODELID  "what is the largest city in the world? only give the answer with no details"

#example output
sys.argv has 4 arguments
Argument 0: amazon_bedrock_ha.py
Argument 1: us-west-2
Argument 2: arn:aws:bedrock:us-east-1:AWSACCOUNTID:provisioned-model/PTMODELID
Argument 3: what is the largest city in the world? only give the answer with no details
Using Regions: us-east-1 and us-west-2
Using prompt: what is the largest city in the world? only give the answer with no details
0: From provisioned throughput in us-east-1: ['Tokyo']
1: From provisioned throughput in us-east-1: ['Tokyo']
2: From provisioned throughput in us-east-1: ['Tokyo']
Throttling detected, retrying with on-demand...
3: From on-demand throughput in us-west-2: ['Tokyo']
4: From provisioned throughput in us-east-1: ['Tokyo']
```

**NOTE) Without the throttling exception error-handling provided in the amazon_bedrock_ha.py script, the boto3 SDK would return an unhandled BedrockRuntime.Client.exceptions.ThrottlingException exception similar to ```botocore.exceptions.ClientError: An error occurred (ThrottlingException) when calling the DummyOperation operation: Unknown```. This error would continue to occur until throttling has stopped for the client.**

## Cleaning up

Be sure to remove the resources created in this repository to avoid charges. **Billing will continue on an hourly basis and will not stop until the Provisioned Throughput has been deleted**. Run the following commands to delete this resource:

1. ``` aws bedrock delete-provisioned-model-throughput --provisioned-model-id ha-test-model ```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
