##################
### загрузчик SZVTD для Новиковой , в планировщике не стоит, sql запросов нет .
####################
import os
import sys
import shutil
from datetime import date, datetime, timedelta
import fnmatch
import psutil
import logging
import configparser
import pandas as pd
import re
os.add_dll_directory(r'c:\Python\Lib\site-packages\clidriver\bin')

import ibm_db
import ibm_db_dbi as db
import csv
import glob



# Создаем объект ConfigParser
config = configparser.ConfigParser()
# Читаем файл конфигурации
config.read('config.ini')

# Конфигурация логгера
logs_file = config['SZVTD_logging']['logs_file']
logging.basicConfig(filename=logs_file, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
def GetRecordasOld(sqlStmt,ibm_db_conn ,*args):
    preparedStmtUpd = None
    returnCode =False
    try:
        preparedStmtUpd = ibm_db.prepare(ibm_db_conn, sqlStmt)
    except Exception:
        message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - ERROR: Unable to prepare the  SQL statement specified."
        logging.info(message)
        print(message)
        input("Нажмите Enter, чтобы выйти...")
        pass
    if preparedStmtUpd is False:
        conn.close()
        exit(-1)
    if len(args) > 0:
        i = 1
        for arg in args:
            try:
                returnCode = ibm_db.bind_param(preparedStmtUpd, i, arg)
            except Exception:
                pass
            i = i + 1
            # If The Application Variable Was Not Bound Successfully, Display An Error Message And Exit
            if returnCode is False:
                message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - Unable to bind the variable to the parameter marker  record exist specified.row N "
                logging.info(message)
                print(message)
                input("Нажмите Enter, чтобы выйти...")

                conn.close()
                exit(-1)

    try:
        # for debug only!!!!!!!!!!!!!!!
        #returnCode=True
        #pass
        returnCode = ibm_db.execute(preparedStmtUpd)

    except Exception:
        message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - ERROR: Unable to execute the SQL update statement."

        print(message)
        input("Нажмите Enter, чтобы выйти...")

        pass
    # If The SQL Statement Could Not Be Executed, Display An Error Message And Exit
    if returnCode is False:
        message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - ERROR: Unable to execute the SQL update statement."
        logging.info(message)
        print(message)
        input("Нажмите Enter, чтобы выйти...")
        conn.close()
        exit(-1)
    # # Otherwise, Complete The Status Message
    else:
        return True


def connDb1():
    # connect  to db
    database_username = 'DB2ADMIN'
    database_password = 'gfhfljrc9'
    database_hostname = '10.2.0.20'
    database_port = '50000'
    database_name = 'OPFR002'
    # Construct the connection string
    connection_string = (
            f"DATABASE={database_name};"
            f"HOSTNAME={database_hostname};"
            f"PORT={database_port};"
            f"PROTOCOL=TCPIP;"
            f"UID={database_username};"
            f"PWD={database_password};"
        )
    # Establish the connection to database
    try:
        ibm_db_conn = ibm_db.connect(connection_string, '', '')
        conn = db.Connection(ibm_db_conn)
    except Exception:
        pass
    # If A Db2 Database Connection Could Not Be Established, Display An Error Message And Exit
    if conn is None:
        message = f"{datetime.now()} - A Db2 Database Connection Could Not Be Established"

        logging.info(message)
        print(message)
        input("Нажмите Enter, чтобы выйти...")
        exit(-1)
    return conn, ibm_db_conn  # Otherwise, Complete The Status Message

def isRecordNewCheck(sqlStmt,ibm_db_conn,*args):
    preparedStmtCheck = None
    returnCode = False
    dataRecord = False

    try:
        preparedStmtCheck = ibm_db.prepare(ibm_db_conn, sqlStmt)
    except Exception:
        message = f"{datetime.now()} -{ibm_db.stmt_errormsg() } - check transaction couldn't be completed"
        logging.info(message)
        print(ibm_db.stmt_errormsg())
        input("Нажмите Enter, чтобы выйти...")

        pass
    if preparedStmtCheck is False:
        conn.close()
        exit(-1)
    if len(args) > 0:
        i = 1
        for arg in args:
            try:
                returnCode = ibm_db.bind_param(preparedStmtCheck, i, arg)

            except Exception:
            # If The Application Variable Was Not Bound Successfully, Display An Error Message And Exit
                pass
            i = i + 1
            if returnCode is False:
                message = f"{datetime.now()} -{ibm_db.stmt_errormsg()} - Unable to bind the variable to the parameter marker specified."
                logging.info(message)
                print(ibm_db.stmt_errormsg())
                input("Нажмите Enter, чтобы выйти...")

                conn.close()
                exit(-1)
    try:
        returnCode = ibm_db.execute(preparedStmtCheck)
    except Exception:
        pass
    # If The SQL Statement Could Not Be Executed, Display An Error Message And Exit
    if returnCode is False:
        message = f"{datetime.now()} -{ibm_db.stmt_errormsg()} - Unable to execute the SQL check  statement."
        logging.info(message)
        print(ibm_db.stmt_errormsg())
        input("Нажмите Enter, чтобы выйти...")

        conn.close()
        exit(-1)
    # Otherwise, Complete The Status Message
    dataRecord = False
    rows = 0
    try:
        dataRecord = ibm_db.fetch_tuple(preparedStmtCheck)
    except:
        message = f"{datetime.now()} -{ibm_db.stmt_errormsg()} - Unable fetch tuple stmt."
        logging.info(message)
        print(ibm_db.stmt_errormsg())
        input("Нажмите Enter, чтобы выйти...")

        pass
    if dataRecord is False:
        rows = 0
    else:
        rows = 1
    return rows


def is_remote_path_mounted(path):
    for part in psutil.disk_partitions(all=False):
        if path.lower().startswith(part.mountpoint.lower()):
            return True
    return False

def check_network_drive_access(network_path):
    if os.path.exists(network_path):
        return True
    elif os.path.isdir(network_path):
        return True
    else:
        return False

#def  sqlUpdate_after(sqlStmt,ibm_db_conn, *args)



def SqlStmt(sqlStmt,ibm_db_conn, *args):
    preparedStmt = None
    returnCode = False
    try:
        preparedStmt = ibm_db.prepare(ibm_db_conn, sqlStmt)
    except Exception:
        message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - Transaction stmt couldn't be completed, row N"
        logging.info(message)
        print(ibm_db.stmt_errormsg())
        input("Нажмите Enter, чтобы выйти...")

        pass
    if preparedStmt is False:
        conn.close()
        exit(-1)
    i=1
    for arg in args:
        try:
            returnCode = ibm_db.bind_param(preparedStmt, i, arg)
        except Exception:
            pass
        i=i+1
    # If The Application Variable Was Not Bound Successfully, Display An Error Message And Exit
    if returnCode is False:
        message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - ERROR: Unable to bind the variable to the parameter marker  record exist specified.row N "
        logging.info(message)
        print(ibm_db.stmt_errormsg())
        input("Нажмите Enter, чтобы выйти...")

        conn.close()
        exit(-1)
        # Execute The Prepared SQL Statement (Using The New Parameter Marker Value)
    try:
        #for debug only!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #returnCode=True

        returnCode = ibm_db.execute(preparedStmt)
    except Exception:
        message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - ERROR: Unable to execute the SQL statement, row N"
        logging.info(message)
        print(ibm_db.stmt_errormsg())
        input("Нажмите Enter, чтобы выйти...")
        pass
        # If The SQL Statement Could Not Be Executed, Display An Error Message And Exit
    if returnCode is False:
        message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - ERROR: Unable to execute the SQL statement"
        logging.info(message)
        print(ibm_db.stmt_errormsg())
        input("Нажмите Enter, чтобы выйти...")

        conn.close()
        exit(-1)
        # Otherwise, Complete The Status Message
    else:
        return True
        # ShowMessage('not exisct, new record!');
def ProcessFile(src_file,fl_dop,logs_file,dat_load ):
    conn, ibm_db_conn = connDb1()
    if conn:
        sqlStmtUpd = None
        sqlStmtCheck = None
        sqlStatement = None
        dat_load = datetime.strptime(dat_load, "%Y_%m_%d")

        load = 0
        notload = 0
        j = 0

        load_dop = 0
        notload_dop = 0
        j_dop = 0

        message = f"{datetime.now()} - {src_file} - start "
        logging.info(message)
        print(message)
        col_names = ["NN", "DST", "ENTNMB", "ZL_UNIC", "ZL_UNIC_POSLE", "KM_ALL_POSLE", "KM_PRIEM_POSLE", "KM_UV_POSLE",
                     "KM_OTH_POSLE", "ZL_TD_ALL", "ZL_TD_PAPER", "ZL_TD_PROC", "ZL_TD_EL_ALL",
                     "ZL_TD_POSLE", "ZL_TD_EL_PROC", "ENT_PERV", "ZL_PERV"]

        #########################################################################################################
        #грузим  новеньких
        if fl_dop==1:
            with open(src_file, 'r') as input_file:
                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                sqlStmtUpd = 'update DB2ADMIN.PU_SZVTD_NEW set newrec=0'

                # // Отметим  все звписи  как старые
                if not GetRecordasOld(sqlStmtUpd,ibm_db_conn):
                    return

                returnCode = False
                fields = []
                fields = next(csvFile)
                for row in csvFile:
                    j = j + 1
                    entnmb = row["ENTNMB"]
                    zl_unic = row['ZL_UNIC']
                    zl_unic_posle = row['ZL_UNIC_POSLE']

                    km_all_posle = row["KM_ALL_POSLE"]
                    km_priem_posle = row['KM_PRIEM_POSLE']
                    km_uv_posle = row['KM_UV_POSLE']
                    km_oth_posle = row['KM_OTH_POSLE']
                    zl_td_all = row['ZL_TD_ALL']

                    zl_td_paper = row['ZL_TD_PAPER']
                    zl_td_proc = row['ZL_TD_PROC']
                    zl_td_el_all = row['ZL_TD_EL_ALL']

                    zl_td_posle = row['ZL_TD_POSLE']
                    zl_td_el_proc = row['ZL_TD_EL_PROC']
                    ent_perv = row['ENT_PERV']
                    zl_perv = row['ZL_PERV']
                    # // Проверка
                    #sqlStmtCheck = ('SELECT * FROM DB2ADMIN.PU_SZVTD_NEW WHERE  ENTNMB=? and ZL_UNIC=? and ZL_UNIC_POSLE=? and KM_ALL_POSLE=? and KM_PRIEM_POSLE=? and KM_UV_POSLE=? and KM_OTH_POSLE=? and ZL_TD_ALL=? and ZL_TD_PAPER=? and ZL_TD_PROC=? and ZL_TD_EL_ALL=? and ZL_TD_POSLE=? and ZL_TD_EL_PROC=? and ENT_PERV=? and ZL_PERV=?')
                    #rows = isRecordNewCheck(sqlStmtCheck, ibm_db_conn, entnmb, zl_unic, zl_unic_posle, km_all_posle, km_priem_posle, km_uv_posle, km_oth_posle, zl_td_all, zl_td_paper, zl_td_proc, zl_td_el_all,zl_td_posle, zl_td_el_proc,ent_perv, zl_perv)
                    sqlStmtCheck = ('SELECT * FROM DB2ADMIN.PU_SZVTD_NEW WHERE  ENTNMB=?')
                    rows = isRecordNewCheck(sqlStmtCheck, ibm_db_conn, entnmb)



                    # ##// 'Нашёл!!!!'
                    if rows > 0:
                        notload = notload + 1
                        returnCode = False
                        #sqlStatement = ('update DB2ADMIN.PU_SZVTD_NEW  set NEWREC=1 where ENTNMB=? and ZL_UNIC=? and ZL_UNIC_POSLE=? and KM_ALL_POSLE=? and KM_PRIEM_POSLE=? and KM_UV_POSLE=? and KM_OTH_POSLE=? and ZL_TD_ALL=? and ZL_TD_PAPER=? and ZL_TD_PROC=? and ZL_TD_EL_ALL=? and ZL_TD_POSLE=? and ZL_TD_EL_PROC=? and ENT_PERV=? and ZL_PERV=?')
                        sqlStatement = ('update DB2ADMIN.PU_SZVTD_NEW  set NEWREC=1, ZL_UNIC=?,ZL_UNIC_POSLE=?, KM_ALL_POSLE=?, KM_PRIEM_POSLE=?, KM_UV_POSLE=?, KM_OTH_POSLE=?, ZL_TD_ALL=? , ZL_TD_PAPER=?, ZL_TD_PROC=? , ZL_TD_EL_ALL=? , ZL_TD_POSLE=? , ZL_TD_EL_PROC=? , ENT_PERV=? ,ZL_PERV=?,DAT_LOAD=? where ENTNMB=?')

                        #if not SqlStmt(sqlStatement, ibm_db_conn,entnmb, zl_unic, zl_unic_posle, km_all_posle, km_priem_posle, km_uv_posle, km_oth_posle, zl_td_all, zl_td_paper, zl_td_proc, zl_td_el_all, zl_td_posle, zl_td_el_proc, ent_perv, zl_perv):
                        if not SqlStmt(sqlStatement, ibm_db_conn,  zl_unic, zl_unic_posle, km_all_posle, km_priem_posle, km_uv_posle, km_oth_posle, zl_td_all, zl_td_paper, zl_td_proc, zl_td_el_all, zl_td_posle, zl_td_el_proc, ent_perv, zl_perv,dat_load, entnmb):

                            message = f"{datetime.now()} - Can't run  sql stmt update, entnmb: {entnmb} - № row {j}"
                            logging.info(message)
                            return
                        else:
                            message = f"{datetime.now()} - запись существует, обновлена, entnmb: {entnmb}  - № row {j}"
                            logging.info(message)
                            print(message)

                    #####################################
                    # не нашел добавляем
                    if rows == 0:
                        load = load + 1
                        dptcod = int(entnmb) // 1_000_000

                        newrec = 1


                        sqlStatement = """INSERT INTO  DB2ADMIN.PU_SZVTD_NEW  (DPTCOD, ENTNMB, ZL_UNIC, ZL_UNIC_POSLE, KM_ALL_POSLE, KM_PRIEM_POSLE, KM_UV_POSLE,
                                    KM_OTH_POSLE, ZL_TD_ALL, ZL_TD_PAPER, ZL_TD_PROC, ZL_TD_EL_ALL,ZL_TD_POSLE, ZL_TD_EL_PROC, ENT_PERV, ZL_PERV,NEWREC,DAT_LOAD) 
                                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                        if not SqlStmt(sqlStatement,ibm_db_conn,  dptcod, entnmb, zl_unic, zl_unic_posle, km_all_posle, km_priem_posle, km_uv_posle,
                                    km_oth_posle, zl_td_all, zl_td_paper, zl_td_proc, zl_td_el_all,zl_td_posle, zl_td_el_proc, ent_perv, zl_perv,newrec, dat_load):
                            message = f"{datetime.now()} - Can't insert sql stmt, {entnmb}  - № row {j}"
                            logging.info(message)
                            return
                        else:
                            message = f"{datetime.now()} - добавлена новая запись   {entnmb} - - № row {j}"
                            logging.info(message)
                            print(message)

            message = f"{datetime.now()} - SZVTD новенькие, всего в списке: -  {j},   загружено: -  {load},  не загружено, запись существует: {notload} "
            logging.info(message)
            print(message)


        #########################################################################################################
        #грузим  ДОП
        else:
            with open(src_file, 'r') as input_file:
                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                sqlStmtUpd = 'update DB2ADMIN.PU_SZVTD_NEW set fl_dop=0'

                # // Отметим  все звписи  как старые
                if not GetRecordasOld(sqlStmtUpd, ibm_db_conn):
                    return

                returnCode = False
                fields = []
                fields = next(csvFile)
                for row in csvFile:
                    j_dop = j_dop + 1
                    entnmb = str(row["ENTNMB"])
                    zl_unic = str(row["ZL_UNIC"])
                    zl_unic = row['ZL_UNIC']
                    zl_unic_posle = row['ZL_UNIC_POSLE']

                    km_all_posle = row["KM_ALL_POSLE"]
                    km_priem_posle = row['KM_PRIEM_POSLE']
                    km_uv_posle = row['KM_UV_POSLE']
                    km_oth_posle = row['KM_OTH_POSLE']
                    zl_td_all = row['ZL_TD_ALL']

                    zl_td_paper = row['ZL_TD_PAPER']
                    zl_td_proc = row['ZL_TD_PROC']
                    zl_td_el_all = row['ZL_TD_EL_ALL']

                    zl_td_posle = row['ZL_TD_POSLE']
                    zl_td_el_proc = row['ZL_TD_EL_PROC']
                    ent_perv = row['ENT_PERV']
                    zl_perv = row['ZL_PERV']
                    # // Проверка
                    #sqlStmtCheck = ('SELECT * FROM DB2ADMIN.PU_SZVTD_NEW WHERE  ENTNMB=? and ZL_UNIC=? and ZL_UNIC_POSLE=? and KM_ALL_POSLE=? and KM_PRIEM_POSLE=? and KM_UV_POSLE=? and KM_OTH_POSLE=? and ZL_TD_ALL=? and ZL_TD_PAPER=? and ZL_TD_PROC=? and ZL_TD_EL_ALL=? and ZL_TD_POSLE=? and ZL_TD_EL_PROC=? and ENT_PERV=? and ZL_PERV=?')
                    #rows = isRecordNewCheck(sqlStmtCheck, ibm_db_conn, entnmb, zl_unic, zl_unic_posle, km_all_posle,
                    #                        km_priem_posle, km_uv_posle, km_oth_posle, zl_td_all, zl_td_paper, zl_td_proc,
                    #                        zl_td_el_all, zl_td_posle, zl_td_el_proc, ent_perv, zl_perv)
                    sqlStmtCheck = ('SELECT * FROM DB2ADMIN.PU_SZVTD_NEW WHERE  ENTNMB=?')
                    rows = isRecordNewCheck(sqlStmtCheck, ibm_db_conn, entnmb)



                    # ##// 'Нашёл!!!!'
                    if rows > 0:
                        notload_dop = notload_dop + 1
                        returnCode = False
                        sqlStatement = ( 'update DB2ADMIN.PU_SZVTD_NEW  set FL_DOP=1, DAT_LOAD=?, ZL_UNIC=?, ZL_UNIC_POSLE=?, KM_ALL_POSLE=? , KM_PRIEM_POSLE=? , KM_UV_POSLE=?, KM_OTH_POSLE=? , ZL_TD_ALL=? , ZL_TD_PAPER=? , ZL_TD_PROC=? , ZL_TD_EL_ALL=? , ZL_TD_POSLE=? , ZL_TD_EL_PROC=? , ENT_PERV=? , ZL_PERV=? where ENTNMB=? ')
                        if not SqlStmt(sqlStatement, ibm_db_conn,  dat_load,zl_unic, zl_unic_posle, km_all_posle,
                                       km_priem_posle, km_uv_posle, km_oth_posle, zl_td_all, zl_td_paper, zl_td_proc,
                                        zl_td_el_all, zl_td_posle, zl_td_el_proc, ent_perv, zl_perv,entnmb) :
                            message = f"{datetime.now()} - Can't run  sql stmt update, entnmb: {entnmb} - № row {j_dop}"
                            logging.info(message)
                            return
                        else:
                            message = f"{datetime.now()} - запись по допам существует, обновлена, entnmb: {entnmb}  - № row {j_dop}"
                            logging.info(message)
                            print(message)

                    #####################################
                    # не нашел добавляем
                    if rows == 0:
                        load_dop = load_dop + 1
                        dptcod = int(entnmb) // 1_000_000

                        fl_dop = 1

                        sqlStatement = """INSERT INTO  DB2ADMIN.PU_SZVTD_NEW  (DPTCOD, ENTNMB, ZL_UNIC, ZL_UNIC_POSLE, KM_ALL_POSLE, KM_PRIEM_POSLE, KM_UV_POSLE,
                                                       KM_OTH_POSLE, ZL_TD_ALL, ZL_TD_PAPER, ZL_TD_PROC, ZL_TD_EL_ALL, ZL_TD_POSLE, ZL_TD_EL_PROC, ENT_PERV, ZL_PERV, FL_DOP, DAT_LOAD)  
                                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                        if not SqlStmt(sqlStatement, ibm_db_conn, dptcod, entnmb, zl_unic, zl_unic_posle, km_all_posle,
                                   km_priem_posle, km_uv_posle,
                                   km_oth_posle, zl_td_all, zl_td_paper, zl_td_proc, zl_td_el_all, zl_td_posle,
                                   zl_td_el_proc, ent_perv, zl_perv, fl_dop, dat_load):
                            message = f"{datetime.now()} - Can't insert sql stmt, {entnmb}  - № row {j}"
                            logging.info(message)
                            return
                        else:
                            message = f"{datetime.now()} - добавлена новая запись по допам   {entnmb} - - № row {j_dop}"
                            logging.info(message)
                            print(message)



            message = f"{datetime.now()} - SZVTD допы, всего в списке: -  {j_dop},   загружено: -  {load_dop},  не загружено, запись существует: {notload_dop} "
            logging.info(message)
            print(message)
            input("Нажмите Enter, чтобы выйти...")

    else:
        message = f"{datetime.now()} -  Нет связи с БД"
        logging.info(message)
        print(message)
        input("Нажмите Enter, чтобы выйти...")


###################################################################################################################
def CopyFromPost ():
    source_folder_path = config['SZVTD_path']['source_folder_path']
    if check_network_drive_access(source_folder_path):
        specific_filename_pattern = config['SZVTD_path']['specific_filename_pattern']
        start_date = datetime.now() - timedelta(days=10)  # последние 30 дней
        matching_files = []
        for f in os.listdir(source_folder_path):
            if fnmatch.fnmatch(f, specific_filename_pattern):
                matching_files.append(f)
        if matching_files:
            latest_file = None
            latest_time = start_date.timestamp()
            for f in matching_files:
                file_path = os.path.join(source_folder_path, f)
                if os.path.getmtime(file_path) > latest_time:
                    latest_time = os.path.getmtime(file_path)
                    latest_file = f
            if latest_file:
                source_file = source_folder_path + latest_file
                destination_folder = config['SZVTD_path']['destination_folder']
                destination_file = destination_folder + latest_file
                if os.path.exists(destination_file):
                    message = f"{datetime.now()} - {latest_file} - проверка списков SZVTD, последний загруженный файл есть в рабочей директории, свежих файлов нет"
                    logging.info(message)
                    print(message)
                    input("Нажмите Enter, чтобы выйти...")

                    pass
                else:
                    shutil.copy(source_file, destination_folder)
                    source_file = destination_folder + latest_file
                    quckViborNew(source_file,logs_file)
            else:
                message = f"{datetime.now()} - {latest_file} - No matching file found within the last 7 days."
                logging.info(message)
                print(message)
                input("Нажмите Enter, чтобы выйти...")

        else:
            message = f"{datetime.now()} - {specific_filename_pattern} - No file matching the pattern found in the folder."
            logging.info(message)
            print(message)
            input("Нажмите Enter, чтобы выйти...")

    else:
        message = f"{datetime.now()} - {source_folder_path} - Remote folder is not mounted"
        logging.info(message)
        print(message)
        input("Нажмите Enter, чтобы выйти...")
def  quckViborNew(src_file,logs_file):

    directory = os.path.dirname(src_file)
    # Получаем время модификации исходного файла
    src_time = os.path.getmtime(src_file)
    older_file = None
    older_time = None
    specific_filename_pattern = config['SZVTD_path']['specific_filename_pattern']

    # Ищем все файлы в директории
    for file in os.listdir(directory):
        if fnmatch.fnmatch(file, specific_filename_pattern):  # Проверяем по шаблону
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                # Если файл старше исходного
                if file_time < src_time:
                    # Если это первый найденный старый файл или он старше предыдущего
                    if older_time is None or file_time > older_time:
                        older_file = file_path
                        older_time = file_time
    # можно одно поле прочитать
    csvFileOld = pd.read_csv(older_file, delimiter=';', encoding='cp1251')
    df1 = pd.DataFrame(csvFileOld)

    csvFileNew = pd.read_csv(src_file, delimiter=';', encoding='cp1251')
    df2 = pd.DataFrame(csvFileNew)

    df_diff = df2[~df2['Графа 4'].isin(df1['Графа 4'])]
    destination_folder = config['SZVTD_path']['destination_folder']
    source_file = destination_folder  + 'res.csv'
    df_diff.to_csv(source_file,sep=';', encoding='cp1251', )




    match = re.search(r'_(\d{4}_\d{2}_\d{2})\.csv$', src_file)
    if match:
        dat_load = match.group(1)

    ProcessFile(source_file,1,logs_file,dat_load)

    # Сравнение по двум графам
    # Объединение DataFrame по 'Графа 4'
    merged = df2.merge(df1[['Графа 4', 'Графа 8']], on='Графа 4', how='inner', suffixes=('_df2', '_df1'))

    # Фильтрация записей, где 'Графа 8' в df2 больше, чем в df1
    df_diff_dop = merged[merged['Графа 8_df2'] > merged['Графа 8_df1']]

    #df_diff_dop = df2[~df2[['Графа 4', 'Графа 8']].apply(tuple, ax is=1).isin(df1[['Графа 4', 'Графа 8']].apply(tuple, axis=1))]
    source_file_dop = destination_folder  + 'res_dop.csv'
    df_diff_dop.to_csv(source_file_dop, sep=';', encoding='cp1251', )

    ProcessFile(source_file_dop,2, logs_file, dat_load)




if __name__ == '__main__':
    message = f"{datetime.now()} -  start "
    logging.info(message)

    CopyFromPost ()


#    ProcessFile()



