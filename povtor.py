# coding: utf8

import openpyxl
import datetime
import os
import MySQLdb
from resources import Settings
from resources import Functions as F

connect = MySQLdb.connect(host=Settings.db_host, user=Settings.db_user, password=Settings.db_password, db=Settings.db_name, charset='utf8')
cursor = connect.cursor()

abonents = F.read_input_file()
phone_numbers = []
for abonent in abonents:
    phone_numbers.append(abonent['phone_number'])

try:
    wb = openpyxl.load_workbook('Файлы{}Отчет.xlsx'.format(os.sep))
except:
    pass
else:
    sh = wb.get_active_sheet()
    for row in  range(5, sh.max_row + 1):
        try:
            phone_number = '86547' + sh['C' + str(row)].value
            account_name = sh['D' + str(row)].value
            date = datetime.datetime.strptime(sh['E' + str(row)].value,'%d-%m-%y').date()
        except:
            continue
        if phone_number not in phone_numbers:
            abonents.append({'phone_number' : phone_number, 'account_name' : account_name, 'date' : date})
            
wb = openpyxl.load_workbook('resources{}table.xlsx'.format(os.sep))
sh = wb.get_active_sheet()
sh['B2'].value = 'Отчет на {}'.format(datetime.date.today().strftime('%d-%m-%y'))
int_row = sh.max_row + 1
idx = 1

for abonent in abonents:
    delta = Settings.period - (datetime.date.today() - abonent['date']).days
    if delta < 0:
        continue
    row = str(int_row)
    speed = F.get_speed(abonent['phone_number'], cursor)
    tariff_tv = F.get_tariff_tv(abonent['account_name'], cursor)
    sessions =  F.get_sessions(abonent['account_name'], cursor)
    sh['B' + row].value = idx
    sh['C' + row].value = abonent['phone_number'][5:]
    sh['D' + row].value = abonent['account_name']
    sh['E' + row].value = abonent['date'].strftime('%d-%m-%y')
    sh['F' + row].value = delta
    sh['G' + row].value = speed['up_rate'] if speed['up_rate'] is not None else '-'
    sh['H' + row].value = speed['dw_rate'] if speed['dw_rate'] is not None else '-'
    sh['I' + row].value = sessions if sessions is not False else '-'
    sh['J' + row].value = tariff_tv['tariff']
    sh['K' + row].value = tariff_tv['tv']
    idx += 1
    int_row += 1
wb.save('Файлы{}Отчет.xlsx'.format(os.sep))
connect.close()