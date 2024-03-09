import requests
from dataclasses import dataclass
import time
import logging

from bs4 import BeautifulSoup
import typer

from sender import MailSender


urls = [
    'https://www.eosc.cz/pracovni-skupiny/architektura-narodni-datove-infrastruktury',
    'https://www.eosc.cz/pracovni-skupiny/metadata',
    'https://www.eosc.cz/pracovni-skupiny/zakladni-sluzby',
    'https://www.eosc.cz/pracovni-skupiny/vzdelavani-a-lidske-zdroje',
    'https://www.eosc.cz/pracovni-skupiny/biozdravipotraviny',
    'https://www.eosc.cz/pracovni-skupiny/materialove-vedy-a-technologie',
    'https://www.eosc.cz/pracovni-skupiny/data-management-pro-umelou-inteligenci-a-strojove-uceni',
    'https://www.eosc.cz/pracovni-skupiny/socialni-vedy',
    'https://www.eosc.cz/pracovni-skupiny/fyzikalni-vedy',
    'https://www.eosc.cz/pracovni-skupiny/humanitni-vedy-a-umeni',
    'https://www.eosc.cz/pracovni-skupiny/environmentalni-vedy',
    'https://www.eosc.cz/pracovni-skupiny/citliva-data'
]


@dataclass(unsafe_hash=True)
class User:
    last_name: str
    first_name: str
    institution: str


class DuplicityChecker:

    def __init__(self, debug: bool):
        self.debug = debug

    def check_content(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        users = self.extract_users(soup)

        duplicated = self.find_duplicate_user(users)
        if len(duplicated) == 0:
        # if len(users_raw) == len(set(users_final)):
            print(f'No duplicities found at adress {url}')
            return duplicated, True
        else:
            return duplicated, False

    def find_duplicate_user(self, users):
        seen = set()
        dupes = []

        for user in users:
            if user in seen:
                dupes.append(user)
            else:
                seen.add(user)
        return dupes


    def extract_users(self, scrape):
        td_elements = scrape.find_all('td')
        elements = []
        for element in td_elements:
            if len(element.contents) > 0:
                elements.append(element.contents[0])
            else:
                elements.append(None)
        
        users = list(self.divide_to_chunks(elements, 3))

        final = []
        for user in users:
            final.append(
                User(
                    last_name=user[0],
                    first_name=user[1],
                    institution=user[2]
                )
            )
        if self.debug:
            logging.info('DEBUG mode! Adding dummy users.')
            final.append(final[-1])
            final.append(final[0])

        return final

    def divide_to_chunks(self, l, n): 
        for i in range(0, len(l), n):  
            yield l[i:i + n] 

def main(
    interval: int = typer.Option(
        help='Interval for duplicity check in hours.'
    ),
    mail: str = typer.Option(
        help='Email which will recieve notifications.'
    ),
    debug: bool = typer.Option(
        help='Debug mode will add first user twice to check functionality.'
    )
):
    checker = DuplicityChecker(debug=debug)
    sender = MailSender(reciever_mail=mail)

    while True:
        logging.info('Checking for duplicities.')
        errors = []
        dup_names = []
        for url in urls:
            dupl, url_check = checker.check_content(url)
            if not url_check:
                errors.append(url)
                dup_names.append(dupl)
        
        if len(errors) > 0:
            logging.info(f'Sending notitfication to {mail}.')
            sender.send_mail(errors, dup_names)
        else:
            logging.info('No duplicity found.')
            # sender.send_mail(urls)
        logging.info('Waiting for next check.')
        time.sleep(interval * 60 * 60)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:\t%(message)s'
    )
    typer.run(main)
