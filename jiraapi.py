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
        # Поисковая строка для получения пула тикетов Jira
        jql = '(summary ~ "1????" OR summary ~ "2????") AND status != Done AND status != Declined'
        # Опции для подключения к серверу Jira
        #  сервер:
        jira_options = {'server': 'https://jira.zyfra.com'}
        dotenv_path = os.path.join(os.path.dirname(__file__),'.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            jira_login = os.getenv("JIRA_LOGIN")
            jira_pass = os.getenv("JIRA_PASS")
        else:
            jira_login = input('Введи логин пользователя Jira: ')
            jira_pass = input('Введи пароль: ')
        # Объявляем переменную - объект JIRA, выполняя обращение к серверу
        self.jira = JIRA(options=jira_options, basic_auth=(jira_login, jira_pass))
        # Количество дней от текущего момента в прошлое, за которое требуется обработать задачи
        self.delta = timedelta(days=int(input('Введи число дней, за которое читать Jira: ')))
        # Список тикетов, полученные запросом из Jira
        self.issues_list = self.jira.search_issues(jql, maxResults=1000)
        # Время в UTC
        self.utc = pytz.UTC


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

        self.file_begins_ends('begin')
        # Перебираем список тикетов, полученных при инициализации
        for i in self.issues_list:
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
        self.file_begins_ends('begin')

        for i in self.issues_list:
            issue = self.jira.issue(str(i))
            if len(issue.fields.comment.comments) != 0:
                for comment in issue.fields.comment.comments:
                    if comment.author.displayName == username:
                        self.write_data(issue, comment)

        self.file_begins_ends('end')

    def non_tp_last_comment(self):
        self.file_begins_ends('begin')

        tp_names_list = ['Anton Nagovitsin', 'Aleksey Polyakov', 'Pavel Khromov', 'Sergey Kondratyev', 'Anton Mulenkov',
                         'Yuriy.Likhanov']

        for i in self.issues_list:
            issue = self.jira.issue(str(i))
            if 'VISTHELP2' in str(issue):
                if len(issue.fields.comment.comments) != 0:
                    lastcomment = issue.fields.comment.comments[-1]
                    if lastcomment.author.displayName not in tp_names_list:
                        if dateutil.parser.isoparse(lastcomment.created) > self.utc.localize(
                                datetime.today() - self.delta):
                            self.write_data(issue, lastcomment)

        self.file_begins_ends('end')



    def check_comments(self):
        """
        Функция для получения коследнего комментария по всем задачам, удовлетворяющим поисковому запросу из блока init
        :return: Функция ничего не возвращает, результатом работы функции является html-файл, который можно открыть в
        браузере.
        """

        self.file_begins_ends('begin')

        # Перебираем список тикетов, полученных при инициализации
        for i in self.issues_list:
            issue = self.jira.issue(str(i))
            # В явном виде проверяем задачи только проекта VISTHELP2
            #if 'VISTHELP2' in str(issue):
            # Если есть комментарии в задаче
            if len(issue.fields.comment.comments) != 0:
                # Берем последний комментарий задачи
                lastcomment = issue.fields.comment.comments[-1]
                # Если комментарий не старше определенного при инициализации количества дней delta
                if dateutil.parser.isoparse(lastcomment.created) > self.utc.localize(datetime.today() - self.delta):
                    # Вызываем функцию записи в файл
                    self.write_data(issue, lastcomment)

        self.file_begins_ends('end')


    def update_label(self):
        print(self.issues_list[0])
        # pass
