
import os
import sys
import shutil
from datetime import date, datetime, timedelta
import fnmatch
import psutil
import logging
import configparser

os.add_dll_directory(r'c:\Python\Lib\site-packages\clidriver\bin')

import ibm_db
import ibm_db_dbi as db
import csv
import glob



# Создаем объект ConfigParser
#config = configparser.ConfigParser()
# Читаем файл конфигурации
#config.read('config.ini')

# Конфигурация логгера
#logs_file = config['logging']['logs_file']
#logging.basicConfig(filename=logs_file, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    database_username = 'super'
    database_password = '88888888'
    #10.2.2.133
    database_hostname = '10.2.2.204'
    database_port = '50000'
    database_name = 'ASV'
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
        print("Подключение успешно!")
        conn = db.Connection(ibm_db_conn)
    except Exception as e:
        print("Ошибка соединения:", e)
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
        print(rows)
        return True
        # ShowMessage('not exisct, new record!');
def ProcessFile(src_file,logs_file):
    conn, ibm_db_conn = connDb1()
    if conn:
        sqlStmtUpd = None
        sqlStmtCheck = None
        sqlStatement = None
        load = 0
        notload = 0
        j = 0
        message = f"{datetime.now()} - {src_file} - start "
        logging.info(message)
        print(message)

        #########################################################################################################
        with open(src_file, 'r') as input_file:

            col_names = ["ACTUAL_DPTCOD", "ACTUAL_ENTNMB", "INN", "KPP","SNILSCS", "FIO", "R_DATE", "GRAGD", "PENS",  "ENTNMB"     ,"ENTNMB_ZA", "NAME_ORG", "DAT_MEROPR",
                         "VID_KM"   ,"MEROPR","DOLG_NAME", "KOD_OKZ", "UVOLN_REASON", "NAME_DOC", "DAT_DOC", "NUM_DOC", "SOVMEST", "PRIZNAK_KS", "UUID", "FO_NUM",
                         "FO_DAT_TXT", "DAT_SPIS"]


            csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')

            sqlStmtUpd = 'update DB2ADMIN.SVR_DUBL_RAZN set newrec=0'

            # // Отметим  все звписи  как старые
            if not GetRecordasOld(sqlStmtUpd,ibm_db_conn):
                return

            returnCode = False
            fields = []
            fields = next(csvFile)
            for row in csvFile:
                j = j + 1
                uuid = str(row["UUID"])
                fo_num = str(row["FO_NUM"])
                # // Проверка uuid + fo_num
                sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_DUBL_RAZN WHERE  UUID=? and FO_NUM=?'
                rows = isRecordNewCheck(sqlStmtCheck, ibm_db_conn, uuid, fo_num)
                pens = row['PENS']
                inn = str(row["INN"]).zfill(10)
                kpp = str(row["KPP"]).zfill(9)
                fio = str(row["FIO"])
                sovmest = row['SOVMEST']
                priznak_ks = row['PRIZNAK_KS']
                r_date = row['R_DATE']
                if r_date == '':
                    r_date = None
                dat_spis = row['DAT_SPIS']
                if dat_spis == '':
                    dat_spis = None

                gragd = row['GRAGD']
                vid_km= row['VID_KM']
                vid_km=int(vid_km)
                # ##// 'Нашёл!!!!'
                if rows > 0:
                    notload = notload + 1
                    returnCode = False
                    sqlStatement = ("update DB2ADMIN.SVR_DUBL_RAZN set NEWREC=1, PENS=?, INN=?, KPP=?, FIO=?, SOVMEST=?, PRIZNAK_KS=?, R_DATE=?,  GRAGD = ?,"
                                            "VID_KM = ?, DAT_SPIS = ?  where UUID=? and FO_NUM=?")
                    if not SqlStmt(sqlStatement, ibm_db_conn, pens, inn,kpp,fio,sovmest,priznak_ks,r_date,gragd,vid_km,dat_spis,uuid,fo_num):
                        message = f"{datetime.now()} - Can't run  sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                        logging.info(message)
                        return
                    else:
                        message = f"{datetime.now()} - запись существует, обновлена, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                        logging.info(message)
                        print(message)

                #####################################
                # не нашел добавляем
                if rows == 0:
                    load = load + 1
                    entnmb = row["ENTNMB"]
                    entnmb = entnmb.replace('-', '')
                    dptcod = str(entnmb)

                    dptcod = dptcod.zfill(12)
                    dptcod = dptcod[0:6]
                    dptcod = int(dptcod)
                    entnmb_c = entnmb

                    entnmb = int(entnmb)
                    name_org = str(row["NAME_ORG"])
                    pens= row["PENS"]
                    actual_entnmb = row["ACTUAL_ENTNMB"]
                    actual_entnmb = actual_entnmb.replace('-', '')
                    actual_dptcod = str( actual_entnmb)

                    actual_dptcod = actual_dptcod.zfill(12)
                    actual_dptcod = actual_dptcod[0:6]
                    actual_dptcod = int(actual_dptcod)
                    actual_entnmb = int(actual_entnmb)

                    entnmb_za = row["ENTNMB_ZA"]
                    entnmb_za = entnmb_za.replace('-', '')
                    entnmb_za = str(entnmb_za)

                    dat_meropr = row['DAT_MEROPR']
                    if dat_meropr == '':
                        dat_meropr = None
                    meropr = str(row["MEROPR"])
                    dolg_name = str(row["DOLG_NAME"])
                    kod_okz = str(row["KOD_OKZ"])
                    uvoln_reason = str(row["UVOLN_REASON"])
                    name_doc = str(row["NAME_DOC"])
                    dat_doc = str(row['DAT_DOC'])
                    if dat_doc == '':
                        dat_doc = None

                    num_doc = str(row['NUM_DOC'])
                    fo_dat_txt = str(row["FO_DAT_TXT"])
                    dat_spis = str(row["DAT_SPIS"])
                    if dat_spis == '':
                        dat_spis = None

                    snilscs = str(row["SNILSCS"])
                    insnmb = row["SNILSCS"]
                    insnmb = insnmb.replace('-', '')
                    insnmb = insnmb[0:9]
                    insnmb = int(insnmb)

                    nspis = 1
                    # для первого списка 1 затем только для новых
                    in_uved = 1
                    dat_load = date.today()
                    newrec = 1

                    sqlStatement = """INSERT INTO DB2ADMIN.SVR_DUBL_RAZN (DPTCOD, ENTNMB, INN, KPP, SNILSCS, FIO, R_DATE, GRAGD, PENS,
                    ENTNMB_ZA, NAME_ORG, DAT_MEROPR,VID_KM, MEROPR, DOLG_NAME, KOD_OKZ, UVOLN_REASON, NAME_DOC, DAT_DOC,
                    NUM_DOC, SOVMEST, PRIZNAK_KS, UUID, FO_NUM, FO_DAT_TXT, DAT_SPIS, INSNMB, ACTUAL_ENTNMB, ACTUAL_DPTCOD,
                    N_SPIS , IN_UVED, NEWREC,NSPIS,ENTNMB_C)  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?,?)"""
                    if not SqlStmt(sqlStatement,ibm_db_conn,  dptcod, entnmb, inn, kpp, snilscs, fio, r_date, gragd, pens,
                                     entnmb_za, name_org, dat_meropr,vid_km, meropr, dolg_name, kod_okz, uvoln_reason, name_doc, dat_doc,
                                    num_doc, sovmest, priznak_ks, uuid, fo_num, fo_dat_txt, dat_spis, insnmb, actual_entnmb, actual_dptcod, nspis , in_uved, newrec,nspis,entnmb_c):
                        message = f"{datetime.now()} - Can't insert sql stmt, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                        logging.info(message)
                        return
                    else:
                        message = f"{datetime.now()} - добавлена новая запись uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                        logging.info(message)
                        print(message)

            message = f"{datetime.now()} - Дубли КМ, всего в списке: -  {j},   загружено: -  {load},  не загружено, запись существует: {notload} "
            logging.info(message)
            print(message)

            sqlStatement = """update DB2ADMIN.SVR_DUBL_RAZN set RES=null where newrec=1 and RES=6"""
            #if not SqlStmt(sqlStatement,ibm_db_conn)
            #    message = f"{datetime.now()} - Can't run sql stmt:update DB2ADMIN.SVR_DUBL_RAZN set RES=null where newrec=1 and RES=6"
            #    logging.info(message)
            #    return
            #message = f"{datetime.now()} - 'update set RES=null where newrec=1 and RES=6' finished"
            #logging.info(message)
            #print(message)

            sqlStatement = """update DB2ADMIN.SVR_DUBL_RAZN set RES=6 where newrec=0"""
            #if not SqlStmt(sqlStatement,ibm_db_conn)
            #    message = f"{datetime.now()} - Can't run sql stmt:update DB2ADMIN.SVR_DUBL_RAZN set RES=6 where newrec=0"
            #    logging.info(message)
            #    return
            #message = f"{datetime.now()} - update 'set RES=6 where newrec=0' finished"
            #logging.info(message)
            #print(message)

        message = "Список дубликаты КМ обработано - " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + \
                  " Всего в списке: " + str(j) + "\n" + \
                  "загружено, новые: " + str(load) + "\n" + \
                  "запись существует: " + str(notload)
        print(message)
        input("Нажмите Enter, чтобы выйти...")

    else:
        message = f"{datetime.now()} -  Нет связи с БД"
        logging.info(message)
        print(message)
        input("Нажмите Enter, чтобы выйти...")


###################################################################################################################
def CopyFromPost ():
    source_folder_path = config['path']['source_folder_path']
    if check_network_drive_access(source_folder_path):
        specific_filename_pattern = config['path']['specific_filename_pattern']
        start_date = datetime.now() - timedelta(days=30)  # последние 30 дней
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
                destination_folder = config['path']['destination_folder']
                destination_file =  destination_folder +  latest_file
                if os.path.exists(destination_file):
                    message = f"{datetime.now()} - {latest_file} - проверка списков DUBL_RAZN, последний загруженный файл есть в рабочей директории, свежих файлов нет"
                    logging.info(message)
                    print(message)
                    input("Нажмите Enter, чтобы выйти...")

                    pass
                else:
                    shutil.copy(source_file, destination_folder)
                    source_file= destination_folder + latest_file
                    ProcessFile(source_file,logs_file)
            else:
                message = f"{datetime.now()} - {latest_file} - No matching file found within the last 30 days."
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

if __name__ == '__main__':
    conn, ibm_db_conn = connDb1()
    if conn:
        inn=245967187
        ogrn=1210200045241
        sqlStmtCheck = "SELECT oo.OO_EXTRACT_ID, date(oop.OO_PACKAGE_TIMESTAMP) as TS,  oo.OO_EXTRACT_OGRN as ogrn, oo.OO_EXTRACT_INN as inn, '' as FOMS,  oop.OO_PACKAGE_FILE_NAME as XMLFILE  FROM db2inst.ASV_OO_EXTRACT oo  WHERE  (oo.OO_EXTRACT_INN = ? or oo.OO_EXTRACT_OGRN='?) order by  date(oop.OO_PACKAGE_TIMESTAMP) desc "
        rows = SqlStmt(sqlStmtCheck, ibm_db_conn, inn, ogrn)

#    ProcessFile()



