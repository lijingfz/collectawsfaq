import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv


def fetch_aws_faq(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch the page!")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    faqs = []
    qna_blocks = soup.find_all(class_='lb-txt-16 lb-rtxt')  # 此选择器基于AWS的FAQ页面的结构，可能会变更
    for block in qna_blocks:
        # print("Notice!!!", block)
        qa = block.find_all('p')
        question_list, answer_list = None, ['Init']  # 保证首次能够进入自动处理循环
        for i in qa:
            # if i.find('b') or i.find(string=re.compile('问：')) and len(answer_list) >= 1:
            if i.find(string=re.compile('问：')) and len(answer_list) >= 1:
                faqs.append((question_list, answer_list))
                question_list, answer_list = None, []
                br_tags = i.find_all('br')
                # question = i.get_text(strip=True)
                # 针对T4类型相关的问题。 jingamz@
                if br_tags:
                    question = str(br_tags[0].previous_sibling)
                    answer_parts = [str(tag.next_sibling) for tag in br_tags]
                    answer = ''.join(answer_parts)
                    answer_list.append(answer)
                else:
                    question = i.get_text(strip=True)
                question_list = question
                # print(question_list)
            else:
                answer = i.get_text(strip=True)
                answer_list.append(answer)
                # print(answer_list)
        # 如果 list中只有一条记录，或者处理循环的最后一条记录 @jingamz
        faqs.append((question_list, answer_list))
    return faqs


def get_all_faq(url):
    baseurl = 'https://aws.amazon.com/'
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch the page!")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    url_blocks = soup.find_all(class_='aws-text-box')
    faqs_url = []
    flag = 0
    for i in url_blocks:
        faqurl = i.find('a')
        if faqurl is not None:
            title = faqurl.get_text(strip=True)
            link = faqurl.get('href')
            full_url = urljoin(baseurl, link)
            # print(title, full_url)
            faqs_url.append((title, full_url, flag))
    return faqs_url

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
    url = "https://aws.amazon.com/cn/ec2/faqs/"  # EC2
    url1 = "https://aws.amazon.com/cn/faqs/"  # 遍历获得所有服务Faqs的链接
    enurl = "https://aws.amazon.com/faqs/"
    faqs_url = get_all_faq(url1)
    
    qa_list = []
    
    for title, full_url, flag in faqs_url:
        pattern = 'faq'
        if re.findall(pattern, full_url):
            # 以EC2 FAQs 为例
            if full_url == url:
                print('Title:', title)
                print('Faqs link:', full_url)
                print('Faqs flag:', flag)
                faqs = fetch_aws_faq(full_url)
                for q, a in faqs:
                    my_qa = {}
                    if q is not None:
                        my_qa = {
                            "": q,
                            "答": ''.join(a)
                        }
                        qa_list.append(my_qa)
    #根据需要指定存放的路径
    filename = 'awsqa.csv'   
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
    
        for row in qa_list:
            writer.writerow([f"{key}:{value}\n" for key,value in row.items()])    
    print("csv创建成功")  
    # 调用函数，示例中移除了几个常见的特殊字符
    remove_special_characters('awsqa.csv', ['":', '","', '"'])
