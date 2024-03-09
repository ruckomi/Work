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

    def check_content(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        users_raw, users_final = self.extract_users(soup)
        if len(users_raw) == len(set(users_final)):
            print(f'No duplicities found at adress {url}')
            return True
        else:
            print(f'Url: {url} probably contains duplicities!')
            return url

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
        return users, final

    def divide_to_chunks(self, l, n): 
        for i in range(0, len(l), n):  
            yield l[i:i + n] 

def main(
    interval: int = typer.Option(
        help='Interval for duplicity check in hours.'
    ),
    mail: str = typer.Option(
        help='Email which will recieve notifications.'
    )
):
    checker = DuplicityChecker()
    sender = MailSender(reciever_mail=mail)

    while True:
        logging.info('Checking for duplicities.')
        errors = []
        for url in urls:
            url = checker.check_content(url)
            if not url:
                errors.append(url)

        if len(errors) > 0:
            logging.info(f'Sending notitfication to {mail}.')
            sender.send_mail(errors)
        else:
            logging.info(f'Sending notitfication to {mail}.')
            sender.send_mail(urls)
        logging.info('Waiting for next check.')
        time.sleep(interval * 60 * 60)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:\t%(message)s'
    )
    typer.run(main)
