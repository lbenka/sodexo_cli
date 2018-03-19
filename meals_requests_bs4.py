import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import click


@click.command()
@click.option('--username', prompt='Your name', help='User name for logging into account')
@click.option('--password', prompt='Your password', help='User password for logging into account')
def get_meals_balance(username, password):
    s = requests.Session()
    r = s.get('https://www.sodexo-ucet.cz/')
    soup = BeautifulSoup(r.content, 'html.parser')

    token = None
    for inp in soup.find_all('input'):
        if inp.get('name') == "__RequestVerificationToken":
            token = inp.get('value')
            break

    if not token:
        return 'cannot find token'

    params = {
        "__RequestVerificationToken": token,
        'CallbackKey': '',
        'CallbackQueryString': '',
        'LoginAsEmployee': False,
        'Username': username,
        'Password': password
    }

    s.post('https://www.sodexo-ucet.cz/', data=params)
    r = s.get('https://www.sodexo-ucet.cz/Dashboard/Index')
    soup = BeautifulSoup(r.content, 'html.parser')

    code = soup.find_all(href=re.compile("employeeCode"))
    if code:
        code = code[0].get('href')
    r = s.get(urljoin('https://www.sodexo-ucet.cz/', code))

    r = s.post('https://karta.sodexo-ucet.cz/Home/GetAccountsAjax', data={'sort': '', 'group': '', 'filter': ''})

    account_balance = None
    for acc in r.json()['Data']:
        if acc['AccountTypeName'] == 'Stravenkový účet':
            account_balance = acc['Balance']
            break

    return click.echo(account_balance)


if __name__ == '__main__':
    get_meals_balance()
