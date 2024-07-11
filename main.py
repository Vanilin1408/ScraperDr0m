import time
import requests
from bs4 import BeautifulSoup
import csv


def extract_data(block, attr: str, attr_class: str, default=None):
    try:
        data = block.find(attr, class_=attr_class)
        return data.text if data else default
    except AttributeError:
        return default


def recording_in_csv(list_data: list) -> None:  # writing data to a csv-file
    with open('DATA.csv', 'w', newline='') as csv_file:
        csv_file.truncate(0)
        try:
            fieldnames = list_data[0].keys()
        except IndexError:
            print('No data to create CSV database file.')
            return
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in list_data:
            writer.writerow(row)
        list_data.clear()
    return


def parse_site(base_url: str) -> None:
    if base_url[-1] != '/':         # just checking the slash for correctness
        base_url: str = f'{base_url}/'

    if "drom.ru" not in base_url:      # just checking that we are going to 'DR0M'
        print("The parser was developed for the 'drome.ru' site, the link does not work another.")
        return

    session = requests.Session()

    try:
        response = session.get(base_url)    # checking the provided link for availability
    except requests.exceptions.RequestException as request_err:
        print(f'Connection error -> {request_err}')
        return

    # to BS lxml
    response_soup = BeautifulSoup(response.text, 'lxml')

    '''
    So, since the <dr0m> developers made a new number format, had to change the formatting 
    for processing the tag with the number of ads
    '''
    try:
        # Take a tag info about count and convert to "int"
        str_info_count_ads: str = response_soup.find('div', class_='css-1xkq48l eckkbc90').text.split(' ')[0]
        amount_ads: int = int(''.join([char for char in str_info_count_ads if char.isdigit()]))  # amount of ads
    except AttributeError:
        try:  # Try to count the pages in a different way, checking the correctness of the link.
            str_info_count_ads: str = response_soup.find('a', class_='css-14yriw2 e1px31z30').text.split(' ')[0]
            amount_ads: int = int(''.join([char for char in str_info_count_ads if char.isdigit()]))
        except AttributeError:
            print("Unable to read pages from site, check if the link "
                  "is correctly written and if any model is selected.\n"
                  "If link is correct -> try to restart.\n"
                  "If this doesn't help -> contact support.")
            return

    max_page: int = amount_ads // 20 + 1 if amount_ads % 20 != 0 else amount_ads // 20  # the last page on site
    list_cars: list = []  # advertisement list
    id_car: int = 0  # var for car ID in table
    dict_buff: dict = {
        '<id>': 0,  # ads (car) attributes
        '<model>': None,
        '<equipment>': None,
        '<description>': None,
        '<price>': None,
        '<location>': None,
        '<link>': None
    }
    print(f'Pages count: {max_page}')

    postfix_url: str = ''    # postfix for processing url with '/?distance=n'
    if '/?distance=' in base_url:    # processing tabs with + 'n' km
        postfix_url = base_url[base_url.find("/?distance"):len(base_url) - 1]
        base_url = base_url[:base_url.find("/?distance") + 1]
    print('Reading...')

    for ind_page in range(1, max_page + 1):  # for every page
        new_url: str = f'{base_url}page{ind_page}{postfix_url}'   # convert the url with\out postfix to the given page
        print(f'Giving the page {ind_page}')

        session = requests.Session()
        try:
            response = session.get(new_url)
        except requests.exceptions.RequestException as request_err:
            print(f'Connection error, error status -> {request_err}')
            return

        response_soup = BeautifulSoup(response.text, 'lxml')

        # MAIN class names of sections, blocks with ads
        name_of_main_section_class: str = "css-1nvf6xk ejck0o60"
        name_of_blocks_class: str = "css-1f68fiz ea1vuk60"

        section = response_soup.find('div', class_=name_of_main_section_class)  # get section with blocks
        if section is None:  # CAPTCHA bypass
            try:
                print('Сaught the captcha or error by TAG NAME, now trying again (*_*)')
                time.sleep(2)     # delay for current page, because captcha
                response = session.get(new_url)     # and again req
                response_soup = BeautifulSoup(response.text, 'lxml')
                section = response_soup.find('div', class_=name_of_main_section_class)
                blocks = section.find_all('div', class_=name_of_blocks_class)
            except AttributeError:
                print(f'Lost page - {ind_page}, need to check tag names.\n If the program skip ALL the PAGES try '
                      f'contacting support\n')     # in case of failure
                continue
        else:
            blocks = section.find_all('div', class_=name_of_blocks_class)

        for tag in blocks:  # for every block with ADS on page
            dict_buff['<id>'] = id_car + 1
            dict_buff['<model>'] = extract_data(tag, 'h3', 'css-16kqa8y efwtv890')
            dict_buff['<equipment>'] = extract_data(tag, 'div', 'css-1hd50jd e3f4v4l0')
            dict_buff['<description>'] = extract_data(tag, 'div', 'css-1fe6w6s e162wx9x0')
            dict_buff['<price>'] = int(extract_data(tag, 'span', 'css-46itwz e162wx9x0').replace('\xa0', '').
                                       replace('₽', ''))
            dict_buff['<location>'] = extract_data(tag, 'span', 'css-1488ad e162wx9x0').replace('≈ ', ''). \
                replace('→', '=>')
            dict_buff['<link>'] = ''

            try:
                link_tag = tag.find('a', 'g6gv8w4 g6gv8w8 _1ioeqy90')
                dict_buff['<link>'] = link_tag.get('href')
            except AttributeError:
                dict_buff['<link>'] = None

            if dict_buff['<model>']:
                id_car += 1
                list_cars.append(dict_buff.copy())

        dict_buff.clear()   # clear the dictionary

    session.close()
    print(f'Amount of active ads: {len(list_cars)}')
    recording_in_csv(list_cars)
    print('Done.')
    return


def main() -> None:
    # paste the link with the selected model and region
    input_url: str = "https://simferopol.drom.ru/volkswagen/golf/?distance=1000"
    parse_site(input_url)
    return


if __name__ == '__main__':
    main()
