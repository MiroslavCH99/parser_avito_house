from bs4 import BeautifulSoup
from selenium import webdriver

from config.logging_config import logger
from app.google_sheets_app.sheets_script import get_columns_sheets
def get_avito_page(url:str)->dict:
    '''
    Парсер для авито
    :param url: ссылка с авито
    :return: вся информаия с сайта об объекте
    '''
    driver = webdriver.Chrome()
    driver.get(url)
    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, 'html.parser')
    result = {}
    result['cite'] = 'avito'
    result['url'] = url
    result['price'] = soup.find('span', {'itemprop': 'price'})['content']

    # Проходим по всем 'таблицам' в объявлении
    for ul in soup.find_all('ul', class_='HRzg1'):
        for li in ul.find_all('li', class_='cHzV4'):
            # Находим первую часть — метку
            label_span = li.find('span', class_='Lg7Ax')
            if not label_span:
                continue

            full_text = li.get_text(strip=True).replace('\xa0', ' ')
            label, value = full_text.split(':')
            result[label] = value

    #добаление адреса
    address = soup.find('span', class_='xLPJ6').get_text(strip=True)
    if address:
        result['addres']=address

    return result

def get_cian_page(url:str)->dict:
    '''
    Парсер для циан
    :param url: ссылка с циан
    :return: вся информаия с сайта об объекте
    '''
    driver = webdriver.Chrome()
    driver.get(url)
    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, 'html.parser')
    result = {}
    result['cite'] = 'cian'
    result['url'] = url
    price_div = soup.find('div', attrs={'data-testid': 'price-amount'})
    if not price_div:
        return None

    # Забираем весь текст внутри, например "72 000 ₽/мес."
    text = price_div.get_text(strip=True)
    result['price'] = text.replace('\u00A0', '').replace(' ', '').split('₽')[0]
    title = soup.find('h1', class_='a10a3f92e9--title--vlZwT').get_text(strip=True)
    result['Количество комнат'] = next((ch for ch in title if ch.isdigit()), None)

    # Ищем все блоки групп
    for group in soup.find_all("div", attrs={"data-name": "OfferSummaryInfoGroup"}):
        header = group.find("h2")
        if not header:
            continue

        # Внутри каждой группы — множество OfferSummaryInfoItem
        for item in group.find_all("div", attrs={"data-name": "OfferSummaryInfoItem"}):
            ps = item.find_all("p")
            if len(ps) >= 2:
                label = ps[0].get_text(strip=True)
                value = ps[1].get_text(strip=True).replace('\xa0', ' ')

            result[label] = value

    #Извлекаем адрес
    container = soup.find('div', class_='a10a3f92e9--address-line--GRDTb')
    if not container:
        return None

    # Находим все элементы адреса
    address_items = container.find_all('a', attrs={'data-name': 'AddressItem'})
    if not address_items:
        return None

    # Собираем текст всех <a> и объединяем
    parts = [item.get_text(strip=True) for item in address_items]
    result['addres'] = ', '.join(parts)
    result['Этаж'] = [i.get_text() for i in soup.find_all('div', class_='a10a3f92e9--text--eplgM') if "Этаж" in i.get_text()][0].replace('Этаж', '')
    return result


def get_json_house(url)->dict:
    '''
    Парсим данные с сайта объявлений и унифицируем их
    :param url: ссылка на объект
    :return: словарь с унифицированными данными
    '''
    try:
        site = url.split('.')[1]
    except IndexError:
        return "Некорректная ссылка"
    try:
        short_url = url.split('?')[0]
    except IndexError:
        return "Некорректная ссылка"
    list_url_sheet = get_columns_sheets()
    if short_url in list_url_sheet:
        return "Ссылка уже есть в таблице"
    if site=='cian':
        json = get_cian_page(short_url)
        return {
            'url': json['url'],
            'site': json['cite'],
            'rooms': json['Количество комнат'],
            'area': json['Общая площадь'],
            'price': json['price'],
            'floor': json['Этаж'],
            'repair': json['Ремонт'],
            'bilding_year': json['Год постройки'],
            'addres': json['addres']
        }
    elif site=='avito':
        json = get_avito_page(short_url)
        return {
            'url': json['url'],
            'site': json['cite'],
            'rooms': json['Количество комнат'],
            'area': json['Общая площадь'],
            'price': json['price'],
            'floor': json['Этаж'],
            'repair': json['Ремонт'],
            'bilding_year': json['Год постройки'],
            'addres': json['addres']
        }
    else:
        return "Некорректная ссылка"
        logger.error('Получена некорректная ссылка')


if __name__=="__main__":
    print(get_json_house('https://www.cian.ru/rent/flat/319088502/'))