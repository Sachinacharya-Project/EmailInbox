import imaplib, email, os
from bs4 import BeautifulSoup
from pwinput import pwinput
from dotenv import load_dotenv
from tqdm import tqdm
load_dotenv()

username = os.environ.get('USEREMAIL', None)
password = os.environ.get('LESSSECURE_PASS', None)

if username == None:
    username = input("Email: ")
if password == None:
    password = pwinput()

host = 'imap.gmail.com'
mail = imaplib.IMAP4_SSL(host)

print("[SIGNIN WITH ]\n{}\n".format(username))

try:
    mail.login(username, password)
    print("Logged in Successfully\n")
except mail.error:
    print("""Error Occured
          Cannot logged into your email
          Reason(s)
            1. Invalid Credentials
            2. Disabled 'Allowed on less secure app' in account setting
            (Google Account Admin Panel > Security > Turn ON allow less secure app)
            3. If option 2 is not available for you, then you must have 2-Step Verification
            (Google Account Admin Panel > Security > Sign into Google > App Password (Get 16-digit code))
            
        Exiting Program\nTry again after check all above possibility
          """)
    exit(1)
mail.select('inbox')

def get_messages():
    search_data = mail.search(None, 'UNSEEN')[1]
    search_items = search_data[0].split()
    output = ''
    print('[TOTAL UNSEEN MESSAGES] {}'.format(len(search_items)))
    print("RETRIVING ALL {} MESSAGES".format(len(search_items)))

    for num in tqdm(search_items):
        data = mail.fetch(num, '(RFC822)')[1]
        b = data[0][1]
        email_message = email.message_from_bytes(b)
        for header in ['Subject', 'To', 'From', 'Date']:
            # First changes
            
            output += "[{}]: {}\n".format(header, email_message[header.lower()])
            # print("{}: {}".format(header, email_message[header.lower()]))
        output += "[Content-Type]: {}".format(str(email_message['Content-Type']).split(';')[0])
        # print('Content-Type: {}'.format(str(email_message['Content-Type']).split(';')[0]))
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain' or part.get_content_type() == 'text/html':
                body = part.get_payload(decode=True)
                soup = BeautifulSoup(body.decode(), features="lxml")
                output += "[Messages]\n{}\n".format(soup.get_text())
                # print('Messages:')
                # print(soup.get_text())
    if len(search_items) < 100:
        print("[INBOX MESSAGES]")
        print(output)
    else:
        print("AMOUNTS OF MESSAGES ARE VERY LARGE TO DISPLAY ON CONSOLE.")
        print("MESSAGES ARE SAVED IN FILE UNDER THE NAME 'output_messages.txt'")
        with open('output_messages.txt', 'w') as file:
            file.seek(0)
            file.truncate()
            file.write("[INBOX MESSAGES]\n")
            file.write(output)
if __name__ == '__main__':
    get_messages()