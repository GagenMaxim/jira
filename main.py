import pandas as pd
from jira import JIRA
import requests
from requests.auth import HTTPBasicAuth
import json


class JiraTask:
    pass


def jiraClient(login: str, password: str):
    options = {'server': 'https://jira.eapteka.ru', 'verify': False}
    jira = JIRA(options=options, basic_auth=(login, password), get_server_info=True)

    return jira


def downloadJiraIssues(jql: str, jira):
    return jira.search_issues(jql, 0, 600)


def parseJiraIssues(issues, jira, auth):
    jira_df = pd.DataFrame(issues)

    tasks = list()
    for issue in issues:
        task = JiraTask()
        task.type = 'запрос'
        task.key = issue.key
        task.title = issue.fields.summary
        task.link_jira = 'https://jira.eapteka.ru/browse/' + issue.key

        url = issue.self
        headers = {
            "Accept": "application/json"
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            auth=auth,
            verify=False
        )
        issueFields = json.loads(response.text)

        # получим журнал работ по задаче
        worklogs = jira.worklogs(issue)

        # приведем рабочее время в часах
        task.work_points = 0
        for worklog in worklogs:
            task.work_points = task.work_points + (worklog.timeSpentSeconds / 3600)

        task.status = issue.fields.status.name


        labels = list(map(lambda label: label.lower(), issue.fields.labels))
        task.bucket = 'no_label'
        if 'support' in labels:
            task.bucket = 'Поддержка'
        elif 'product' in labels:
            task.bucket = 'Продуктовая'
        elif 'techdebt' in labels:
            task.bucket = 'Тех долг'

        task.link_api = issue.self

        dt_str = issue.fields.created
        dt_str = dt_str.split('-')[0]
        task.created = int(dt_str)

        titles = list(map(lambda label: label.lower(), task.title.split()))
        task.ignor = False
        if 'совещания' in titles:
            task.ignor = True
        elif 'изучение' in titles:
            task.ignor = True
        elif 'автоматизация' in titles:
            task.ignor = True
        elif 'обучение' in titles:
            task.ignor = True
        elif 'тестирование' in titles:
            task.ignor = True
        elif 'настройка' in titles:
            task.ignor = True
        elif 'тест' in titles:
            task.ignor = True


        if task.work_points >= 8:
            tasks.append(task)

    return tasks


jql = 'project = TWO' #PLMDLP


uid = 'g.melnikov' #getpass.getpass('Jira Login:')
pswd = 'твой пароль' #getpass.getpass('Jira Password:')

jira = jiraClient(uid, pswd) #инициализация клиента jira
issues = downloadJiraIssues(jql, jira)

auth = HTTPBasicAuth(uid, pswd) #базовая авторизация
tasks = parseJiraIssues(issues, jira, auth)
df = pd.DataFrame([obj.__dict__ for obj in tasks])

#сохраним файл cvs из таблицы задач спринта
df.to_excel('C:/Users/g.melnikov/Desktop/Python/file_040723.xlsx')


#сохраним файл cvs из таблицы задач спринта
#сохраним файл cvs из таблицы задач спринта
