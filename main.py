from bs4 import BeautifulSoup
from selenium import webdriver
import utils
import pandas as pd
import logging
import re

kcalmar = 'https://kcalmar.com/accounts/dietitian/login/'
patient_group = ''
login = ''
password = ''

driver = webdriver.Chrome()
driver.get(kcalmar)
driver.find_element_by_id('id_username').send_keys(login)
driver.find_element_by_id('id_password').send_keys(password)
driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/form/p[2]/button').click()

driver.get(patient_group)

menus = BeautifulSoup(driver.page_source, 'html.parser').find_all('div', {'class': 'col s12 m6 l3'})
patients = utils.create_patients_dict(menus)

count = 0
patients_result = {}
for pat, res in patients.items():
    if count == 3:
        break
    for x, link in res.items():
        print(f'Patient: {pat} -> menu: {x}')
        driver.get(link)
        soup_temp = BeautifulSoup(driver.page_source, 'html.parser')
        if soup_temp.find('td', {'class': 'day-1'}).find('div', {'class': 'dishes-ingredients'}).text == '':
            driver.get(link + '1')
            soup = BeautifulSoup(driver.page_source, 'html.parser')
        else:
            driver.get(link + '0')
            soup = BeautifulSoup(driver.page_source, 'html.parser')

        print(f'Finding microelements for {pat}...')
        microelements = utils.find_microelements(soup)

        print(f'')
        info = dict()
        patient_menus = dict()

        for micro in microelements:
            for m in micro.find_all("td"):
                divs = m.find_all("div")
                info[f'{divs[0].text.strip()} ({x})'] = divs[1].text

        if pat in patients_result.keys():
            patients_result[pat][x] = info
        else:
            patient_menus[x] = info 
            patients_result[pat] = patient_menus
        
    try:
        patients_result[pat]['Full'] = {}
        for d in (patients_result[pat]['I'], patients_result[pat]['II']): patients_result[pat]['Full'].update(d)
    except KeyError as e:
        print(e)
        patients_result[pat]['Full'] = patients_result[pat]['I']

        patients_result[pat]['Full'] = utils.create_additional_stats(patients_result[pat]['Full'])
    count = count + 1
    
menus_df = utils.prepare_csv(patients_result)
