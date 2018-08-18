# coding: utf-8

import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from resources import Settings
#import Settings
#import warnings
#warnings.filterwarnings("ignore")

class Incident():    
    def __init__(self, url, service, date, phone):
        self.url = 'https://argus.south.rt.ru' + url if url != '' else ''
        self.service = service
        self.date = self.modify_date(date)
        self.phone = phone
    
    def modify_date(self, date):
        
        date_split = date.split()[0]
        return datetime.datetime.strptime(date_split, '%d.%m.%Y').date()
    
    def __str__(self):
        return 'Услуга: {}\nТелефон: {}\nДата: {}\nURL: {}\n'.format(self.service, self.phone, self.date.strftime('%d.%m.%Y'), self.url)
    
    def __gt__(self, other):
        return self.date > other.date
    
    def __lt__(self, other):
        return self.date < other.date    



def get_browser():
    while True:
        try:
            browser = webdriver.Chrome()
            #browser = webdriver.PhantomJS(executable_path='/home/inet/GIT/povtor/phantomjs')
        except Exception as ex:
            print(ex)
            time.sleep(120)
            continue
        else:
            return browser
        
def open_argus():
    browser = get_browser() 
    while True:
        try:
            browser.get('https://argus.south.rt.ru/argus/')
            xpath = '//*[@id="login_form-username"]'
            if wait_pages(browser, xpath):
                browser.find_element(By.XPATH, xpath).send_keys(Settings.ARGUS_LOGIN)
            xpath = '//*[@id="login_form-password"]'
            if wait_pages(browser, xpath):
                browser.find_element(By.XPATH, xpath).send_keys(Settings.ARGUS_PASSWORD)
            click_element(browser, '//*[@id="login_form-submit"]/span')
            wait_pages(browser, '//*[@id="mmf-main_menu_bar"]/ul/li[2]/ul/li[3]/a/span')
            
        except:
            browser.quit()
            time.sleep(15)
            browser = get_browser()
        else:
            break
    return browser

def wait_pages(browser, xpath):
    WebDriverWait(browser, 120).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
    time.sleep(2)
    return True

def click_element(browser, xpath):
    if wait_pages(browser, xpath):
        browser.find_element(By.XPATH, xpath).click()


def get_claims_argus(browser,days):
    browser.get('https://argus.south.rt.ru/argus/views/supportservice/summary/TaskSummaryView.xhtml')
    try:    
        click_element(browser, '//*/span[@title="По участкам, о выполнении контрольных сроков"]')  
        click_element(browser, '//*/div[@class="ui-grid-col-4"]/div/div/div/div[2]/span')
            
        xpath = '//*/div[@class="ui-grid-col-4"]/div/div[3]/input'
        if wait_pages(browser, xpath):
            browser.find_element(By.XPATH, xpath).send_keys('\b{}'.format(days))
        
        click_element(browser, '//*/span[contains(text(),"Ставропольский филиал")]/../../span[1]')            
        click_element(browser, '//*/span[contains(text(),"Ставропольский край")]/../../span[1]')            
        click_element(browser, '//*/span[contains(text(),"{}")]/../../span[1]'.format(Settings.department))            
        click_element(browser, '//*/span[contains(text(),"{}")]/../../div/div/span'.format(Settings.area))            
        click_element(browser, '//*/span[text()="ОК"]')
        if wait_pages(browser, '//*[@id="pvt_flt_f-filter_panel"]'):
            try:
                click_element(browser, '//*/td[text()="3ЛТП.Выездной наряд"]/../td[2]')
            except:
                return []
        time.sleep(5)
        xpath = '//*/span[text()="по технологии ADSL"]/../../../td[3]/div/div/a'
        result = []
        if wait_pages(browser, xpath):
            elements = browser.find_elements(By.XPATH, xpath)
            for element in elements:
                url = element.get_attribute('href').replace('https://argus.south.rt.ru','')
                service_xpath = '//*/a[@href="{}"]/../../../../td[4]/div/span'.format(url)
                date_xpath = '//*/a[@href="{}"]/../../../../td[18]/div/span'.format(url)
                date = browser.find_element(By.XPATH, date_xpath).get_attribute('title')
                service = browser.find_element(By.XPATH, service_xpath).get_attribute('title')
                result.append(Incident(url=url, service=service, date=date, phone=''))
    except:
        return None
    else:
        return result

def get_phone_argus(browser, claim):
    try:
        browser.get(claim.url)
        click_element(browser, '//*/a[@id="installation_edit_form-installationService"]/span')
        xpath = '//*/tbody[@id="client_tabs-client_installations_form-client_installations_table_data"]/tr[1]/td[2]'
        if wait_pages(browser, xpath):
            claim.phone = browser.find_element(By.XPATH, xpath).text.replace('(', '').replace(')','')
    except:
        return None
    else:
        return True

    

#br = open_argus()
#time.sleep(5)
#claims = get_claim_argus(br, 2)
#for claim in claims:
    #get_phone_argus(br, claim)

#claims = sort_claims(claims)
#for claim in claims:
    #print(claim)
    
#br.quit()

