import requests
from bs4 import BeautifulSoup


def extract_prices(symbol):         # extracts desired data
    url = 'https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=' + symbol
    resource = requests.get(url).text
    soup = BeautifulSoup(resource, 'html.parser')

    price_descr = soup.find('div', class_="profilLast")      # if not found - gives None
    
    if price_descr is None:             
        raise ScrappingFailed(f'failed to get data from {url}')

    price = price_descr.text                            # current price
    price_soup = soup.find('div', class_="right textNowrap")
    change1 = price_soup.find('span')                   # change 1
    change2 = change1.next_sibling.next_sibling         # change 2
    return price, change1.text, change2.text        # returns 3 string values

# for testing
# def price_printer( res_tuple ):
#     if res_tuple is None: print('blad')
#     res_tuple_converted = map(convert_to_number, res_tuple)
#     (price, ch1, ch2) = res_tuple_converted
#     print(f'obecna cena to {price} \n')
#     print(f'zmiana: {ch1}% // {ch2}')

def convert_to_number(n): # function converting strings to float (there are other characters to trim)
    n=n.strip(' ')
    res = ''
    for char in n:
        if char.isnumeric() or char == '-':
            res += char
        elif char == ',' :
            res += '.'
        elif char.lower() == 'u' or char == '%': # means end of useful data
            break
        else: 
            pass
    return float(res)

# def program():
#     while True:
#         s0 = input('exit aby wyjsc. jaki surowiec? ')
#         if s0 == 'exit': break
#         if s0 == '': s0 = 'zloto'
#         try:
#             price_printer( price_extracter(s0) )
#         except AttributeError:
#             print('nie znaleziono')

# used decorator for fun
def convert_decorator(funkcja):
    def returns_converted(s):
        result_tuple = funkcja(s)
        if result_tuple is None: return None
        return tuple(convert_to_number(n) for n in result_tuple)
    return returns_converted

class ScrappingFailed(Exception):
    pass


price_extracter_conv = convert_decorator(extract_prices)   # function our site needs


if __name__ == '__main__':
    # program()
    pass