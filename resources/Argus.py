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
        except:
            time.sleep(120)
            continue
        else:
            return browser
        
def open_argus():
    browser = get_browser() 
    while True:
        try:
            browser.get('https://argus.south.rt.ru/argus/')
            element = browser.find_element_by_id("login_form-username")
            element.send_keys(Settings.ARGUS_LOGIN)
            element = browser.find_element_by_id("login_form-password")
            element.send_keys(Settings.ARGUS_PASSWORD)
            element = browser.find_element_by_id("login_form-submit")
            element.click()
        except:
            browser.quit()
            time.sleep(15)
            browser = get_browser()
        else:
            break
    return browser

def wait_pages(browser, xpath):
    WebDriverWait(browser, 300).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
    time.sleep(2)
    return True
    #try:
        #WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        #time.sleep(2)
    #except:
        #return False
    #else:
        #return True

def click_element(browser, xpath):
    if wait_pages(browser, xpath):
        browser.find_element(By.XPATH, xpath).click()


def get_claims_argus(browser,days):
    browser.get('https://argus.south.rt.ru/argus/views/supportservice/summary/TaskSummaryView.xhtml')
    try:    
        click_element(browser, '//*/span[@title="По участкам, о выполнении контрольных сроков"]')
        #xpath = '//*/span[@title="По участкам, о выполнении контрольных сроков"]'
        #if wait_pages(browser, xpath):
            #browser.find_element(By.XPATH, xpath).click()
        
        click_element(browser, '//*/div[@class="ui-grid-col-4"]/div/div/div/div[2]/span')
        #xpath = '//*/div[@class="ui-grid-col-4"]/div/div/div/div[2]/span'
        #if wait_pages(browser, xpath):
            #browser.find_element(By.XPATH, xpath).click()
            
        xpath = '//*/div[@class="ui-grid-col-4"]/div/div[3]/input'
        if wait_pages(browser, xpath):
            browser.find_element(By.XPATH, xpath).send_keys('\b{}'.format(days))
        
        click_element(browser, '//*/span[contains(text(),"Ставропольский филиал")]/../../span[1]')
        #xpath = '//*/span[contains(text(),"Ставропольский филиал")]/../../span[1]'
        #if wait_pages(browser, xpath):
            #browser.find_element(By.XPATH, xpath).click()
            
        click_element(browser, '//*/span[contains(text(),"Ставропольский край")]/../../span[1]')
        #xpath = '//*/span[contains(text(),"Ставропольский край")]/../../span[1]'
        #if wait_pages(browser, xpath):
            #browser.find_element(By.XPATH, xpath).click()
            
        click_element(browser, '//*/span[contains(text(),"{}")]/../../span[1]'.format(Settings.department))
        #xpath = '//*/span[contains(text(),"{}")]/../../span[1]'.format(Settings.department)
        #if wait_pages(browser, xpath):
            #browser.find_element(By.XPATH, xpath).click()
            
        click_element(browser, '//*/span[contains(text(),"{}")]/../../div/div/span'.format(Settings.area))
        #xpath = '//*/span[contains(text(),"{}")]/../../div/div/span'.format(Settings.area)
        #if wait_pages(browser, xpath):
            #browser.find_element(By.XPATH, xpath).click()
            
        click_element(browser, '//*/span[text()="ОК"]')
        #xpath = '//*/span[text()="ОК"]'
        #if wait_pages(browser, xpath):
            #browser.find_element(By.XPATH, xpath).click()
            
        click_element(browser, '//*/td[text()="3ЛТП.Выездной наряд"]/../td[2]')
        #xpath = '//*/td[text()="3ЛТП.Выездной наряд"]/../td[2]'
        #if wait_pages(browser, xpath):
            #browser.find_element(By.XPATH, xpath).click()
            
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
        return result
    except:
        return None

def get_phone_argus(browser, claim):
    browser.get(claim.url)
    
    click_element(browser, '//*/a[@id="installation_edit_form-installationService"]/span')
    #xpath = '//*/a[@id="installation_edit_form-installationService"]/span'
    #if wait_pages(browser, xpath):
        #browser.find_element(By.XPATH, xpath).click()
    xpath = '//*/tbody[@id="client_tabs-client_installations_form-client_installations_table_data"]/tr[1]/td[2]'
    if wait_pages(browser, xpath):
        claim.phone = browser.find_element(By.XPATH, xpath).text.replace('(', '').replace(')','')
    

    

#br = open_argus()
#time.sleep(5)
#claims = get_claim_argus(br, 2)
#for claim in claims:
    #get_phone_argus(br, claim)

#claims = sort_claims(claims)
#for claim in claims:
    #print(claim)
    
#br.quit()

