from requests_html import HTMLSession
import click


@click.command()
@click.option('--username', prompt='Your name', help='User name for logging into account')
@click.option('--password', prompt='Your password', help='User password for logging into account')
def get_meals_balance(username, password):
    s = HTMLSession()
    r = s.get('https://www.sodexo-ucet.cz/')

    token = None
    for inp in r.html.find('input'):
        if inp.attrs.get('name') == "__RequestVerificationToken":
            token = inp.attrs.get('value')
            break

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

    link = None
    for l in r.html.absolute_links:
        if 'employeeCode' in l:
            link = l
            break

    s.get(link)
    r = s.post('https://karta.sodexo-ucet.cz/Home/GetAccountsAjax', data={'sort': '', 'group': '', 'filter': ''})

    account_balance = None
    for acc in r.json()['Data']:
        if acc['AccountTypeName'] == 'Stravenkový účet':
            account_balance = acc['Balance']
            break

    return click.echo(account_balance)


if __name__ == '__main__':
    get_meals_balance()
