from jira import JIRA
from datetime import timedelta, datetime
import dateutil.parser
import pytz


class Jira:
    def __init__(self):
        jql = '(summary ~ "1????" OR summary ~ "2????") AND status != Done AND status != Declined'
        jira_options = {'server': 'https://jira.zyfra.com'}
        jira_login = input('Введи логин пользователя Jira: ')
        jira_pass = input('Введи пароль: ')
        self.jira = JIRA(options=jira_options, basic_auth=(jira_login, jira_pass))
        self.days = int(input('Введи число дней, за которое читать Jira: '))
        self.issues_list = self.jira.search_issues(jql, maxResults=1000)
        self.delta = timedelta(days=self.days)
        self.utc = pytz.UTC
        self.string_before = ["<!DOCTYPE html>", "<html lang=\"ru\">", "<head>",
                              "    <title>Выгрузка из Джиры</title>", "    <meta charset=\"utf-8\">",
                              "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
                              "	   <style>",
                              "h2 { text-align: center; font-family: Verdana, Arial, Helvetica, sans-serif; color: #336; }",
                              "h3 { text-align: center; font-family: Verdana, Arial, Helvetica, sans-serif; color: blue; }",
                              "   p { color: green; }", "	</style>", "</head> ", "<body>",
                              "			<h2>Последние комментарии</h2>", '\n',
                              "    <section id=\"docs\" style=\"margin: 5%;\">"]

        self.string_after = ["    </section>", "</body>", "</html> "]

    def last_comment(self):
        filename = 'jiraReport' + datetime.now().ctime() + '.html'

        filename = filename.replace(' ', '_')
        filename = filename.replace(':', '')

        f = open(filename, 'w')

        for line in self.string_before:
            f.write(line)
            f.write('\n')

        for i in self.issues_list:
            issue = self.jira.issue(str(i))
            if 'VISTHELP2' in str(issue):
                if len(issue.fields.comment.comments) != 0:
                    lastcomment = issue.fields.comment.comments[-1]
                    if dateutil.parser.isoparse(lastcomment.created) > self.utc.localize(datetime.today() - self.delta):
                        f.write("\n			<div>")
                        f.write("\n				<h3><a href=\"" + "https://jira.zyfra.com/browse/" + str(
                            issue) + "\" target=\"new\">" + issue.fields.summary + "</a></h3>")
                        f.write("\n				<p>" + dateutil.parser.isoparse(
                            lastcomment.created).ctime() + "</p>")
                        f.write("\n				<p>" + lastcomment.author.displayName + "</p>")
                        f.write("\n				<p>" + lastcomment.body + "</p>")
                        f.write('=' * 100)

        for line in self.string_after:
            f.write(line)
            f.write('\n')

        f.close()

    def all_user_comments(self, username='Dmitriy Protasov'):
        filename = 'jiraReport' + datetime.now().ctime() + '.html'
        filename = filename.replace(' ', '_')
        filename = filename.replace(':', '')

        f = open(filename, 'w')

        for line in self.string_before:
            f.write(line)
            f.write('\n')

        for i in self.issues_list:
            issue = self.jira.issue(str(i))
            if len(issue.fields.comment.comments) != 0:
                for comment in issue.fields.comment.comments:
                    if comment.author.displayName == username:
                        f.write("\n			<div>")
                        f.write("\n				<h3><a href=\"" + "https://jira.zyfra.com/browse/" + str(
                            issue) + "\" target=\"new\">" + issue.fields.summary + "</a></h3>")
                        f.write("\n				<p>" + dateutil.parser.isoparse(comment.created).ctime() + "</p>")
                        f.write("\n				<p>" + comment.author.displayName + "</p>")
                        f.write("\n				<p>" + comment.body + "</p>")
                        f.write('\n'+'=' * 100+'\n')

        for line in self.string_after:
            f.write(line)
            f.write('\n')

        f.close()

    def non_tp_last_comment(self):
        filename = 'jiraReport' + datetime.now().ctime() + '.html'
        filename = filename.replace(' ', '_')
        filename = filename.replace(':', '')

        f = open(filename, 'w')

        for line in self.string_before:
            f.write(line)
            f.write('\n')

        tp_names_list = ['Anton Nagovitsin', 'Aleksey Polyakov', 'Pavel Khromov', 'Sergey Kondratyev', 'Anton Mulenkov',
                         'Yuriy.Likhanov']

        f = open(filename, 'w')

        for i in self.issues_list:
            issue = self.jira.issue(str(i))
            if 'VISTHELP2' in str(issue):
                if len(issue.fields.comment.comments) != 0:
                    lastcomment = issue.fields.comment.comments[-1]
                    if lastcomment.author.displayName not in tp_names_list:
                        if dateutil.parser.isoparse(lastcomment.created) > self.utc.localize(
                                datetime.today() - self.delta):
                            f.write("\n			<div>")
                            f.write("\n				<h3><a href=\"" + "https://jira.zyfra.com/browse/" + str(
                                issue) + "\" target=\"new\">" + issue.fields.summary + "</a></h3>")
                            f.write(
                                "\n				<p>" + dateutil.parser.isoparse(lastcomment.created).ctime() + "</p>")
                            f.write("\n				<p>" + lastcomment.author.displayName + "</p>")
                            f.write("\n				<p>" + lastcomment.body + "</p>")
                            f.write('\n' + '=' * 100 + '\n')

        f.close()
