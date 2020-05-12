import requests
from bs4 import BeautifulSoup


def price_extracter(u):
    # print('dzialamy')
    soup = get_soup_bankier(u)
    price_descr = soup.find('div', class_="profilLast")     #jeśli nie znajdzie - zła strona - zwraca None
    
    if price_descr is None: 
        return None

    price = price_descr.text    #znajduje cenę
    price_soup = soup.find('div', class_="right textNowrap")
    change1 = price_soup.find('span')                   #znajduje zmiane
    change2 = change1.next_sibling.next_sibling         #znajduje zmiane
    return price, change1.text, change2.text        #zwraca 3 stringi do obrobki


def get_soup_bankier(symbol):
    url = 'https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=' + symbol
    resource = requests.get(url).text
    souped_resource = BeautifulSoup(resource, 'html.parser')
    return souped_resource


def price_printer( res_tuple ):
    if res_tuple is None: print('blad')
    res_tuple_converted = map(convert_to_number, res_tuple)
    (price, ch1, ch2) = res_tuple_converted
    print(f'obecna cena to {price} \n')
    print(f'zmiana: {ch1}% // {ch2}')


def convert_to_number(n):
    n=n.strip(' ')
    res = ''
    for char in n:
        if char.isnumeric() or char == '-':
            res += char
        elif char == ',' :
            res += '.'
        elif char.lower() == 'u' or char == '%':
            break
        else: 
            pass
    return float(res)


def program():
    while True:
        s0 = input('exit aby wyjsc. jaki surowiec? ')
        if s0 == 'exit': break
        if s0 == '': s0 = 'zloto'
        try:
            price_printer( price_extracter(s0) )
        except AttributeError:
            print('nie znaleziono')

if __name__ == '__main__':
    program()