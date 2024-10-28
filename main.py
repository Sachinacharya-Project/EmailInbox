from typing import TypedDict, List
from bs4 import BeautifulSoup
from colorama import Fore, init
from tqdm import tqdm
import imaplib
import email

init(autoreset=True)


TypedOutput = TypedDict(
    "TypedOutput",
    {
        "Subject": str,
        "To": str,
        "From": str,
        "Date": str,
        "Content-Type": str,
        "Body": str,
    },
)


class Inbox:
    host = "imap.gmail.com"

    def __init__(self, host: str | None = None) -> None:
        """Read Inbox from mail provider.

        Args:
            host (str | None, optional): Host url for the Mail Server. Defaults to 'imap.gmail.com'.
        """
        if host:
            self.host = host
        self.mail = imaplib.IMAP4_SSL(self.host)

    def login(self, user: str, password: str):
        """Sign in the User to the Server, This method must be called before calling get_messages() method.

        Args:
            user (str): User / Email to authenticate
            password (str): Password corresponding to user for signin.

        Returns:
            bool: If signin is success, it returns True otherwise returns False.
        """
        print(
            f"{Fore.WHITE}[Connecting]{Fore.LIGHTWHITE_EX} Connecting to host as {user}"
        )
        try:
            self.mail.login(user, password)
            print(
                f"{Fore.LIGHTGREEN_EX}[Login]{Fore.GREEN} {user} has logged in successfully."
            )
            return True
        except self.mail.error as e:
            print(f"{Fore.RED}[Error]{Fore.LIGHTRED_EX} Cannot login the user.n\n", e)
            return False

    def get_messages(self) -> List[TypedOutput]:
        """Retrive all the messages of type Plain Text and HTML from the Inbox.

        Returns:
            List[TypedOutput]: List of informations of the messages / mail.
        """
        self.mail.select("INBOX")

        output: List[TypedOutput] = []
        searched_data = self.mail.search(None, "UNSEEN")[1]
        searched_data = searched_data[0].split()

        print(
            f"\n{Fore.CYAN}[Count]{Fore.LIGHTCYAN_EX} There are total of {len(searched_data)} unseen messages."
        )
        print(
            f"{Fore.BLUE}[NOTE]{Fore.LIGHTBLUE_EX} Only messages of type 'text/plain' and 'text/html' are read.\n"
        )

        for data in tqdm(searched_data):
            data_ = self.mail.fetch(data, "(RFC822)")[1]
            b = data_[0][1]
            email_message = email.message_from_bytes(b)

            temp_data: TypedOutput = {
                "Subject": email_message["subject"],
                "To": email_message["to"],
                "From": email_message["from"],
                "Date": email_message["date"],
                "Content-Type": email_message["Content-Type"],
            }

            for part in email_message.walk():
                if (
                    part.get_content_type() == "text/plain"
                    or part.get_content_type() == "text/html"
                ):
                    body = part.get_payload(decode=True)
                    soup = BeautifulSoup(body, "html.parser")
                    temp_data["Body"] = soup.get_text()
            output.append(temp_data)
        return output


if __name__ == "__main__":
    import json

    inbox = Inbox()
    inbox.login("email-address", "password")

    with open("data.json", "w") as file:
        json.dump(inbox.get_messages(), file, indent=4)
