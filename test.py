from bs4 import BeautifulSoup
from selenium import webdriver

kcalmar = 'https://kcalmar.com/accounts/dietitian/login/'

driver = webdriver.Chrome()
driver.get(kcalmar)
driver.find_element_by_id('id_username').send_keys("username")
driver.find_element_by_id('id_password').send_keys("password")
driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/form/p[2]/button').click()

driver.get('')
soup = BeautifulSoup(driver.page_source, 'html.parser')
microelements = soup.find("div", {"class": "microelements"})
micro_table = microelements.find("table")
m_table = micro_table.find_all("tr")

info = dict()
count = 0

for micro in m_table:
    for m in micro.find_all("td"):
        divs = m.find_all("div")
        info[divs[0].text.strip()] = divs[1].text
        count = count + 1
    