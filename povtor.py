#!/usr/bin/env python3
# coding: utf8

import openpyxl
import datetime
import time
import os
import MySQLdb
from resources import Settings
from resources import Argus
from resources import Functions as F
import warnings
warnings.filterwarnings("ignore")

def main():
    #run_date = datetime.datetime.now().date() # Запуск завтра
    run_date = datetime.datetime.now().date() - datetime.timedelta(days=1) # Запуск сейчас
    
    while True:
        current_date = datetime.datetime.now().date()
        if (current_date != run_date) and (datetime.datetime.now().hour >= 6):
            print('Начало работы: {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            incidents = F.read_report_file()
            if len(incidents) == 0:
                delta = Settings.period
            else:
                delta = (datetime.datetime.now().date() - incidents[0].date).days + 1
            browser = Argus.open_argus()
            while True:
                claims = Argus.get_claims_argus(browser, delta)
                if claims is not None:
                    break
                browser.quit()
                time.sleep(60)
                browser = Argus.open_argus()   
            for claim in claims:
                while True:
                    if Argus.get_phone_argus(browser, claim) is True:
                        incidents.append(claim)
                        break
            browser.quit()
            
            incidents += F.read_input_file()
            incidents = F.sort_claims(incidents)
               
            connect = MySQLdb.connect(host=Settings.db_host, user=Settings.db_user, password=Settings.db_password, db=Settings.db_name, charset='utf8')
            cursor = connect.cursor()
            
            wb = openpyxl.load_workbook('resources{}table.xlsx'.format(os.sep))
            sh = wb.active
            sh['B2'].value = 'Отчет на {}'.format(datetime.date.today().strftime('%d.%m.%Y'))
            int_row = sh.max_row + 1
            idx = 1
            
            use_phones = []
            for incident in incidents:
                if incident.phone in use_phones:
                    continue
                delta = Settings.period - (datetime.datetime.now().date() - incident.date).days
                if delta < 0:
                    continue
                row = str(int_row)
                speed = F.get_speed(incident.phone, cursor)
                tariff_tv = F.get_tariff_tv(incident.phone, cursor)
                sessions =  F.get_sessions(incident.phone, cursor)
                address = F.get_address(incident.phone, cursor)
                sh['B{}'.format(row)].value = idx
                sh['C{}'.format(row)].value = incident.phone.replace(Settings.phone_code, '')
                sh['D{}'.format(row)].value = address
                sh['E{}'.format(row)].value = incident.date.strftime('%d.%m.%Y')
                sh['F{}'.format(row)].value = delta
                sh['G{}'.format(row)].value = speed['up_rate'] if speed['up_rate'] is not None else '-'
                sh['H{}'.format(row)].value = speed['dw_rate'] if speed['dw_rate'] is not None else '-'
                sh['I{}'.format(row)].value = sessions if sessions is not False else '-'
                sh['J{}'.format(row)].value = tariff_tv['tariff']
                sh['K{}'.format(row)].value = tariff_tv['tv']
                idx += 1
                int_row += 1
                use_phones.append(incident.phone)
            wb.save('Файлы{}Отчет закрытые ADSL.xlsx'.format(os.sep))
            connect.close()
            run_date = current_date
            print('Завершение работы: {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            print('---------\n')            
        else:
            time.sleep(60*20)
            continue            


if __name__ == '__main__':
    cur_dir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
    os.chdir(cur_dir)
    main()