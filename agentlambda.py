import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_named_parameter(event, name):
    return next(item for item in event['parameters'] if item['name'] == name)['value']


def create_case(event):
    """
    Create a new support case.

    :param subject:
    :param service: The service to use for the new case.
    :param category: The category to use for the new case.
    :param severity: The severity to use for the new case.
    :return: The caseId of the new case.
    """
    support_client = boto3.client("support")
    try:
        response = support_client.create_case(
            # subject="Example case for testing, ignore.",
            subject=get_named_parameter(event, 'subject'),
            serviceCode=get_named_parameter(event, 'service'),
            severityCode=get_named_parameter(event, 'severity'),
            categoryCode=get_named_parameter(event, 'category'),
            communicationBody="Bedrock autoraise testing case",
            language="zh",
            issueType="customer-service",
        )
        case_id = response["caseId"]
    except ClientError as err:
        if err.response["Error"]["Code"] == "SubscriptionRequiredException":
            logger.info(
                "You must have a Business, Enterprise On-Ramp, or Enterprise Support "
                "plan to use the AWS Support API. \n\tPlease upgrade your subscription to run these "
                "examples."
            )
        else:
            logger.error(
                "Couldn't create case. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    else:
        return case_id


def lambda_handler(event, content):
    response_code = 200
    print("jingamz:", event)
    support_client = boto3.client("support")
    action_group = event['actionGroup']
    api_path = event['apiPath']
    if api_path == '/create-case':
        response = support_client.describe_cases(caseIdList=[create_case(event)])
        # response = support_client.describe_cases(caseIdList=['case-890717383483-mczh-2024-a14ce2b9bd839d42'])
        body = response['cases'][0]['displayId']
        print(body)
    else:
        response_code = 400
        body = {"{}::{} is not a valid api, try another one.".format(action_group, api_path)}
    response_body = {
        'application/json': {
            'body': str(body)
        }
    }
    # Bedrock action group response format
    action_response = {
        "messageVersion": "1.0",
        "response": {
            'actionGroup': action_group,
            'apiPath': api_path,
            'httpMethod': event['httpMethod'],
            'httpStatusCode': response_code,
            'responseBody': response_body
        }
    }

    return action_response
