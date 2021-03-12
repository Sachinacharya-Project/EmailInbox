import imaplib, email, os
from bs4 import BeautifulSoup
username = os.environ.get('USEREMAIL')
password = os.environ.get('USERPASS')
host = 'imap.gmail.com'

mail = imaplib.IMAP4_SSL(host)
mail.login(username, password)
mail.select('inbox')

def get_messages():
    search_data = mail.search(None, 'UNSEEN')[1]
    print('Total Unseen: {}'.format(len(search_data[0].split())))
    for num in search_data[0].split():
        data = mail.fetch(num, '(RFC822)')[1]
        b = data[0][1]
        email_message = email.message_from_bytes(b)
        for header in ['Subject', 'To', 'From', 'Date']:
            print("{}: {}".format(header, email_message[header.lower()]))
        print('Content-Type: {}'.format(str(email_message['Content-Type']).split(';')[0]))
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain' or part.get_content_type() == 'text/html':
                body = part.get_payload(decode=True)
                soup = BeautifulSoup(body.decode(), features="lxml")
                print('Messages:')
                print(soup.get_text())
if __name__ == '__main__':
    get_messages()