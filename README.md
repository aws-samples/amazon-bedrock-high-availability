## Designing highly available Generative AI applications using Amazon Bedrock

## Introduction
In this repository, we'll explore how to set up high availability with Amazon Bedrock, a fully managed service that simplifies building and running applications on AWS. More specifically, we'll focus on leveraging Amazon Bedrock's provisioned throughput as our primary endpoint and using Amazon Bedrock on-demand as our secondary endpoint. Additionally, we'll demonstrate how to switch between regions using the same concept.

**NOTE) The architecture in this repository is only designed for development purposes only.**

## Walkthrough
For the demonstration in this repository, you will see an approach for using Amazon Bedrock in a high-available manner using [Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) and [on-demand throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html). The following is a detailed outline of the architecture in this repository:
1. Requests are sent to a model on Amazon Bedrock that is configured to use Provisioned Throughput in region 1
2. A throttling exception will occur, triggering requests to be sent to a model on Amazon Bedrock in region 2 using on-demand throughput
   
The illustration below details what this solution will look like once fully implemented.

<img src="images/Solution Overiew.png">

<br /> 

### Prerequisites
To follow through this repository, you will need an <a href="https://console.aws.amazon.com/" >AWS account</a>, an <a href="https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/" >Amazon Bedrock supported region</a>, access to [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/setting-up.html) and access to the <a href="https://aws.amazon.com/cli/">AWS CLI</a>. In addition, you will need [Python 3](https://www.python.org/downloads/) installed locally. We also assume you have familiar with the basics of Linux bash commands.

### Step 1: Grant model access for Anthropic Claude v2 in Amazon Bedrock (AWS Console)
1. Ensure you have [granted model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html#model-access-add) to the ```Anthropic Claude``` model in Amazon Bedrock.

### Step 2: Request a Model unit quota increase (AWS Console)
1. Navigate to the [Service Quotas dashboard](https://us-east-1.console.aws.amazon.com/servicequotas/home/services/bedrock/quotas) for Amazon Bedrock
2. Search for the ```Model units per provisioned model for Anthropic Claude V2 18K``` quota limit
3. Select the ```Request increase at account level``` button
4. Update the ```Increase quota value``` to 1
5. Select the ```Request``` button
6. Once the quota increase has completed, move to step 3

### Step 3: Create Provisioned Throughput for Anthropic Claude v2 in Amazon Bedrock (AWS CLI)
1. Run the following command to create Provisioned Throughput for Anthropic Claude v2
```aws bedrock create-provisioned-model-throughput \
   --model-units 1 \
   --commitment-duration OneMonth \
   --provisioned-model-name ha-test-model \
   --model-id arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2 

   #ENSURE TO RECORD THE "provisionedModelArn" VALUE FROM THE OUTPUT OF THE COMMAND ABOVE  
```

### Step 4: Run the amazon_bedrock_ha.py Python script
1. Run the following command to execute the amazon_bedrock_ha.py Python script
```
python3 amazon_bedrock_ha.py <REPLACE_ME_WITH_PROMPT> <REPLACE_ME_WITH_PROVISIONED_MODEL_ARN>
```

## Cleaning up
Be sure to remove the resources created in this repository to avoid charges. Run the following commands to delete these resources:
1. ```aws bedrock delete-provisioned-model-throughput --provisioned-model-id <REPLACE_ME_WITH_PROVISIONED_MODEL_ARN>```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

