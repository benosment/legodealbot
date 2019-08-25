#! /usr/bin/env python3

import praw
import re
import logging
import logging.config
import os
import smtplib
from email.generator import Generator
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO
from twilio.rest import Client

query_terms = ['assembly square', 'treehouse', 'modular', 'overwatch', 'architecture']


def search_post(submission):
    found_list = []
    for query in query_terms:
        pattern = re.compile(query)
        match = pattern.search(submission.title.lower())
        if match:
            found_list.append(match.group(0))
        match = pattern.search(submission.selftext.lower())
        if match:
            found_list.append(match.group(0))
    return set(found_list)


def send_email(subject, body):
    try:
        gmail_user = os.environ.get('MAIL_USERNAME')
        gmail_password = os.environ.get('MAIL_PASSWORD')
    except:
        logging.exception('unable to import mail username/password')
        raise

    if not gmail_user or not gmail_password:
        raise EnvironmentError('invalid user or password for sending mail')

    from_address = ['pycomic-v2', gmail_user]
    recipient = ['Master', gmail_user]

    print(subject, body)
    # 'alternative' MIME type - HTML and plaintext bundled in one email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '%s' % Header(subject, 'utf-8')
    msg['From'] = '"%s" <%s>' % (Header(from_address[0], 'utf-8'),
                                 from_address[1])
    msg['To'] = '"%s" <%s>' % (Header(recipient[0], 'utf-8'), recipient[1])

    htmlpart = MIMEText(body, 'html', 'UTF-8')
    msg.attach(htmlpart)
    str_io = StringIO()
    gen = Generator(str_io, False)
    gen.flatten(msg)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, gmail_user, str_io.getvalue())
        server.close()
    except smtplib.SMTPException:
        logging.error('Failed to send mail')


def send_text(msg):
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_NUMBER')
    my_number = os.environ.get('MY_PHONE')

    if not all([twilio_number, twilio_account_sid, twilio_auth_token]):
        raise Exception("Twilio environment variables not configured")

    client = Client(twilio_account_sid, twilio_auth_token)
    client.messages.create(
        to=my_number, from_=twilio_number,
        body=msg)


def notify(submission, match_list):
    logging.debug('Found: %s [%s]', submission.title, submission.url)
    email_title = submission.title
    email_body = 'Link: %s\n\n %s' % (submission.url,
                                      submission.selftext)
    for match in match_list:
        pattern = re.compile(re.escape(match), re.IGNORECASE)
        email_body = pattern.sub('<mark>%s</mark>' % match, email_body)
    email_body = 'Matched: <b>%s</b>\n\n' % (', '.join(match_list)) + email_body
    email_body = email_body.replace('\n', '<br>')
    send_email(email_title, email_body)

    msg = "Found: %s - %s" % (' '.join(match_list), submission.permalink)
    print(msg)
    send_text(msg)


if __name__ == '__main__':
    reddit = praw.Reddit('legodealbot')
    subreddit = reddit.subreddit('legodeal')

    for submission in subreddit.stream.submissions():
        print('Searching post: %s' % submission.title)
        found = search_post(submission)
        if found:
            notify(submission, found)
