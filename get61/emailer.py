#!/opt/anaconda3/bin/python3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from string import Template
from score_table import get_leaderboard
import pandas as pd

MY_ADDRESS = 'andrewduncansweeney@gmail.com'
PASSWORD = 'kyzvljcflfpzobpc'

def get_contacts(filename):
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for contact in contacts_file:
            names.append(contact.split()[0])
            emails.append(contact.split()[1])
    return names, emails

def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def main():
    names, emails = get_contacts('contacts.txt')
    #message_template = read_template('message.txt')
    userlist = {'Ben Statz': 'Casetta Bloody Mary', 'Ryan Kelly': 'RKD', 'Gena Rieger-Olson': 'The L in MSLGL',
                'Duncan Sweeney': 'Duncan', 'Jacob Hanke': 'jacobhanke12', 'Edward Mckenna': 'Dr Brad Peck',
                'Thomas Gering': 'KingCrab',
                'Andrew Wells': '3SheepsToTheWind', 'Ticho': 'Andrew Ticho', 'Brett Falkowski': 'Falko',
                'Sam Reinertson': 'Riding Lawnmauer', 'Nate Bartz': 'Moonblatz', 'Bret Olson': 'Bert Olson',
                'Dan Brunner': 'DPB', 'Srdjan Gajic': 'Provie', 'James Madsen': 'James Madsen'}

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    for name, email in zip(names, emails):
        msg = MIMEMultipart()  # creates message.txt

        #message = message_template.substitute(PERSON_NAME=name.title())
        score_df = get_leaderboard('https://get61.com/leaderboard?lifetime=true&sortBy=lifetime_score', userlist)

        #print(message)

        msg['From'] = MY_ADDRESS
        msg['To'] = email
        msg['Subject'] = 'This Weeks Scores'

        html = """\
        <html>
            <head></head>
            <body>
                {0}
            <body>
        </html>
        """.format(score_df.to_html())
        part1 = MIMEText(html, 'html')
        msg.attach(part1)

        s.send_message(msg)
        del msg
    s.quit()

if __name__ == '__main__':
    main()

