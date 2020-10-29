from jira import JIRA
import os
from dotenv import load_dotenv
from collections import defaultdict


class api_work():

    def __init__(self):
        self.second_line = list()
        self.first_line_dict = defaultdict()
        self.first_line = list()

    def get_issues(self, project='VISTHELP'):
        jql = 'status != Done AND status != Declined AND project = {}'.format(project)
        jira_options = {'server': 'https://jira.zyfra.com'}
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            jira_login = os.getenv("JIRA_LOGIN_ANTON")
            jira_pass = os.getenv("JIRA_PASS_ANTON")
        else:
            jira_login = input('Введи логин пользователя Jira: ')
            jira_pass = input('Введи пароль: ')
        # print(jira_login)
        self.jira = JIRA(options=jira_options, basic_auth=(jira_login, jira_pass))
        self.issues = self.jira.search_issues(jql, maxResults=1000)

    def find_labels(self):
        # TODO: Допилить функцию, которая находила бы задачи без указанных меток и по возможности проставляла их
        jql = 'status != Done AND status != Declined AND reporter in ("vistsupport24@zyfra.com")'
        # jql = '(summary ~ "1????" OR summary ~ "2????") AND status != Done AND status != Declined'
        # jql = 'project = VISTHELP AND text ~ Б1564'
        # jql = 'project = VISTHELP AND text ~ 1564'
        # jql = 'project = VISTHELP AND status in ("In Progress", Pending) AND reporter in ("vistsupport24@zyfra.com") AND text ~ "Степной"'
        jira_options = {'server': 'https://jira.zyfra.com'}
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            jira_login = os.getenv("JIRA_LOGIN_ANTON")
            jira_pass = os.getenv("JIRA_PASS_ANTON")
        else:
            jira_login = input('Введи логин пользователя Jira: ')
            jira_pass = input('Введи пароль: ')
        print(jira_login)
        jira = JIRA(options=jira_options, basic_auth=(jira_login, jira_pass))
        issues = jira.search_issues(jql, maxResults=1000)
        for i in issues:
            issue = jira.issue(i)
            print(issue,
                  issue.fields.labels,
                  issue.fields.creator.key,
                  issue.fields.reporter.key)
            break
        # print(issue, issue.fields.reporter, issue.fields.labels)

    def find_lost_answers(self):
        """
        Проверка, имеются ли упущенные комментарии на второй линии,
        то есть такие, после которых движение задачи на первой линии не было возобновлено
        :return: Функция создает html-файл со списком упущенных задач второй линии
        """

        # Вызываем функцию, получающую список задач из джиры
        self.get_issues()

        # Определяем список имен сотрудников ТП в Джире
        tp_names_list = ['Anton Nagovitsin', 'Aleksey Polyakov', 'Pavel Khromov', 'Sergey Kondratyev', 'Anton Mulenkov',
                         'Yuriy.Likhanov']

        # Начинаем перебирать заявки, полученные в списке фунцией get.issues()
        for i in self.issues:
            # Получаем объект "Заявка" из джиры
            issue = self.jira.issue(str(i))
            # Проверяем список присоединенных задач к заявке
            for issue_link in issue.fields.issuelinks:
                # Проверяем, есть ли аттрибут с именем inwardIssue
                if hasattr(issue_link, 'inwardIssue'):
                    # Если есть, то получаем объект заявки, присоединенной к задаче
                    linked_issue = self.jira.issue(issue_link.inwardIssue.key)
                # Иначе проверяем, есть ли аттрибут с именем outwardIssue
                elif hasattr(issue_link, 'outwardIssue'):
                    # Если есть, то получаем объект заявки, присоединенной к задаче
                    linked_issue = self.jira.issue(issue_link.outwardIssue.key)
                # В противном случае переходим к следующей итерации цикла
                else:
                    continue

                # Проверяем несколько условий.
                # Первое - равно ди название проекта текущей заявки проекту присоединенной задачи?
                # Второе - имеются ли комментарии в присоединенной задаче?
                # Третье - проверяем, есть ли более свежие комментарии присоединённой задачи по отношению к проверяемой?
                # Четвертое - не является ли автором комментария присоединенной задачи сотрудником ТП?
                if issue.fields.project != linked_issue.fields.project \
                        and len(linked_issue.fields.comment.comments) != 0 \
                        and issue.fields.updated < linked_issue.fields.comment.comments[-1].created \
                        and linked_issue.fields.comment.comments[-1].author.displayName not in tp_names_list:
                    # В случае удовлетворительного прохождения всех условий, выполняем действия ниже
                    print(issue, linked_issue)
