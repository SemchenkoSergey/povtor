# coding: utf8

import datetime
import openpyxl
import os
from resources import Settings
from resources import Argus

def get_address(phone_number, cursor):
    command = '''
    SELECT
     locality,
     street,
     house_number,
     apartment_number
    FROM abon_dsl
    WHERE phone_number = "{}"
    '''.format(phone_number)
    cursor.execute(command)
    result = cursor.fetchone()
    if result is None:
        return '-'
    address = [s for s in result if s is not None]
    return ', '.join(address)


def get_speed(phone_number, cursor):
    command = '''
    SELECT ROUND(AVG(dd.max_up_rate)), ROUND(AVG(dd.max_dw_rate))
    FROM abon_dsl ad INNER JOIN data_dsl dd
	ON ad.hostname=dd.hostname AND ad.board=dd.board AND ad.port=dd.port
    WHERE CAST(dd.datetime AS DATE) = DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY) AND ad.phone_number = '{}'    
    '''.format(phone_number)
    cursor.execute(command)
    result = cursor.fetchall()
    return {'up_rate' : result[0][0],
            'dw_rate' : result[0][1]}
        

def get_sessions(phone_number, cursor):
    command = '''
    SELECT count
    FROM data_sessions
    WHERE date = DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY) AND account_name = (
     SELECT account_name
     FROM abon_dsl
     WHERE phone_number = '{}')
    '''.format(phone_number)
    cursor.execute(command)
    result = cursor.fetchall()
    if len(result) == 0:
        return False
    else:
        return result[0][0]

def get_tariff_tv(phone_number, cursor):
    command = '''
    SELECT tariff, tv
    FROM abon_dsl
    WHERE phone_number = '{}'
    '''.format(phone_number)
    cursor.execute(command)
    result = cursor.fetchall()
    if len(result) == 0:
        return {'tariff' : '-',
                'tv' : '-'}
    else:
        return {'tariff' : result[0][0],
                'tv' : 'Да' if result[0][1] == 'yes' else 'Нет'}

def read_input_file():
    result = []
    date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
    with open('Файлы{}Заявки.txt'.format(os.sep), 'r') as f:
        for line in f:
            if '#' in line:
                continue
            phone = line.strip()
            if len(phone) == 0:
                continue
            if len(phone) != 10:
                phone = Settings.phone_code + phone
            result.append(Argus.Incident(url='', service='', date=date, phone=phone))
    with open('Файлы{}Заявки.txt'.format(os.sep), 'w') as f:
        f.write('# Номер_телефона\n\n')
    return result

def read_report_file():
    result = []
    try:
        wb = openpyxl.load_workbook('Файлы{}Отчет закрытые ADSL.xlsx'.format(os.sep))
    except Exception as ex:
        #print(ex)
        pass
    else:
        sh = wb.active
        for row in  range(5, sh.max_row + 1):
            phone = Settings.phone_code + sh['C{}'.format(row)].value
            date = sh['E{}'.format(row)].value
            result.append(Argus.Incident(url='', service='', date=date, phone=phone))
    return result
    
def sort_claims(claims):
    results = []
    for i, claim in enumerate(claims):
        if i == 0:
            results.append(claim)
            continue
        for y, result in enumerate(results):
            if claim < result:
                results.insert(y, claim)
                break
            if y == len(results) - 1:
                results.append(claim)
                break
    return results[::-1]