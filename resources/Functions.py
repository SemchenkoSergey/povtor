# coding: utf8

import datetime
import os
from resources import Settings

def get_speed(phone_number, cursor):
    command = '''
    SELECT MIN(dd.max_up_rate), MIN(dd.max_dw_rate)
    FROM abon_dsl ad INNER JOIN data_dsl dd
	ON ad.hostname=dd.hostname AND ad.board=dd.board AND ad.port=dd.port
    WHERE dd.datetime >= DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY) AND ad.phone_number = '{}'    
    '''.format(phone_number)
    cursor.execute(command)
    result = cursor.fetchall()
    return {'up_rate' : result[0][0],
            'dw_rate' : result[0][1]}
        

def get_sessions(account_name, cursor):
    command = '''
    SELECT count
    FROM data_sessions
    WHERE date = DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY) AND account_name = '{}'
    '''.format(account_name)
    cursor.execute(command)
    result = cursor.fetchall()
    if len(result) == 0:
        return False
    else:
        return result[0][0]

def get_tariff_tv(account_name, cursor):
    command = '''
    SELECT tariff, tv
    FROM abon_dsl
    WHERE account_name = '{}'
    '''.format(account_name)
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
    day = datetime.date.today() - datetime.timedelta(days=1)
    with open('Файлы{}Заявки.txt'.format(os.sep), 'r') as f:
        for line in f:
            if '#' in line:
                continue
            try:
                phone_number, account_name = line.split(':')
            except:
                continue
            phone_number = phone_number.strip()
            account_name = account_name.strip()
            if len(phone_number) == 5:
                phone_number = '86547' + phone_number
            result.append({'phone_number' : phone_number, 'account_name' : account_name, 'date' : day})
    with open('Файлы{}Заявки.txt'.format(os.sep), 'w') as f:
        f.write('# Номер_телефона : учетное_имя\n\n')
    return result