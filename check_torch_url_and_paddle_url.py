"""
此脚本用于检查指定paddle api和torch api网址是否符合版本规范
"""
import re
import logging
import requests
import glob
import os


def split_markdown_by_titles(file_path):
    sections = []
    current_section = {'title': '', 'content': ''}

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith('#'):
            if current_section['title']:
                sections.append(current_section)
            current_section = {'title': line.strip('# \n'), 'content': ''}
        else:
            current_section['content'] += line

    if current_section['title']:
        sections.append(current_section)

    return sections


def is_accessible(url):
    try:
        # 发送HTTP GET请求
        response = requests.get(url, timeout=5)

        # 检查响应状态码，200表示成功访问
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False


def website_contains_instant_substring(url, substring='window.docInfo.version="develop"'):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            website_content = response.text
        else:
            return False
    except requests.RequestException:
        return None

    return substring in website_content


def replace_and_save_md_file(file_path, old_string, new_string):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    new_lines = [line.replace(old_string, new_string) for line in lines]

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)


def check_paddle_url(markdown_file_path,
                     split_key="api/",
                     target_url="https://www.paddlepaddle.org.cn/documentation/docs/zh/develop/"):
    """
    error code
    0 success
    1 没有url
    2 初始url不可访问
    3 修正后url不可访问
    4 版本不匹配
    """
    sections = split_markdown_by_titles(markdown_file_path)

    title = sections[2]['title']  # paddle api is at 3th

    name_pattern = r'\[(.*?)\]'
    matches = re.findall(name_pattern, title)
    if matches:
        name = matches[0]
        logging.info(f"paddle api name: {name}")
    else:
        logging.info("no match name")
        return 0
    url_pattern = r'\((.*?)\)'
    matches = re.findall(url_pattern, title)
    if matches:
        url = matches[0]
        logging.info(f"paddle api url: {url}")
    else:
        logging.info("no paddle api url")
        return 0
    init_url = url
    if is_accessible(url):
        logging.info(f"success requests{url}")
    else:
        logging.info(f"no success requests{url}")
        return 2

    url_split = url.split(split_key)

    if url_split[0] == target_url:
        logging.info("init url is target_url")
    else:
        logging.info("init url is different from target_url")
        logging.info("init error url is ", url)

        url = target_url + "api/" + url_split[1]
        logging.info("corrected url is ", url)
        if is_accessible(url):
            logging.info(f"success requests{url}")
        else:
            logging.info(f"no success requests{url}")
            return 3

    if website_contains_instant_substring(url, substring='window.docInfo.version="develop"'):
        logging.info("the version is window.docInfo.version='develop'")

    else:
        logging.info("version error")
        return 4
    if init_url != url:
        replace_and_save_md_file(markdown_file_path, old_string=init_url, new_string=url)
    return 0


def check_torch_url(markdown_file_path,
                    split_key="docs/",
                    target_version="stable"):
    """
    error code
    0 success
    1 没有url
    2 初始url不可访问
    3 修正后url不可访问
    4 版本不匹配
    """
    sections = split_markdown_by_titles(markdown_file_path)

    title = sections[1]['title']  # paddle api is at 3th

    name_pattern = r'\[(.*?)\]'
    matches = re.findall(name_pattern, title)
    if matches:
        name = matches[0]
        logging.info(f"paddle api name: {name}")
    else:
        logging.info("no match name")
        return 0
    url_pattern = r'\((.*?)\)'
    matches = re.findall(url_pattern, title)
    if matches:
        url = matches[0]
        logging.info(f"paddle api url: {url}")
    else:
        logging.info("no paddle api url")
        return 0
    init_url = url
    if is_accessible(url):
        logging.info(f"success requests{url}")
    else:
        logging.info(f"no success requests{url}")
        return 2

    url_split = url.split(split_key)[1].split('/')[0]

    if url_split == target_version:
        logging.info("init url is target_url")
    else:
        logging.info("init url is different from target_url")
        logging.info("init error url is ", url)

        url = url.replace(url_split, target_version)
        logging.info("corrected url is ", url)
        if is_accessible(url):
            logging.info(f"success requests{url}")
        else:
            logging.info(f"no success requests{url}")
            return 3

    if init_url != url:
        replace_and_save_md_file(markdown_file_path, old_string=init_url, new_string=url)
    return 0


def configure_logging(log_file):
    # 配置日志格式
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    log_file = "my_log.log"

    # 配置日志记录
    configure_logging(log_file)

    md_file_paths = glob.glob(os.path.join("cuda", "*.md"))

    paddle_api_error_paths = []
    for md_path in md_file_paths:
        error_code = check_paddle_url(markdown_file_path=md_path)
        if error_code != 0:
            paddle_api_error_paths.append(md_path)
    print(paddle_api_error_paths)

    torch_api_error_paths = []
    for md_path in md_file_paths:
        error_code = check_torch_url(markdown_file_path=md_path, split_key="docs/", target_version="stable")
        if error_code != 0:
            torch_api_error_paths.append(md_path)
    print(torch_api_error_paths)
    # print(f"current error_code is {error_code}")
