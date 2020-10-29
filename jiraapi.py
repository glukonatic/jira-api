from jira import JIRA
from datetime import timedelta, datetime
import dateutil.parser
import pytz
import os
from dotenv import load_dotenv


class Jira:
    """
    Класс, содержащий функции для обращения к API Jira за данными, а так же для внесения изменений в эти данные
    """

    def __init__(self):
        """
        Инициализация объекта класса
        """
        pass

    def get_issues(self, project='VISTHELP'):
        # Поисковая строка для получения пула тикетов Jira
        jql = 'status != Done AND status != Declined AND project = {}'.format(project)
        # Опции для подключения к серверу Jira
        #  сервер:
        jira_options = {'server': 'https://jira.zyfra.com'}
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            jira_login = os.getenv("JIRA_LOGIN_ANTON")
            jira_pass = os.getenv("JIRA_PASS_ANTON")
        else:
            jira_login = input('Введи логин пользователя Jira: ')
            jira_pass = input('Введи пароль: ')
        # Объявляем переменную - объект JIRA, выполняя обращение к серверу
        self.jira = JIRA(options=jira_options, basic_auth=(jira_login, jira_pass))
        # Количество дней от текущего момента в прошлое, за которое требуется обработать задачи
        self.delta = timedelta(days=int(input('Введи число дней, за которое читать Jira: ')))
        # Время в UTC
        self.utc = pytz.UTC
        # Список тикетов, полученные запросом из Jira
        return self.jira.search_issues(jql, maxResults=1000)


    def file_begins_ends(self, flg):

        # Список строк для формирования заголовка отчета
        string_before = ["<!DOCTYPE html>", "<html lang=\"ru\">", "<head>",
                         "    <title>Выгрузка из Джиры</title>", "    <meta charset=\"utf-8\">",
                         "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
                         "	   <style>",
                         "h2 { text-align: center; font-family: Verdana, Arial, Helvetica, sans-serif; color: #336; }",
                         "h3 { text-align: center; font-family: Verdana, Arial, Helvetica, sans-serif; color: blue; }",
                         "   p { color: green; }", "	</style>", "</head> ", "<body>",
                         "			<h2>Последние комментарии</h2>", '\n',
                         "    <section id=\"docs\" style=\"margin: 5%;\">"]
        # Список строк для формирования окончания отчета
        string_after = ["    </section>", "</body>", "</html> "]

        if flg == 'begin':
            # Имя файла, получаемого в результате работы функции
            filename = str('jiraReport' + datetime.now().ctime() + '.html').replace(' ', '_').replace(':', '')
            # Открываем файл
            self.file = open(filename, 'w')
            for line in string_before:
                self.file.write(line)
        else:
            # Закрываем файл
            for line in string_after:
                self.file.write(line)
            self.file.close()

    def write_data(self, i, c):
        self.file.write("\n			<div>")
        self.file.write("\n				<h3><a href=\"" + "https://jira.zyfra.com/browse/" + str(
            i) + "\" target=\"new\">" + i.fields.summary + "</a></h3>")
        self.file.write("\n				<p>" + dateutil.parser.isoparse(c.created).ctime() + "</p>")
        self.file.write("\n				<p>" + c.author.displayName + "</p>")
        self.file.write("\n				<p>" + c.body + "</p>")
        self.file.write('\n' + '=' * 100 + '\n')

    def last_comment(self):
        """
        Функция для получения коследнего комментария по всем задачам, удовлетворяющим поисковому запросу из блока init
        :return: Функция ничего не возвращает, результатом работы функции является html-файл, который можно открыть в
        браузере.
        """

        issues = self.get_issues(project='VISTHELP2')
        self.file_begins_ends('begin')
        # Перебираем список тикетов, полученных при инициализации
        for i in issues:
            issue = self.jira.issue(str(i))
            # В явном виде проверяем задачи только проекта VISTHELP2
            if 'VISTHELP2' in str(issue):
                # Если есть комментарии в задаче
                if len(issue.fields.comment.comments) != 0:
                    # Берем последний комментарий задачи
                    lastcomment = issue.fields.comment.comments[-1]
                    # Если комментарий не старше определенного при инициализации количества дней delta
                    if dateutil.parser.isoparse(lastcomment.created) > self.utc.localize(datetime.today() - self.delta):
                        # Вызываем функцию записи в файл
                        self.write_data(issue, lastcomment)

        self.file_begins_ends('end')

    def all_users_comments(self, username=''):
        """
        Функция, возвращающая все комментарии в Jira от определенного пользователя
        :param username: Имя пользователя, как в Jira
        :return: Функция ничего не возвращает, при этом
        """

        issues = self.get_issues(project='VISTHELP2')
        self.file_begins_ends('begin')

        for i in issues:
            issue = self.jira.issue(str(i))
            if len(issue.fields.comment.comments) != 0:
                for comment in issue.fields.comment.comments:
                    if comment.author.displayName == username:
                        self.write_data(issue, comment)

        self.file_begins_ends('end')

    def non_tp_last_comment(self):
        # Заполняем "шапку" в файле
        self.file_begins_ends('begin')
        # Определяем список имен сотрудников ТП в Джире
        tp_names_list = ['Anton Nagovitsin', 'Aleksey Polyakov', 'Pavel Khromov', 'Sergey Kondratyev', 'Anton Mulenkov',
                         'Yuriy.Likhanov']

        # Получаем список задач
        issues = self.get_issues(project='VISTHELP2')
        # Листаем задачи
        for i in issues:
            # Получаем объект задачи из джиры
            issue = self.jira.issue(str(i))
            # Если есть комментарии в задаче
            if len(issue.fields.comment.comments) != 0:
                # Берем последний комментарий задачи
                lastcomment = issue.fields.comment.comments[-1]
                # Проверяем, имеются ли авторами последних комментариев сотрудники ТП
                if lastcomment.author.displayName not in tp_names_list:
                    # Если комментарий не старше определенного при инициализации количества дней delta
                    if dateutil.parser.isoparse(lastcomment.created) > self.utc.localize(
                            datetime.today() - self.delta):
                        # Вызываем функцию записи в файл
                        self.write_data(issue, lastcomment)

        # Заполняем окончание файла, сохраняем
        self.file_begins_ends('end')

    def check_comments(self):
        """
        Функция для получения последнего комментария по всем задачам, удовлетворяющим поисковому запросу
        :return: Функция ничего не возвращает, результатом работы функции является html-файл, который можно открыть в
        браузере.
        """

        # Заполняем "шапку" в файле
        self.file_begins_ends('begin')

        # Получаем список задач
        issues = self.get_issues(project='VISTHELP2')

        # Листаем задачи
        for i in issues:
            # Получаем объект задачи из джиры
            issue = self.jira.issue(str(i))
            # Если есть комментарии в задаче
            if len(issue.fields.comment.comments) != 0:
                # Берем последний комментарий задачи
                lastcomment = issue.fields.comment.comments[-1]
                # Если комментарий не старше определенного при инициализации количества дней delta
                if dateutil.parser.isoparse(lastcomment.created) > self.utc.localize(datetime.today() - self.delta):
                    # Вызываем функцию записи в файл
                    self.write_data(issue, lastcomment)

        # Заполняем окончание файла, сохраняем
        self.file_begins_ends('end')

    def update_label(self):
        print(self.issues_list[0])
        # pass

    def find_lost_answers(self):
        """
        Проверка, имеются ли упущенные комментарии на второй линии,
        то есть такие, после которых движение задачи на первой линии не было возобновлено
        :return: Функция создает html-файл со списком упущенных задач второй линии
        """

        # Заполняем "шапку" в файле
        self.file_begins_ends('begin')

        # Вызываем функцию, получающую список задач из джиры
        issues = self.get_issues()

        # Определяем список имен сотрудников ТП в Джире
        tp_names_list = ['Anton Nagovitsin', 'Aleksey Polyakov', 'Pavel Khromov', 'Sergey Kondratyev', 'Anton Mulenkov',
                         'Yuriy.Likhanov']

        # Начинаем перебирать заявки, полученные в списке фунцией get.issues()
        for i in issues:
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
                    # Вызываем функцию записи в файл
                    self.write_data(issue, issue.fields.comment.comments[-1])

        # Заполняем окончание файла, сохраняем
        self.file_begins_ends('end')
