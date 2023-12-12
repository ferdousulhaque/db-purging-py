import datetime
import pymysql
import time
import configparser

# Configs Read from config.ini file
config = configparser.ConfigParser()
config.read_file(open(r'config.ini'))
database_ip = int(config.get('database', 'ip'))
database_port = int(config.get('database', 'port'))
database_name = config.get('database', 'name')
database_user = config.get('database', 'user')
database_password = config.get('database', 'pass')
main_table_name = config.get('main_table', 'table_name')
main_table_time_field_name = config.get('main_table', 'table_time_field_name')
main_table_order_by = config.get('main_table', 'table_order_by')
main_table_purge_chunk = config.get('main_table', 'table_purge_chunk')
main_table_select_before_minutes = config.get('main_table', 'table_before_minutes')
backup_table_name = config.get('backup_table', 'table_name')
backup_table_purge_chunk = config.get('backup_table', 'table_purge_chunk')
backup_table_purge_days = config.get('backup_table', 'table_purge_days')
backup_table_time_field_name = config.get('backup_table', 'table_time_field_name')
backup_table_order_by = config.get('backup_table', 'table_order_by')

MYSQL_DB = {
    'host': database_ip,
    'port': database_port,
    'db': database_name,
    'user': database_user,
    'passwd': database_password
}


def get_Connection() -> pymysql.Connection:
    db = pymysql.connect(**MYSQL_DB)
    return db


def purge_table() -> None:
    db = get_Connection()
    cursor = db.cursor()

    print('Starting Purging Script')
    sql = '''SET SQL_SAFE_UPDATES = 0'''
    cursor.execute(sql)
    db.commit()

    # Select and Insert to Backup
    query_start = time.time()
    sql = f'''insert into {backup_table_name} SELECT * FROM {main_table_name}
    where {main_table_time_field_name} < date_sub(now(), interval {main_table_select_before_minutes} minute) 
    order by {main_table_order_by} asc limit {main_table_purge_chunk}; '''
    cursor.execute(sql)
    db.commit()
    query_end = time.time()
    select_insert_time = query_end - query_start
    print("Select Insert Time: {}".format(select_insert_time))

    # Select and Delete from Main Table
    query_start = time.time()
    sql = f'''delete from {main_table_name} where {main_table_order_by} in 
    (SELECT * FROM (SELECT {main_table_order_by} FROM {main_table_name} 
    where {main_table_time_field_name} < date_sub(now(), interval {main_table_select_before_minutes} minute) 
    order by {main_table_order_by} asc limit {main_table_purge_chunk}) as t);'''
    cursor.execute(sql)
    db.commit()
    query_end = time.time()
    select_delete_time = query_end - query_start
    print("Select Delete Time: {}".format(select_delete_time))

    # Purge from Backup Table
    query_start = time.time()
    sql = f'''delete from {backup_table_name} where {backup_table_time_field_name} < date_sub(now(), 
    interval {backup_table_purge_days} day)
    order by otp_id asc limit {backup_table_purge_chunk};'''
    cursor.execute(sql)
    db.commit()
    query_end = time.time()
    purge_backup_time = query_end - query_start
    print("Purge from Backup Time: {}".format(purge_backup_time))

    sql = '''SET SQL_SAFE_UPDATES = 1'''
    cursor.execute(sql)
    db.commit()
    db.close()
    print('Completing Purging Script')


try:
    purge_table()
except Exception as e:
    print(str(e))
