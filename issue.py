# Copyright (c) 2022 Terwer Authors. All Rights Reserved.
# @author terwer on 2023/10/10
# ========================================================
import requests
from loguru import logger


def collect_issues():
    # 用户名和GitHub访问令牌
    username = 'terwer'
    token = ''
    with open('token.txt', 'r') as f:
        token = f.read().strip()

    # 设置API请求头，包括身份验证
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # 获取用户的所有存储库（分页处理）
    repos_url = f'https://api.github.com/users/{username}/repos'
    repo_issues = {}

    page = 1
    while True:
        response = requests.get(repos_url, headers=headers, params={'per_page': 100, 'page': page})
        repos_data = response.json()

        if not repos_data:
            break

        for index, repo in enumerate(repos_data, start=(page - 1) * 100 + 1):
            repo_name = repo['name']
            repo_url = repo['html_url']
            logger.info(f'Processing repository {index}/{len(repos_data) + (page - 1) * 100}: {repo_name}')

            issues_url = f'https://api.github.com/repos/{username}/{repo_name}/issues'

            # 获取存储库的所有问题（分页处理）
            page_issues = []
            page_issue = 1
            while True:
                response = requests.get(issues_url, headers=headers, params={'state': 'open', 'page': page_issue})
                issues_data = response.json()
                logger.info(f'Repository: {repo_name}, Page: {page_issue}, Issues Count: {len(issues_data)}')

                if not issues_data:
                    break

                page_issues.extend(issues_data)
                page_issue += 1

            if page_issues:
                repo_issues[repo_name] = {'url': repo_url, 'issues': page_issues}
            else:
                logger.warning(f'Repository {repo_name} has no open issues.')

        page += 1

    # 保存结果到 issue.md
    with open('issues.md', 'w') as file:
        for repo_name, repo_data in repo_issues.items():
            file.write(f'## Repository: {repo_name} ({len(repo_data["issues"])} issues)\n')
            file.write(f'Repository URL: [{repo_name}]({repo_data["url"]})\n')
            file.write(f'Open Issues:\n')
            for issue in repo_data["issues"]:
                file.write(f'  - [{issue["title"]}]({issue["html_url"]})\n')
            file.write('\n')

    logger.info('Issues collected and saved to issues.md')
