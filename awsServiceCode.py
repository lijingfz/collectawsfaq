import logging
import boto3
from botocore.exceptions import ClientError
import csv

logger = logging.getLogger(__name__)


def get_info_support(support_client):
    """
    Use the AWS SDK for Python (Boto3) to create an AWS Support client and count
    the available services in your account.
    This example uses the default settings specified in your shared credentials
    and config files.

    :param support_client: A Boto3 Support Client object.
    """
    try:
        print("Hello, AWS Support! Let's count the available Support services:")
        response = support_client.describe_services()
        print(f"There are {len(response['services'])} services available.")
        return response['services']
    except ClientError as err:
        if err.response["Error"]["Code"] == "SubscriptionRequiredException":
            logger.info(
                "You must have a Business, Enterprise On-Ramp, or Enterprise Support "
                "plan to use the AWS Support API. \n\tPlease upgrade your subscription to run these "
                "examples."
            )
        else:
            logger.error(
                "Couldn't count services. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
def remove_special_characters(filename, special_characters):
    # 读取原始文件内容
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # 删除特殊字符
    for char in special_characters:
        content = content.replace(char, '')

    # 将处理后的内容写回文件
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)


if __name__ == "__main__":
    service_list = get_info_support(boto3.client("support"))
    #指定明确 Service Code 以及 Category Code 以及Name的对应关系
    for i in service_list:
        i['service code'] = i['code']
        i['service name'] = i['name']
        del i['code']
        del i['name']
        print(i)
    filename = 'awsservice.csv'

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        for row in service_list:
            writer.writerow([f"{key}:{value}\n" for key, value in row.items()])

    print("csv创建成功")
    # 整理生成文件格式
    remove_special_characters('awsservice.csv', ['":', '","', '"'])
