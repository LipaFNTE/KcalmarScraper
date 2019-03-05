from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import re


def find_microelements(soup: BeautifulSoup):
    """
    Find all microelements for certain patient (menu) using BeautifulSoup
    object. Method returns list of 'tr' objects consists of all microelements.
    :param soup:
    :return:
    """
    
    microelements = soup.find("div", {"class": "microelements"})
    micro_table = microelements.find("table")
    return micro_table.find_all("tr")


def create_patients_dict(menus: BeautifulSoup):
    """
    For given BeautifulSoup object with menus of all patients create a dict
    with good structure for further analysis.
    """
    patients = {}
    for menu in menus:
        if menu.find('p', {'class': 'name'}).text == 'Powrót do katalogu głównego':
            continue
        patient_info = menu.find("a")
        menu_link = 'https://kcalmar.com' + patient_info.get('href')
        patient_name_info = patient_info.find('p').text.split()
        patient_name = patient_name_info[0] + ' ' + patient_name_info[1]
        patient_menu = patient_name_info[2]
        patient_dict = {patient_menu: menu_link}
        if patient_name in patients.keys():
            patients[patient_name][patient_menu] = menu_link
        else:
            patients[patient_name] = patient_dict

    return patients


def prepare_csv(results: dict):
    """
    Convert prepared data into csv file, readable and possible to analyze.
    :param results:
    :return: DataFrame
    """
    final_menus = {}
    for pat, menus in results.items():
        final_menus[pat] = menus['Full']

    menus_table = pd.DataFrame.from_dict(final_menus, orient='index')
    menus_table.columns = sorted(menus_table.columns)
    menus_table = refactor_menus_data(menus_table)

    menus_table.to_csv('Menus.csv')
    return menus_table


def refactor_menus_data(menus: pd.DataFrame):
    """

    :param menus:
    :return:
    """
    new_columns = []
    first_index = menus.index[0]
    for col in menus.columns:
        x = re.search(r'(μ[a-z]+)|[a-z][A-Z]+|[a-z]+|%', menus.loc[first_index, col])
        if x is not None:
            new_columns.append(col + f' ({x.group(0)})')
            menus[col] = menus[col].apply(lambda value: value.replace(x.group(0), ''))
        else:
            new_columns.append(col)

    menus.columns = new_columns
    return menus


def create_additional_stats(df: dict):
    """

    :param df:
    :return:
    """
    col_list_1 = ['Białko ogółem wg rozp. 1169/2011 (I)', 'Węglowodany ogółem (I)',
                  'Kwasy tłuszczowe jednonienasycone ogółem (I)', 'Kwasy tłuszczowe nasycone ogółem (I)',
                  'Kwasy tłuszczowe wielonienasycone ogółem (I)']
    col_list_2 = [x.replace('(I)', '(II)') for x in col_list_1]

    value_1 = df[col_list_1[0]] + df[col_list_1[1]] + df[col_list_1[2]] + df[col_list_1[3]] + df[col_list_1[4]]
    value_2 = df[col_list_2[0]] + df[col_list_2[1]] + df[col_list_2[2]] + df[col_list_2[3]] + df[col_list_2[4]]

    df['Białko ogółem % (I)'], df['Białko ogółem % (II)'] = df[col_list_1[0]]/value_1, df[col_list_2[0]]/value_2
    df['Węglowodany ogółem % (I)'], df['Węglowodany ogółem % (II)'] = df[col_list_1[1]]/value_1, df[col_list_2[1]]/value_2
    df['Tłuszcz ogółem % (I)'] = (df[col_list_1[2]] + df[col_list_1[3]] + df[col_list_1[4]])/value_1
    df['Tłuszcz ogółem % (II)'] = (df[col_list_2[2]] + df[col_list_2[3]] + df[col_list_2[4]])/value_2

    return df


def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    print(e)
