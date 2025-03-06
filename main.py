# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import sys
from PySide6.QtCore import (Qt,QFileInfo )
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFileDialog,
    QGridLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QComboBox,
    QTextEdit,
    QSpinBox
)


import os
os.add_dll_directory(r'c:\Python\Lib\site-packages\clidriver\bin')

import ibm_db
import ibm_db_dbi as db
import csv
from datetime import date, datetime, timedelta
import glob
import logging
import pandas as pd
# Конфигурация логгера
logs_file = r'c:\!!!\Списки\loader.log\\'
logging.basicConfig(filename=logs_file, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Loader2')
        self.setGeometry(500, 500, 500, 450)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.btnConn = QPushButton("1. Connect portal db")
        self.labelConn = QLabel("not connected")
        self.layout.addWidget(self.labelConn)
        self.layout.addWidget(self.btnConn)
        self.btnConn.clicked.connect(self.connDb1)

        self.lblListName = QLabel("Select list name:")
        self.layout.addWidget(self.lblListName)

        self.cmbBox=QComboBox()
        self.cmbBox.addItems(["...","ИС КМ позже 3м", "ИС КМ до даты регистрации", "Совместители, уволенные с основной должности","STAG_SFR",
                              "PENS","false","Есть код ОУТ - нет доптарифа","Есть доптариф за 2023 год, нет стажа с ОУТ","szv_budg_plan",
                              "Есть КМ Прием - нет увольнения, нет РСВ за следующие", "Педагоги, медики","Есть КМ с кодом РКС","КМ с некорректными  наименованиями организаций",
                              "temp_regnum_kp","Есть СЗВ-М за 2021-2023 год - нет стажа","kp_itog2024","Есть РСВ - нет КМ"])

        # The default signal from currentIndexChanged sends the index
        self.cmbBox.currentIndexChanged.connect(self.index_changed_cmbBox)
        self.layout.addWidget(self.cmbBox)

        self.labelYear = QLabel("Год? введите год напр. 2023 (для ркс\мкс берем из поля 'ЭТК_стаж январь 2023', для мед\пед из названия 'нет стаж за...')")
        self.layout.addWidget(self.labelYear)

        self.year_box = QSpinBox()
        self.year_box.setRange(2021,2035)
        self.layout.addWidget(self.year_box)
        self.year_box.valueChanged.connect(self.yerPedMed_value_changed)

        self.year_box.setEnabled(False)


        self.cmbBox.setEnabled(False)
        self.labelFile = QLabel("file: ")
        self.layout.addWidget(self.labelFile)
        self.btnFopn = QPushButton("3. openFile")
        self.btnFopn.setEnabled(False)
        self.layout.addWidget(self.btnFopn)
        self.btnFopn.clicked.connect(self.fopn1)
        self.labelStart = QLabel("")
        self.layout.addWidget(self.labelStart)
        self.btnStart = QPushButton("4. start")
        self.btnStart.setEnabled(False)
        self.layout.addWidget(self.btnStart)
        self.btnStart.clicked.connect(self.start1)
        self.textEdit = QTextEdit()
        self.layout.addWidget(self.textEdit)
        self.isConnected=False
        self.conn=None
        self.ibm_db_conn=None
        self.cursorID=None
        self.filename=None
        self.datload=None
        self.ListNmbr = -1
        self.yerPedMed = 2021
   # @QtCore.Slot()
    def connDb1(self):
        if not self.isConnected :
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
                self.ibm_db_conn = ibm_db.connect(connection_string, '', '')
                self.conn = db.Connection(self.ibm_db_conn)
                message = f"{datetime.now()} - A Db2 Database connected success"
                logging.info(message)
                self.labelConn.setText(u"<b>connected success</b>")
                #self.btnFopn.setEnabled(True)
                self.btnConn.setEnabled(False)
                self.cmbBox.setEnabled(True)
            except Exception:
                pass
            # If A Db2 Database Connection Could Not Be Established, Display An Error Message And Exit
            if  self.conn is None:
                message = f"{datetime.now()} - A Db2 Database Connection Could Not Be Established"
                logging.info(message)

                exit(-1)
            # Otherwise, Complete The Status Message
            else:
                self.isConnected = True

    def yerPedMed_value_changed(self, yer):
        self.yerPedMed=yer
    def index_changed_cmbBox(self, index):  # index is an int stating from 0
        self.btnFopn.setEnabled(True)


        text = self.cmbBox.currentText()
        self.lblListName.setText("List name: "+text)
        self.ListNmbr = index
        if index == 11 or index == 12:
            self.year_box.setEnabled(True)


    def fopn1(self):
        self.filename = QFileDialog.getOpenFileName(self, "Open File", "", "CSV data files (*.csv)")[0]
        if self.filename:
            self.labelFile.setText(u"file: "+self.filename)
            self.datload=date.today()
            self.btnStart.setEnabled(True)

    def isFileName(self):
        if ("КМ позже текущей даты+3 месяца" in self.filename and self.ListNmbr == 1)\
                or ("КМ до даты регистрации страхователя" in self.filename and self.ListNmbr == 2)\
                or ("Совместители, уволенные с основной должности" in self.filename and self.ListNmbr == 3)\
                or ("stag_sfr" in self.filename and self.ListNmbr == 4) \
                or ("szvm_no" in self.filename and self.ListNmbr == 5) \
                or ("false" in self.filename and self.ListNmbr == 6) \
                or ("нет доптарифа" in self.filename and self.ListNmbr == 7) \
                or ("нет стажа с ОУТ" in self.filename and self.ListNmbr == 8) \
                or ("budg" in self.filename and self.ListNmbr == 9) \
                or ("нет увольнения, нет РСВ" in self.filename and self.ListNmbr == 10) \
                or ("Педагоги, медики" in self.filename and self.ListNmbr == 11)\
                or ("Есть КМ с кодом РКС" in self.filename and self.ListNmbr == 12)\
                or ("КМ с некорректными наименованиями организаций" in self.filename and self.ListNmbr == 13)\
                or ("temp_regnum_kp" in self.filename and self.ListNmbr == 14)\
                or ("Есть СЗВ-М за 2021-2023 год - нет стажа" in self.filename and self.ListNmbr == 15)\
                or ("kp_itog2024" in self.filename and self.ListNmbr == 16) \
                or ("Есть РСВ - нет КМ" in self.filename and self.ListNmbr == 17) :
                    return True
        else:
            msgBox = QMessageBox()
            msgBox.setText("are you shure? file was renamed? ")
            msgBox.exec()
            return False

    def SqlStmt(self, sqlStmt, *args):
        preparedStmt = None
        returnCode = False
        try:
            preparedStmt = ibm_db.prepare(self.ibm_db_conn, sqlStmt)
        except Exception:

            message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - Transaction stmt couldn't be completed, row N"
            logging.info(message)
            pass
        if preparedStmt is False:
            self.conn.close()
            exit(-1)
        i=1
        for arg in args:
            try:
                returnCode = ibm_db.bind_param(preparedStmt, i, arg)
            except Exception:
                print(ibm_db.stmt_errormsg())
                returnCode=False
                pass
            i=i+1
        # If The Application Variable Was Not Bound Successfully, Display An Error Message And Exit
        if returnCode is False:
            print(ibm_db.stmt_errormsg())
            message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - ERROR: Unable to bind  specified.arg- {arg} - {i} - {preparedStmt}"
            logging.info(message)
            msgBox = QMessageBox()
            msgBox.setText("ERROR:  Unable to bind  specified.arg")
            msgBox.exec()

            self.conn.close()
            exit(-1)
        # Execute The Prepared SQL Statement (Using The New Parameter Marker Value)
        #for debug only!!!
        try:
            # for debug only!!!
            #returnCode  = True

            returnCode = ibm_db.execute(preparedStmt)

        except Exception:
            print(ibm_db.stmt_errormsg())
            message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - ERROR: Unable to execute the SQL statement"
            logging.info(message)
            returnCode=False
            pass
        # If The SQL Statement Could Not Be Executed, Display An Error Message And Exit
        if returnCode is False:
            message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - ERROR: Unable to execute the SQL statement"
            logging.info(message)
            msgBox = QMessageBox()

            msgBox.setText("ERROR:Unable to execute the SQL statement")
            msgBox.exec()

            self.conn.close()
            exit(-1)
        # Otherwise, Complete The Status Message
        else:
            return True
        # ShowMessage('not exisct, new record!');

    def GetRecordasOld(self, sqlStmt,*args):
        preparedStmtUpd = None
        returnCode=False
        try:
            preparedStmtUpd = ibm_db.prepare(self.ibm_db_conn, sqlStmt)
        except Exception:
            message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - Transaction prepare  update couldn't be completed"
            logging.info(message)
            pass
        if preparedStmtUpd is False:
            msgBox = QMessageBox()
            msgBox.setText("\nERROR: Unable to prepare the  SQL statement specified.")
            msgBox.exec()
            self.conn.close()
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
                    message = f"{datetime.now()} - {ibm_db.stmt_errormsg()} - Unable to bind getrecordasold the variable to the parameter marker  record exist specified.row N  "
                    logging.info(message)

                    self.conn.close()
                    exit(-1)

        try:
            # for debug only!!!!!!!!!!!!!!!
            #returnCode=True
            #pass
            returnCode = ibm_db.execute(preparedStmtUpd)

        except Exception:
            pass

        # If The SQL Statement Could Not Be Executed, Display An Error Message And Exit
        if returnCode is False:
            msgBox = QMessageBox()
            msgBox.setText("\nERROR: Unable to execute the SQL update statement.")
            msgBox.exec()
            self.conn.close()
            exit(-1)
        # # Otherwise, Complete The Status Message
        else:
            return True
    def isRecordNewCheck(self,sqlStmt,*args):
        preparedStmtCheck = None
        returnCode = False
        dataRecord = False

        try:
            preparedStmtCheck = ibm_db.prepare(self.ibm_db_conn, sqlStmt)
        except Exception:
            message = f"{datetime.now()} -{ibm_db.stmt_errormsg()} - check transaction couldn't be completed"
            logging.info(message)
            pass
        if preparedStmtCheck is False:
            self.conn.close()
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
                    self.conn.close()
                    exit(-1)
        try:
            returnCode = ibm_db.execute(preparedStmtCheck)
        except Exception:
            print(ibm_db.stmt_errormsg())
            pass
        # If The SQL Statement Could Not Be Executed, Display An Error Message And Exit
        if returnCode is False:
            self.conn.close()
            exit(-1)
        # Otherwise, Complete The Status Message
        dataRecord = False
        rows = 0
        try:
            dataRecord = ibm_db.fetch_tuple(preparedStmtCheck)
        except:
            print(ibm_db.stmt_errormsg())
            pass
        if dataRecord is False:
            rows = 0
        else:
            rows = 1
        return rows
    def null_check(self,*args):
        new_args = [arg for arg in args if arg is not None]
        result = self.isRecordNewCheck(*new_args)
        return result

    def null_check_upd(self,*args):
        new_args = [arg for arg in args if arg is not None]
        result = self.SqlStmt(*new_args)
        return result


    def start1(self):
        self.btnStart.setEnabled(False)
        self.labelStart.setText(u"starting..")
        sqlStmtUpd = None
        sqlStmtCheck = None
        sqlStatement = None
        load = 0
        notload = 0
        j = 0

        if not self.isFileName():
            return

        message = f"{datetime.now()} - {self.filename} - start "
        logging.info(message)

        ##################################################################################################################
        #    -----km 3 mes ---------------
        ##################################################################################################################
        if self.ListNmbr == 1:
            with open(self.filename, 'r') as input_file:
                col_names = ['ENTNMB','NAME_ORG','INN','KPP','STATUS','KATEG','KOD_SNYAT','DAT_SNYAT','DAT_MEROPR','MEROPR','DOC','DOC_N',
                            'DOC_DAT','SNILSCS','FIO','R_DATE','UUID','FO_NUM','FO_DAT_TXT']
                csvFile = csv.DictReader(input_file,fieldnames=col_names, delimiter=';')
                sqlStmtUpd = 'update DB2ADMIN.SVR_KM3MES set newrec=0'
                # // Отметим  все звписи  как старые
                if not self.GetRecordasOld(sqlStmtUpd):
                    return
                returnCode = False
                fields = []
                fields = next(csvFile)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append(str(j))
                    self.textEdit.update()
                    #logwriter.writerow(['', "loading "  + str(j)])
                    uuid = str(row["UUID"])
                    fo_num = str(row["FO_NUM"])
                    #// Проверка uuid + fo_num
                    sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_KM3MES WHERE  UUID=? and FO_NUM=?'
                    rows = self.isRecordNewCheck(sqlStmtCheck, uuid, fo_num)
                    dat_meropr = row['DAT_MEROPR']
                    if dat_meropr == '':
                        dat_meropr = None
                    # ##// 'Нашёл!!!!'
                    if rows > 0:
                        notload = notload+1
                        returnCode = False
                        sqlStatement = "update DB2ADMIN.SVR_KM3MES set NEWREC=1, DAT_MEROPR=?, DAT_MEROPR_T=?  where UUID=? and FO_NUM=?"
                        if not self.SqlStmt(sqlStatement,dat_meropr,dat_meropr,uuid,fo_num):
                            message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                    #####################################
                    # не нашел добавляем
                    if rows == 0 :
                        load=load+1
                        entnmb = row["ENTNMB"]
                        dptcod = str(entnmb)
                        dptcod = dptcod.zfill(12)
                        dptcod = dptcod[0:6]
                        dptcod = int(dptcod)
                        entnmb = int(entnmb)
                        nameorg = str(row["NAME_ORG"])
                        inn = str(row["INN"]).zfill(10)
                        kpp = str(row["KPP"]).zfill(9)
                        status = str(row["STATUS"]).zfill(2)
                        kateg = str(row["KATEG"]).zfill(4)
                        kod_snyat = row['KOD_SNYAT']
                        if  kod_snyat=='':
                            kod_snyat =None
                        dat_snyat = row['DAT_SNYAT']
                        if dat_snyat == '':
                            dat_snyat=None
                        meropr = str(row["MEROPR"])
                        doc_dat = str(row['DOC_DAT'])
                        doc = str(row["DOC"])
                        doc_n = str(row["DOC_N"])
                        snilscs = str(row["SNILSCS"])
                        insnmb = row["SNILSCS"]
                        insnmb = insnmb.replace('-', '')
                        insnmb = insnmb[0:9]
                        insnmb = int(insnmb)
                        fio = str(row["FIO"])
                        r_date = row['R_DATE']
                        fo_dat_txt = str(row["FO_DAT_TXT"])
                        nspis = 1
                        # для первого списка 1 затем только для новых
                        inuved = 1
                        #datload = date.today()
                        newrec = 1
                        sqlStatement = """INSERT INTO SVR_KM3MES (DPTCOD, ENTNMB, NAME_ORG, INN, KPP, STATUS, KATEG, KOD_SNYAT, DAT_SNYAT, DAT_MEROPR, MEROPR, DOC, DOC_N, DOC_DAT, SNILSCS, INSNMB, FIO, R_DATE, UUID, FO_NUM, FO_DAT_TXT, NSPIS , IN_UVED, DAT_LOAD, NEWREC,DAT_MEROPR_T) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)"""
                        if not self.SqlStmt(sqlStatement,dptcod,entnmb,nameorg,inn,kpp,status,kateg, kod_snyat,dat_snyat,dat_meropr, meropr, doc, doc_n, doc_dat, snilscs, insnmb, fio, r_date, uuid, fo_num, fo_dat_txt, nspis,inuved, self.datload, newrec, dat_meropr):
                            message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                self.textEdit.append('ИС КМ позже 3 мес, обработано всего :' +  str(j) +'  из них загружено новые: ' + str(load) )
                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        #              ---- km- do reg --------------------
        ###################################################################################################################
        elif self.ListNmbr == 2:
            with open(self.filename, 'r') as input_file:
                col_names = ['ACTUAL_ENTNMB','ANAME', 'AINN', 'AKPP',  'SNILSCS',  'FIO',  'ILS', 'D_DATE', 'ENTNMB', 'NAME_ORG', 'INN', 'KPP',
                        'KATEG', 'STATUS', 'KOD_POSTAN', 'DAT_POSTAN', 'KOD_SNYAT', 'DAT_SNYAT', 'SRSPOST', 'MEROPR', 'DAT_MEROPR', 'DOC',
                        'DOC_N','DOC_DAT','DATE_ILS','UUID','FO_NUM','FO_DAT_TXT']

                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                ##########################################
                # // Отметим  все звписи  как старые
                sqlStmtUpd = 'update DB2ADMIN.SVR_KMDOREG set newrec=0'
                if not self.GetRecordasOld(sqlStmtUpd):
                    return
                returnCode = False

                fields=[]
                fields = next(csvFile)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append('all: ' +str(j))
                    self.textEdit.update()
                    app.processEvents()

                    uuid = str(row["UUID"])
                    fo_num = str(row["FO_NUM"])
                    ##########################################################
                    # // Проверка uuid + fo_num
                    sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_KMDOREG WHERE  UUID=? and FO_NUM=?'
                    rows = self.isRecordNewCheck(sqlStmtCheck, uuid, fo_num)
                    dat_meropr = row['DAT_MEROPR']
                    if dat_meropr == '':
                        dat_meropr = None
                    # ##// 'Нашёл!!!!'
                    if rows > 0:


                        returnCode = False
                        sqlStmtUpd = ""
                        sqlStmtUpd = "update DB2ADMIN.SVR_KMDOREG set NEWREC=1, DAT_MEROPR=?, DAT_MEROPR_T=?  where UUID=? and FO_NUM=?"
                        if not self.SqlStmt(sqlStmtUpd,dat_meropr,dat_meropr,uuid,fo_num):
                            message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        notload = notload + 1
                        self.textEdit.append('not loaded, record exist: ' + str(notload))
                        app.processEvents()



                        #####################################
                    # не нашел, добавляем
                    if rows == 0:
                        entnmb = row["ENTNMB"]
                        dptcod = str(entnmb)
                        dptcod = dptcod.zfill(12)
                        dptcod = dptcod[0:6]
                        dptcod = int(dptcod)
                        entnmb = int(entnmb)
                        nameorg = str(row["NAME_ORG"])
                        actual_entnmb = row["ACTUAL_ENTNMB"]
                        actual_dptcod = str(actual_entnmb)
                        actual_dptcod = actual_dptcod.zfill(12)
                        actual_dptcod = actual_dptcod[0:6]
                        actual_dptcod = int(actual_dptcod)
                        actual_entnmb = int(actual_entnmb)
                        inn = str(row["INN"]).zfill(10)
                        kpp = str(row["KPP"]).zfill(9)
                        status = str(row["STATUS"]).zfill(2)
                        kateg = str(row["KATEG"]).zfill(4)
                        kod_postan= row['KOD_POSTAN']
                        if kod_postan == '':
                            kod_postan = None
                        dat_postan = row['DAT_POSTAN']
                        if dat_postan == '':
                            dat_postan = None
                        kod_snyat = row['KOD_SNYAT']
                        if kod_snyat == '':
                            kod_snyat = None
                        dat_snyat = row['DAT_SNYAT']
                        if dat_snyat == '':
                            dat_snyat = None
                        srspost=str(row["SRSPOST"])
                        date_ils=str(row["DATE_ILS"])
                        meropr = str(row["MEROPR"])
                        doc_dat = str(row['DOC_DAT'])
                        doc = str(row["DOC"])
                        doc_n = str(row["DOC_N"])
                        snilscs = str(row["SNILSCS"])
                        insnmb = row["SNILSCS"]
                        insnmb = insnmb.replace('-', '')
                        insnmb = insnmb[0:9]
                        insnmb = int(insnmb)
                        fio = str(row["FIO"])
                        ils= str(row["ILS"])

                        d_date = row['D_DATE']
                        if d_date == '':
                            d_date = None

                        fo_dat_txt = str(row["FO_DAT_TXT"])
                        nspis = 1
                        # для первого списка 1 затем только для новых
                        inuved = 1

                        newrec = 1
                        sqlStatement = """INSERT INTO SVR_KMDOREG (DPTCOD, ACTUAL_ENTNMB, ACTUAL_DPTCOD, ENTNMB, NAME_ORG, INN, KPP, STATUS, KATEG, KOD_POSTAN, DAT_POSTAN, 
                                               KOD_SNYAT, DAT_SNYAT, SRSPOST,  DAT_MEROPR, MEROPR, DOC, DOC_N, DOC_DAT, DATE_ILS, SNILSCS, INSNMB, FIO, ILS, D_DATE, UUID, FO_NUM, FO_DAT_TXT, NSPIS , IN_UVED, DAT_LOAD, NEWREC,DAT_MEROPR_T) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                        if not self.SqlStmt(sqlStatement, dptcod, actual_entnmb,actual_dptcod,entnmb, nameorg, inn, kpp, status, kateg, kod_postan,
                                       dat_postan, kod_snyat,dat_snyat,srspost,dat_meropr, meropr, doc, doc_n, doc_dat,date_ils, snilscs, insnmb, fio,
                                       ils, d_date, uuid, fo_num, fo_dat_txt, nspis, inuved, self.datload, newrec,
                                       dat_meropr):
                            message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        load = load + 1
                        self.textEdit.append('loaded, new record: ' + str(load))
                        app.processEvents()
                self.textEdit.append('ИС КМ до даты регистрации страхователя, обработано всего :' +  str(j) +'  из них загружено новые: ' + str(load) )
                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        #                      ----sovm_uv Совместители, уволенные с основной должности-----------------
        ###################################################################################################################
        elif self.ListNmbr == 3:
            with open(self.filename, 'r') as input_file:

           # row_count = len([row.rstrip() for row in input_file])

                col_names = ['ACTUAL_ENTNMB','ANAME', 'AINN', 'AKPP', 'AKOD', 'ASTATUS', 'AKOD_SNYAT', 'ADAT_SNYAT','ENTNMB', 'NAME_ORG',
                         'INN', 'KPP','KATEG', 'STATUS',  'KOD_SNYAT', 'DAT_SNYAT',
                         'SNILSCS',  'FIO',  'ILS', 'D_DATE', 'DAT_MEROPR', 'MEROPR','TIP_SOVM',  'NUM_DOC',
                         'DAT_DOC','UUID','FO_NUM','FO_DAT_TXT', 'DAT_MERUV', 'NUM_DOCUV',  'UUID_UV',  'FO_NUM_UV', 'FO_DATUV_T']

                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                ##########################################
                # // Отметим  все звписи  как старые
                sqlStmtUpd = 'update DB2ADMIN.SVR_SVM_UV set newrec=0'
                if not self.GetRecordasOld(sqlStmtUpd):
                    return
                returnCode = False

                fields=[]
                fields = next(csvFile)

                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append(str(j))
                    self.textEdit.update()
                    app.processEvents()

                    uuid = str(row["UUID"])

                    # uuid = str(df.loc[ind, "UUID"])
                    fo_num = str(row["FO_NUM"])

                    # fo_num = str(df.loc[ind, "FO_NUM"])
                    ##########################################################
                    # // Проверка uuid + fo_num
                    sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_SVM_UV WHERE  UUID=? and FO_NUM=?'
                    rows = self.isRecordNewCheck(sqlStmtCheck, uuid, fo_num)
                    dat_meropr = row['DAT_MEROPR']

                    if dat_meropr == '':
                        dat_meropr = None
                    tip_sovm = str(row["TIP_SOVM"])
                    # ##// 'Нашёл!!!!'
                    if rows > 0:
                        returnCode = False
                        sqlStmtUpd = ""

                        sqlStmtUpd = "update DB2ADMIN.SVR_SVM_UV set NEWREC=1, IN_UVED=0, DAT_MEROPR=?, TIP_SOVM=?  where UUID=? and FO_NUM=?"
                        if not self.SqlStmt(sqlStmtUpd,dat_meropr,tip_sovm, uuid,fo_num):
                            message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        notload = notload + 1
                        self.textEdit.append('notloaded, record exist: ' + str(notload))
                        app.processEvents()
                    #####################################
                    # не нашел добавляем
                    if rows == 0:
                        entnmb = row["ENTNMB"]

                        # entnmb = df.loc[ind, "ENTNMB"]
                        dptcod = str(entnmb)
                        dptcod = dptcod.zfill(12)
                        dptcod = dptcod[0:6]
                        dptcod = int(dptcod)
                        entnmb = int(entnmb)

                        nameorg = str(row["NAME_ORG"])

                        actual_entnmb = row["ACTUAL_ENTNMB"]
                        actual_dptcod = str(actual_entnmb)
                        actual_dptcod = actual_dptcod.zfill(12)
                        actual_dptcod = actual_dptcod[0:6]
                        actual_dptcod = int(actual_dptcod)
                        actual_entnmb = int(actual_entnmb)

                        inn = str(row["INN"]).zfill(10)
                        kpp = str(row["KPP"]).zfill(9)

                        a_inn = str(row["AINN"]).zfill(10)
                        a_kpp = str(row["AKPP"]).zfill(9)
                        a_name_org = str(row["ANAME"])


                        status = str(row["STATUS"]).zfill(2)
                        kateg = str(row["KATEG"]).zfill(4)

                        kod_snyat = row['KOD_SNYAT']
                        if kod_snyat == '':
                            kod_snyat = None

                        dat_snyat = row['DAT_SNYAT']
                        if dat_snyat == '':
                            dat_snyat = None
                        akod_snyat = row['AKOD_SNYAT']
                        if akod_snyat == '':
                            akod_snyat = None

                        adat_snyat = row['ADAT_SNYAT']
                        if adat_snyat == '':
                            adat_snyat = None

                        meropr = str(row["MEROPR"])
                        dat_doc = row['DAT_DOC']
                        num_doc = str(row["NUM_DOC"])
                        snilscs = str(row["SNILSCS"])
                        insnmb = row["SNILSCS"]
                        insnmb = insnmb.replace('-', '')
                        insnmb = insnmb[0:9]
                        insnmb = int(insnmb)
                        fio = str(row["FIO"])
                        ils= str(row["ILS"])
                        d_date = row['D_DATE']
                        if d_date == '':
                            d_date = None

                        fo_dat_txt = str(row["FO_DAT_TXT"])


                        dat_meruv = row["DAT_MERUV"]
                        num_docuv = str(row["NUM_DOCUV"])
                        uuid_uv = str(row["UUID_UV"])
                        fo_num_uv = str(row["FO_NUM_UV"])
                        fo_datuv_t = str(row["FO_DATUV_T"])

                        nspis = 1
                        # для первого списка 1 затем только для новых
                        in_uved = 1
                        dat_load = date.today()
                        newrec = 1
                        sqlStatement = """INSERT INTO SVR_SVM_UV (DPTCOD, ACTUAL_ENTNMB, ACTUAL_DPTCOD, AKOD_SNYAT, ADAT_SNYAT, ENTNMB, NAME_ORG, INN, KPP, STATUS, KATEG, 
                                           KOD_SNYAT, DAT_SNYAT,  DAT_MEROPR, MEROPR, NUM_DOC, DAT_DOC,  SNILSCS, INSNMB, FIO, ILS, D_DATE, UUID, FO_NUM, FO_DAT_TXT, 
                                            DAT_MERUV, NUM_DOCUV, UUID_UV, FO_NUM_UV, FO_DATUV_T, NSPIS , IN_UVED, DAT_LOAD, NEWREC, DAT_MEROPR_T, A_INN, A_KPP, A_NAME_ORG, TIP_SOVM) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement, dptcod, actual_entnmb,actual_dptcod,akod_snyat,adat_snyat,entnmb, nameorg, inn, kpp, status, kateg,
                                       kod_snyat,dat_snyat,dat_meropr, meropr,num_doc,dat_doc,  snilscs, insnmb, fio,
                                       ils, d_date, uuid, fo_num, fo_dat_txt, dat_meruv, num_docuv, uuid_uv, fo_num_uv,  fo_datuv_t, nspis, in_uved, self.datload, newrec,
                                       dat_meropr,a_inn,a_kpp,a_name_org,tip_sovm):
                            message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        load = load + 1
                        self.textEdit.append('loaded, new record: ' + str(load))
                        app.processEvents()
                self.textEdit.append('ИС Совместители,  уволен с основ должн., обработано всего :' +  str(j) +'  из них загружено новые: ' + str(load) )

                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        #                -stag2023---
        ###################################################################################################################
        elif self.ListNmbr == 4:
            with open(self.filename, 'r') as input_file:
                col_names = ['DPTCOD','ENTNMB_C',   'SNILSCS', 'FL_STAG' ]
                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                #logwriter = csv.writer(logsfile, delimiter=';')
                #logwriter.writerow(['datload','list', 'err'])
                #logwriter.writerow([self.datload,'STAG_SFR', ''])

                ##########################################
                # // Отметим  все звписи  как старые
                sqlStmtUpd = 'update DB2ADMIN.STAG_SFR set newrec=0'
                if not self.GetRecordasOld(sqlStmtUpd):
                    return

                returnCode = False
                fields = []
                fields = next(csvFile)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append(str(j))
                    self.textEdit.update()

                    entnmb_c = row["ENTNMB_C"]
                    fl_stag = row["FL_STAG"]
                    if fl_stag=='да':
                        fl_stag=1
                    else:
                        fl_stag=0
                    entnmb = entnmb_c.replace('-', '')
                    dptcod = str(entnmb)
                    dptcod = dptcod.zfill(12)
                    dptcod = dptcod[0:6]
                    dptcod = int(dptcod)
                    entnmb = int(entnmb)
                    snilscs = row["SNILSCS"]
                    insnmb = snilscs.replace('-', '')
                    insnmb = insnmb[0:9]
                    insnmb = int(insnmb)
                    ##########################################################
                    # // Проверка entnmb + snilscs
                    sqlStmtCheck = 'SELECT * FROM DB2ADMIN.STAG_SFR WHERE  ENTNMB=? and INSNMB=?'
                    rows = self.isRecordNewCheck(sqlStmtCheck, entnmb, insnmb)

                    ##// 'Нашёл!!!!'
                    if rows > 0:
                        notload = notload + 1
                        returnCode = False
                        sqlStmtUpd = ""
                        sqlStmtUpd = "update DB2ADMIN.STAG_SFR set NEWREC=1, FL_STAG=?, DAT_LOAD=?  where ENTNMB=? and INSNMB=?"
                        if not self.SqlStmt(sqlStmtUpd, fl_stag, self.datload, entnmb, insnmb):
                            #message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            message = f"{datetime.now()} - Can't run sql stmt update,  № row {j}"

                            logging.info(message)

                            return

                            # не нашел добавляем
                    if rows == 0:
                        load = load + 1
                        nspis = 1
                        newrec = 1
                        sqlStatement = """INSERT INTO STAG_SFR (DPTCOD,ENTNMB_C, ENTNMB,  SNILSCS, INSNMB, FL_STAG, NSPIS , NEWREC, DAT_LOAD) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                        if not self.SqlStmt(sqlStatement, dptcod, entnmb_c, entnmb, snilscs,insnmb, fl_stag, nspis, newrec,  self.datload):
                            #message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            message = f"{datetime.now()} - Can't run sql stmt insert, - № row {j}"

                            logging.info(message)

                            return
                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        #                       - SZVM_NO pens ----
        ###################################################################################################################
        elif self.ListNmbr == 5:
            mask = '02_szvm_no_*.csv'
            directory = os.path.dirname(self.filename)
            files = glob.glob(f"{directory}/{mask}")
            QApplication.setOverrideCursor(Qt.WaitCursor)
            load = 0
            notload = 0
            j = 0
            for file in files:
                message = f"{datetime.now()} - {file}"
                logging.info(message)
                self.textEdit.append(str(file))
                self.textEdit.update()
                app.processEvents()

                load_file = 0
                notload_file = 0
                j_file = 0

                with open(file, 'r') as input_file:
                    file_info = QFileInfo(file)
                    file_name = file_info.fileName()
                    tmpstr = file_name[11:]
                    tmpindex = tmpstr.index('m')
                    yer = int(tmpstr[tmpindex+1:tmpindex+5])
                    mon = int(tmpstr[0:tmpindex])
                    csvFile = csv.DictReader(input_file, delimiter=';')
                    sqlStmtUpd = 'update DB2ADMIN.SVR_SZVM_NO_10M set actual=null where YER=? and MON=?'
                    # // Отметим  все звписи  как старые
                    if not self.GetRecordasOld(sqlStmtUpd,yer,mon):
                        return
                    returnCode = False
                    for row in csvFile:
                        j = j + 1
                        j_file = j_file + 1
                        snilscs = str(row["SNILSCS"])
                        reg_num = int(row["REG_NUM"])
                        meropr= str(row["MEROPR"])
                        dol=str(row["DOL"])
                        meropr_date = row["MEROPR_DATE"]

                        priznak_sovmest = row["PRIZNAK_SOVMEST"]
                        #// Проверка
                        sqlStmtCheck = 'select * from DB2ADMIN.SVR_SZVM_NO_10M where SNILSCS=? and REG_NUM=?  and MEROPR=? and DOL=? and YER=? and MON=?'
                        rows = self.isRecordNewCheck(sqlStmtCheck, snilscs, reg_num, meropr, dol, yer, mon)

                        if priznak_sovmest == '' and meropr_date == '':
                            sqlStmtCheck = sqlStmtCheck + ' and PRIZNAK_SOVMEST is null and MEROPR_DATE is null'
                            rows = self.isRecordNewCheck(sqlStmtCheck, snilscs, reg_num, meropr, dol, yer, mon)

                        else:
                            if len(priznak_sovmest)>0 and len(meropr_date) >0:
                                sqlStmtCheck = sqlStmtCheck + ' and PRIZNAK_SOVMEST=?  and MEROPR_DATE=? '
                                rows = self.isRecordNewCheck(sqlStmtCheck, snilscs, reg_num, meropr, dol, yer, mon, priznak_sovmest,meropr_date)
                            else:
                                if meropr_date == '':
                                    sqlStmtCheck = sqlStmtCheck + ' and PRIZNAK_SOVMEST=?  and MEROPR_DATE is null'
                                    rows = self.isRecordNewCheck(sqlStmtCheck, snilscs, reg_num, meropr, dol, yer, mon, priznak_sovmest)
                                else:
                                    sqlStmtCheck = sqlStmtCheck + ' and MEROPR_DATE=?  and PRIZNAK_SOVMEST is null'
                                    rows = self.isRecordNewCheck(sqlStmtCheck, snilscs, reg_num, meropr, dol, yer, mon, meropr_date)



                        reg_organ_unreg_date=row["REG_ORGAN_UNREG_DATE"]
                        if reg_organ_unreg_date == '':
                            reg_organ_unreg_date = None

                        ifns_unreg_date=row["IFNS_UNREG_DATE"]
                        if ifns_unreg_date == '':
                            ifns_unreg_date = None

                        message = f"{datetime.now()} -  № row: {j_file} - snils: {snilscs}  "
                        logging.info(message)

                        # ##// 'Нашёл!!!!'
                        if rows > 0:


                            returnCode = False
                            sqlStatement = 'update DB2ADMIN.SVR_SZVM_NO_10M set actual = 1, REG_ORGAN_UNREG_DATE=?, IFNS_UNREG_DATE=? where SNILSCS=? and REG_NUM=? and MEROPR=? and DOL=? and YER=? and MON=?  '
                            #if not self.SqlStmt(sqlStatement,reg_organ_unreg_date, ifns_unreg_date, snilscs, reg_num, meropr, dol, yer,mon, priznak_sovmest, meropr_date):
                            #    message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            #    logging.info(message)
                            #    return

                            if priznak_sovmest == '' and meropr_date == '':
                                sqlStatement = sqlStatement +'and  PRIZNAK_SOVMEST is null and MEROPR_DATE is null '

                                if meropr_date == '':
                                    meropr_date = None
                                if priznak_sovmest == '':
                                    priznak_sovmest = None

                                if not self.SqlStmt(sqlStatement,reg_organ_unreg_date, ifns_unreg_date, snilscs, reg_num, meropr, dol, yer,mon):
                                    #message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                                    message = f"{datetime.now()} - Can't run sql stmt update,  - № row {j}"

                                    logging.info(message)
                                    return
                            else:

                                if len(priznak_sovmest) > 0 and len(meropr_date) > 0:
                                    if meropr_date == '':
                                        meropr_date = None
                                    if priznak_sovmest == '':
                                        priznak_sovmest = None

                                    sqlStatement = sqlStatement + ' and  PRIZNAK_SOVMEST=? and MEROPR_DATE=?'
                                    if not self.SqlStmt(sqlStatement,reg_organ_unreg_date, ifns_unreg_date, snilscs, reg_num, meropr, dol, yer,mon, priznak_sovmest, meropr_date):
                                        #message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                                        message = f"{datetime.now()} - Can't run sql stmt update,  № row {j}"

                                        logging.info(message)
                                        return

                                else:
                                    if meropr_date == '':
                                        meropr_date = None

                                    if priznak_sovmest == '':
                                        priznak_sovmest = None

                                    if meropr_date == None:
                                        sqlStatement = sqlStatement + ' and PRIZNAK_SOVMEST=?  and MEROPR_DATE is null'
                                        if not self.SqlStmt(sqlStatement,reg_organ_unreg_date, ifns_unreg_date, snilscs, reg_num, meropr, dol, yer,mon, priznak_sovmest):
                                            #message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                                            message = f"{datetime.now()} - Can't run sql stmt update,  - № row {j}"

                                            logging.info(message)
                                            return
                                    else:
                                        sqlStatement = sqlStatement +  ' and MEROPR_DATE=?  and PRIZNAK_SOVMEST is null'
                                        if not self.SqlStmt(sqlStatement,reg_organ_unreg_date, ifns_unreg_date, snilscs, reg_num, meropr, dol, yer,mon, meropr_date):
                                            #message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                                            message = f"{datetime.now()} - Can't run sql stmt update,  - № row {j}"

                                            logging.info(message)
                                            return
                            notload = notload + 1
                            notload_file = notload_file + 1

                            self.textEdit.append('not loaded, record exist: ' + str(notload_file))
                            self.textEdit.update()
                            app.processEvents()

                        #####################################
                        # не нашел добавляем
                        if rows == 0 :


                            dptcod = str(reg_num)
                            dptcod = dptcod.zfill(12)
                            dptcod = dptcod[0:6]
                            dptcod = int(dptcod)
                            insnmb =  snilscs
                            insnmb = insnmb.replace('-', '')
                            insnmb = insnmb[0:9]
                            insnmb = int(insnmb)

                            status_ils = str(row["STATUS_ILS"])
                            death_date = row["DEATH_DATE"]
                            if death_date == '':
                                death_date = None

                            fio = str(row["FIO"])
                            birth_date = row["BIRTH_DATE"]
                            if birth_date == '':
                                birth_date = None

                            pens = row["PENS"]
                            if pens == '':
                                pens = None
                            date_pens = row["DATE_PENS"]
                            if date_pens == '':
                                date_pens = None

                            ctg = row["CTG"]
                            if ctg == '':
                                ctg = None
                            else:
                                ctg=int(ctg )

                            inn = str(row["INN"])

                            kpp = str(row["KPP"])
                            if kpp=='-':
                                kpp=''
                            sts_id = row["STS_ID"]
                            if sts_id == '':
                                sts_id = None
                            else:
                                sts_id=int(sts_id)
                            ar_id = row["AR_ID"]
                            if ar_id == '':
                                ar_id = None
                            else:
                                ar_id=int(ar_id)

                            rr_id = row["RR_ID"]
                            if rr_id == '':
                                rr_id = None
                            else:
                                rr_id=int(rr_id)
                            reg_organ_reg_date = row["REG_ORGAN_REG_DATE"]
                            if reg_organ_reg_date == '':
                                reg_organ_reg_date = None


                            ifns_reg_date = row["IFNS_REG_DATE"]
                            if ifns_reg_date == '':
                                ifns_reg_date = None
                            if mon==1:
                                szvm09 = str(row["SZVM12"])
                            else:
                                szvm09 = str(row["SZVM"+str(mon-1)])
                            szvm10 = str(row["SZVM"+str(mon)])
                            if meropr_date == '':
                                meropr_date = None
                            if priznak_sovmest == '':
                                priznak_sovmest = None

                            actual=1
                            sqlStatement = """INSERT INTO DB2ADMIN.SVR_SZVM_NO_10M  (DPTCOD, INSNMB, SNILSCS, STATUS_ILS, DEATH_DATE, FIO, BIRTH_DATE, PENS, DATE_PENS, REG_NUM,  CTG, INN, KPP, STS_ID, AR_ID, RR_ID,
                                              REG_ORGAN_REG_DATE, IFNS_REG_DATE, REG_ORGAN_UNREG_DATE, IFNS_UNREG_DATE, SZVM09, SZVM10,   MEROPR, MEROPR_DATE, DOL, 
                                              PRIZNAK_SOVMEST,YER,MON, ACTUAL )  VALUES (?, ?,  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""


                            if not self.SqlStmt(sqlStatement,dptcod, insnmb, snilscs, status_ils, death_date, fio, birth_date, pens, date_pens, reg_num,  ctg, inn, kpp, sts_id, ar_id, rr_id,
                                              reg_organ_reg_date, ifns_reg_date, reg_organ_unreg_date, ifns_unreg_date, szvm09, szvm10,   meropr, meropr_date, dol,
                                              priznak_sovmest,yer,mon, actual):
                                #message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                                message = f"{datetime.now()} - Can't run sql stmt insert, - № row {j}"

                                logging.info(message)


                                return
                            load = load + 1
                            load_file = load_file + 1

                            self.textEdit.append('loaded, new record: ' + str(load_file))
                            self.textEdit.update()
                            app.processEvents()


                if j_file > 0:
                    message = f"{datetime.now()} - Done {file} - Всего в списке: {j_file} - loaded, new record: {load_file} - not loaded, record exist: {notload_file}"
                    logging.info(message)
            self.textEdit.append('Pens всего :' + str(
                j_file) + '  из них загружено новые: ' + str(load_file))

            QApplication.restoreOverrideCursor()
        ##################################################################################################################
        #    -----ИНОСРАНЦЫ ---------------
        ##################################################################################################################
        elif self.ListNmbr == 6:
            with open(self.filename, 'r') as input_file:

                col_names = ["DPTCOD",    "RGN_ILS", "RGN_CHG_ILS", "INSNMB",  "SNILSCS",  "ILS_STATUS", "DAT_ILS", "FAM",  "NAM",  "PTR",
                             "GNDR",  "R_DATE",   "DTH_DATE","GRAZH","BRTH_D_TYPE","BRTH_D_CNTRY","BRTH_D_RGN","BRTH_D_RN","BRTH_D_PUNKT","DUL_CHLD_TYPE","DUL_CHLD",
                             "DUL_CHLD_SER_ROME", "DUL_CHLD_SER_RUS","DUL_CHLD_NMB", "DUL_CHLD_KEM_VIDAN" ,"DUL_CHLD_DATE_VID", "MSK_DPT", "MSK_SER",
                             "MSK_NMBR", "PENS_DPT", "ID_FBDP", "FIO_MTHR","R_DATE_MTHR","SNILSCS_MTHR", "FIO_MTHR_EGIS", "R_DATE_MTHR_EGIS", "SNILSCS_MTRH_EGIS"]

                             #"MSK_RASPOR","OTHER_VIPL_DPT","OTHER_VIPL_PRIZNAK","RES","RES_WORK","RES_NOTWORK","NSPIS", "COMMENT","ZAPROS_MVD","ZAPROS_POS",
                             #"OTVET_MVD", "OTVET_POS","DAT_LOAD","NEWREC","YEAR","MON"]





                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                # sqlStmtUpd = 'update DB2ADMIN.SVR_INOSTR_DUL set newrec=0'
                # // Отметим  все звписи  как старые
                #if not self.GetRecordasOld(sqlStmtUpd):
                #    return
                #returnCode = False
                fields = []
                fields = next(csvFile)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                dptcod=(2540,2760,2801,2802,2803,2804,2805,2807,2808,2810,2812,2814,2815,2816,2817,2818,2819,2820,2821,2822,2823,2824,2825,
                        2826,2827,2829,2830,2831,2832,2833,2834,2836,2837,2838,2840,2841,2842,2843,2844,2845,2847,2848,2849,2850,2851,2852,2853,
                        2854,2855,2856,2857,2858,2859,2860,2861,2862,2863,2865,2866,2867,2868,2869,2870,2871,2873,2874,2876,2878,2879)
                cnt_dpt=0
                for row in csvFile:
                    j = j + 1
                    cnt_dpt = cnt_dpt+1
                    self.textEdit.append(str(j))
                    self.textEdit.update()
                    # 'Нашёл!!!!'
                    rows=0
                    if rows > 0:
                        notload = notload + 1
                        returnCode = False
                        sqlStatement = "update DB2ADMIN.SVR_KM3MES set NEWREC=1, DAT_MEROPR=?, DAT_MEROPR_T=?  where UUID=? and FO_NUM=?"
                        if not self.SqlStmt(sqlStatement, dat_meropr, dat_meropr, uuid):
                            message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                    #####################################
                    # не нашел добавляем
                    if rows == 0:
                        load = load + 1
                        if cnt_dpt<69:
                            dptcod_value = dptcod[cnt_dpt]
                        else:
                            cnt_dpt=1
                            dptcod_value = dptcod[cnt_dpt]

                        rgn_ils = int(row["RGN_ILS"])
                        rgn_chg_ils = int(row["RGN_CHG_ILS"])
                        insnmb = int(row["INSNMB"])
                        snilscs = str(row["SNILSCS"])
                        ils_status = str(row["ILS_STATUS"])
                        fam = str(row["FAM"])
                        nam = str(row["NAM"])
                        ptr = str(row["PTR"])
                        if ptr == '' or ptr == '-':
                            ptr = None
                        gndr = str(row["GNDR"])
                        grazh = str(row["GRAZH"])
                        brth_d_type = str(row["BRTH_D_TYPE"])

                        brth_d_cntry = str(row["BRTH_D_CNTRY"])
                        if brth_d_cntry == '' or brth_d_cntry == '-':
                            brth_d_cntry = None

                        brth_d_rgn = str(row["BRTH_D_RGN"])
                        if brth_d_rgn == '' or brth_d_rgn == '-':
                            brth_d_rgn = None

                        brth_d_rn = str(row["BRTH_D_RN"])
                        if brth_d_rn  == '' or brth_d_rn  == '-':
                            brth_d_rn  = None

                        brth_d_punkt = str(row["BRTH_D_PUNKT"])

                        dul_chld_type = str(row["DUL_CHLD_TYPE"])
                        dul_chld = str(row["DUL_CHLD"])
                        dul_chld_ser_rome = str(row["DUL_CHLD_SER_ROME"])
                        if dul_chld_ser_rome  == '' or dul_chld_ser_rome  == '-':
                            dul_chld_ser_rome  = None

                        dul_chld_ser_rus = str(row["DUL_CHLD_SER_RUS"])
                        dul_chld_nmb = str(row["DUL_CHLD_NMB"])

                        dul_chld_kem_vidan = str(row["DUL_CHLD_KEM_VIDAN"])
                        msk_dpt = str(row["MSK_DPT"])
                        if msk_dpt == '' or msk_dpt=='-':
                            msk_dpt = None
                        msk_ser = str(row["MSK_SER"])
                        if msk_ser == '' or msk_ser == '-':
                            msk_ser = None

                        msk_nmbr = str(row["MSK_NMBR"])
                        if msk_nmbr == '' or msk_nmbr == '-':
                            msk_nmbr = None

                        pens_dpt = str(row["PENS_DPT"])
                        if pens_dpt == '' or pens_dpt=='-':
                            pens_dpt = None

                        id_fbdp = str(row["ID_FBDP"])
                        if id_fbdp == '' or id_fbdp=='-':
                            id_fbdp = None
                        fio_mthr = str(row["FIO_MTHR"])
                        if fio_mthr == '' or fio_mthr=='-':
                            fio_mthr = None

                        r_date_mthr = str(row["R_DATE_MTHR"])
                        if r_date_mthr == '' or r_date_mthr == '-':
                            r_date_mthr = None

                        snilscs_mthr = str(row["SNILSCS_MTHR"])
                        if snilscs_mthr == '' or snilscs_mthr == '-':
                            snilscs_mthr = None

                        fio_mthr_egis = str(row["FIO_MTHR_EGIS"])
                        if fio_mthr_egis == '' or fio_mthr_egis == '-':
                            fio_mthr_egis = None


                        snilscs_mtrh_egis = str(row["SNILSCS_MTRH_EGIS"])
                        if snilscs_mtrh_egis == '' or snilscs_mtrh_egis == '-':
                            snilscs_mtrh_egis = None



                        dat_ils = row['DAT_ILS']
                        if dat_ils == '' or dat_ils == '-':
                            dat_ils = None

                        r_date = row['R_DATE']
                        if r_date == '' or r_date == '-':
                            r_date = None

                        dth_date =  row['DTH_DATE']
                        if dth_date == '' or dth_date == '-':
                            dth_date = None

                        dul_chld_date_vid = row['DUL_CHLD_DATE_VID']
                        if dul_chld_date_vid == '' or dul_chld_date_vid == '-':
                            dul_chld_date_vid = None

                        r_date_mthr = row['R_DATE_MTHR']
                        if r_date_mthr == '' or r_date_mthr=='-' :
                            r_date_mthr = None

                        r_date_mthr_egis = row['R_DATE_MTHR_EGIS']
                        if r_date_mthr_egis == '' or r_date_mthr_egis == '-':
                            r_date_mthr_egis = None

                        nspis = 1
                        # для первого списка 1 затем только для новых
                        newrec = 1
                        msk_raspor=None
                        other_vipl_dpt=None
                        # здесь потом дописать
                        # квартал 3,6,9,12
                        year=2024

                        mon=6







                        sqlStatement = """INSERT INTO SVR_INOSTR_DUL ( DPTCOD , RGN_ILS, RGN_CHG_ILS, INSNMB, SNILSCS, ILS_STATUS, DAT_ILS,
                                      FAM, NAM, PTR, GNDR, R_DATE, DTH_DATE, GRAZH,  BRTH_D_TYPE,  BRTH_D_CNTRY,  BRTH_D_RGN,  BRTH_D_RN, BRTH_D_PUNKT, 
                                      DUL_CHLD_TYPE, DUL_CHLD, DUL_CHLD_SER_ROME,  DUL_CHLD_SER_RUS, DUL_CHLD_NMB, DUL_CHLD_KEM_VIDAN, DUL_CHLD_DATE_VID, 
                                      MSK_DPT, MSK_SER, MSK_NMBR,  PENS_DPT, ID_FBDP, FIO_MTHR, R_DATE_MTHR, SNILSCS_MTHR, FIO_MTHR_EGIS, R_DATE_MTHR_EGIS, 
                                      SNILSCS_MTRH_EGIS, MSK_RASPOR, OTHER_VIPL_DPT, NSPIS,NEWREC, YEAR, MON,DAT_LOAD)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement, dptcod_value , rgn_ils, rgn_chg_ils, insnmb, snilscs, ils_status, dat_ils,
                                      fam, nam, ptr, gndr, r_date, dth_date, grazh,  brth_d_type,  brth_d_cntry,  brth_d_rgn,  brth_d_rn, brth_d_punkt,
                                      dul_chld_type, dul_chld, dul_chld_ser_rome,  dul_chld_ser_rus, dul_chld_nmb, dul_chld_kem_vidan, dul_chld_date_vid,
                                      msk_dpt, msk_ser, msk_nmbr,  pens_dpt, id_fbdp, fio_mthr, r_date_mthr, snilscs_mthr, fio_mthr_egis, r_date_mthr_egis,
                                      snilscs_mtrh_egis, msk_raspor, other_vipl_dpt, nspis,newrec, year, mon, self.datload):
                            message = f"{datetime.now()} - Can't run sql stmt insert,  - № row {j}"
                            logging.info(message)

                            return
                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        #    ----- ЕСТЬ  КОД ОУТ  НЕТ  ДОПТАРИФА ---------------
        ###################################################################################################################
        elif self.ListNmbr == 7:
            with (open(self.filename, 'r') as input_file):
                col_names = ['SNILS', 'FIO', 'STATUS_ILS', 'D_DATE', 'YEAR', 'REG_NUM', 'FULL_NAME', 'INN',
                             'KPP', 'KATEG', 'STATUS', 'KOD_SNYAT', 'DAT_SNYAT', 'A_REG_NUM',
                             'A_NAME', 'AINN', 'A_KPP', 'A_ADRESS', 'STG_TYPE', 'ILS_DATE', 'STG_BEGIN',
                             'STG_END', 'KOD1_23', 'KOD2_23', 'KOD3_23',
                             'KOD4_23', 'KOD5_23', 'KOD6_23', 'KOD7_23', 'KOD8_23', 'KOD9_23', 'KOD10_23',
                             'KOD11_23', 'KOD12_23']
                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                ##########################################
                # // Отметим  все звписи  как старые
                sqlStmtUpd = 'update DB2ADMIN.SVR_DT_LGOT_1723 set newrec=0'
                if not self.GetRecordasOld(sqlStmtUpd):
                    return
                returnCode = False

                fields=[]
                fields = next(csvFile)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append('all: ' +str(j))
                    self.textEdit.update()
                    app.processEvents()
                    ##########################################################
                    # //
                    reg_num = row["REG_NUM"]
                    snils = str(row["SNILS"])
                    snils = snils.replace('-', '')
                    snils = snils[0:9]
                    snils = int(snils)
                    dptcod = str(reg_num)
                    dptcod = dptcod.zfill(12)
                    dptcod = dptcod[0:6]
                    dptcod = int(dptcod)
                    reg_num = int(reg_num)
                    a_reg_num = row["A_REG_NUM"]

                    a_dptcod = str(a_reg_num)
                    a_dptcod = a_dptcod.zfill(12)
                    a_dptcod = a_dptcod[0:6]
                    a_dptcod = int(a_dptcod)
                    a_reg_num = int(a_reg_num)

                    kod1_23 = str(row["KOD1_23"])
                    if kod1_23:
                        jan23 = 'нет'
                    else:
                        jan23 = ''

                    kod2_23 = str(row["KOD2_23"])
                    if kod2_23:
                        feb23 = 'нет'
                    else:
                        feb23 = ''
                    kod3_23 = str(row["KOD3_23"])
                    if kod3_23:
                        mar23 = 'нет'
                    else:
                        mar23 = ''
                    kod4_23 = str(row["KOD4_23"])
                    if kod4_23:
                        apr23 = 'нет'
                    else:
                        apr23 = ''

                    kod5_23 = str(row["KOD5_23"])
                    if kod5_23:
                        may23 = 'нет'
                    else:
                        may23 = ''

                    kod6_23 = str(row["KOD6_23"])
                    if kod6_23:
                        jun23 = 'нет'
                    else:
                        jun23 = ''
                    kod7_23 = str(row["KOD7_23"])
                    if kod7_23:
                        jul23 = 'нет'
                    else:
                        jul23 = ''
                    kod8_23 = str(row["KOD8_23"])
                    if kod8_23:
                        aug23 = 'нет'
                    else:
                        aug23 = ''
                    kod9_23 = str(row["KOD9_23"])
                    if kod9_23:
                        sep23 = 'нет'
                    else:
                        sep23 = ''

                    kod10_23 = str(row["KOD10_23"])
                    if kod10_23:
                        okt23 = 'нет'
                    else:
                        okt23 = ''
                    kod11_23 = str(row["KOD11_23"])
                    if kod11_23:
                        nov23 = 'нет'
                    else:
                        nov23 = ''

                    kod12_23 = str(row["KOD12_23"])
                    if kod12_23:
                        decm23 = 'нет'
                    else:
                        decm23 = ''

                    stg_begin = row["STG_BEGIN"]
                    stg_end = row["STG_END"]
                    ils_date = row["ILS_DATE"]





                    sqlStmtCheck = """SELECT * FROM DB2ADMIN.SVR_DT_LGOT_1723 WHERE SNILS=? AND REG_NUM=? AND A_REG_NUM=? AND KOD1_23=?
                                     AND KOD2_23=? AND KOD3_23=? AND KOD4_23=? AND KOD5_23=? AND KOD6_23=? AND KOD7_23=? AND KOD8_23=?
                                     AND KOD9_23=? AND KOD10_23=? AND KOD11_23=? AND KOD12_23=? AND STG_BEGIN=? AND STG_END=? AND ILS_DATE=? """
                    rows = self.isRecordNewCheck(sqlStmtCheck, snils, reg_num,a_reg_num, kod1_23,kod2_23,kod3_23,kod4_23,kod5_23,kod6_23,kod7_23,kod8_23,
                                                 kod9_23,kod10_23,kod11_23,kod12_23, stg_begin, stg_end, ils_date)
                    #dat_meropr = row['DAT_MEROPR']
                    #if dat_meropr == '':
                    #    dat_meropr = None
                    #rows=0


                    # ##// 'Нашёл!!!!'
                    if rows > 0:


                        returnCode = False
                        sqlStmtUpd = ""
                        sqlStmtUpd = """UPDATE DB2ADMIN.SVR_DT_LGOT_1723 set NEWREC=1, DAT_LOAD=?  where SNILS=? and REG_NUM=? and A_REG_NUM=? AND KOD1_23=?
                                     AND KOD2_23=? AND KOD3_23=? AND KOD4_23=? AND KOD5_23=? AND KOD6_23=? AND KOD7_23=? AND KOD8_23=?
                                     AND KOD9_23=? AND KOD10_23=? AND KOD11_23=? AND KOD12_23=? AND STG_BEGIN=? AND STG_END=? AND ILS_DATE=? """
                        if not self.SqlStmt(sqlStmtUpd,self.datload,snils,reg_num,a_reg_num, kod1_23,kod2_23,kod3_23,kod4_23,kod5_23,kod6_23,kod7_23,kod8_23,
                                                 kod9_23,kod10_23,kod11_23,kod12_23, stg_begin, stg_end, ils_date):

                            message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        notload = notload + 1
                        self.textEdit.append('not loaded, record exist: ' + str(notload))

                        app.processEvents()


                        #####################################
                    # не нашел, добавляем
                    if rows == 0:





                        inn = str(row["INN"]).zfill(10)

                        full_name = str(row["FULL_NAME"])




                        dat_snyat = row['DAT_SNYAT']
                        if dat_snyat == '':
                            dat_snyat = None

                        fio = str(row["FIO"])
                        kpp = str(row["KPP"])
                        a_kpp = str(row["A_KPP"])

                        status_ils = str(row["STATUS_ILS"])

                        stg_type = str(row["STG_TYPE"])

                        d_date = row['D_DATE']
                        if d_date == '':
                            d_date = None

                        kateg = str(row["KATEG"])
                        kod_snyat = str(row["KOD_SNYAT"])
                        a_name = str(row["A_NAME"])
                        ainn = str(row["AINN"])
                        a_adress = str(row["A_ADRESS"])


                        nspis = 1
                        # для первого списка 1 затем только для новых
                        inuved = 1
                        newrec = 1
                        sqlStatement = """INSERT INTO SVR_DT_LGOT_1723 (SNILS, FIO, STATUS_ILS, D_DATE,  REG_NUM, FULL_NAME, INN,
                                      DAT_SNYAT, A_REG_NUM,A_DPTCOD,
                                      STG_TYPE, ILS_DATE, STG_BEGIN,  STG_END, KOD1_23, KOD2_23, KOD3_23,
                                     KOD4_23, KOD5_23, KOD6_23, KOD7_23, KOD8_23, KOD9_23, KOD10_23,
                                     KOD11_23, KOD12_23,DAT_LOAD, KPP,A_KPP, DPTCOD, KATEG, KOD_SNYAT, A_NAME, AINN, A_ADRESS, DECM23,NOV23,SEP23,OKT23,AUG23,
                                     JUL23,JUN23,MAY23, APR23,MAR23,FEB23,JAN23,NSPIS,NEWREC) 
                                     VALUES (?,?,?,? ,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement, snils, fio, status_ils, d_date,  reg_num, full_name, inn,
                                      dat_snyat, a_reg_num,a_dptcod,
                                      stg_type, ils_date, stg_begin,  stg_end, kod1_23, kod2_23, kod3_23,
                                     kod4_23, kod5_23, kod6_23, kod7_23, kod8_23, kod9_23, kod10_23,
                                     kod11_23, kod12_23,self.datload, kpp,a_kpp, dptcod, kateg, kod_snyat, a_name, ainn, a_adress, decm23,nov23,sep23,okt23,aug23,
                                     jul23,jun23,may23, apr23,mar23,feb23,jan23,nspis,newrec):
                            #message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            message = f"{datetime.now()} - Can't run sql stmt insert,  - № row {j}"

                            logging.info(message)

                            return
                        load = load + 1
                        self.textEdit.append('loaded, new record: ' + str(load))
                        app.processEvents()
                self.textEdit.append('ИС Есть код ОУТ - нет доптарифа, обработано всего :' + str(
                    j) + '  из них загружено новые: ' + str(load))

                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        #    ----- ЕСТЬ  ДОПТАРИФ НЕТ  стажа  КОД ОУТ  ---------------
        ###################################################################################################################
        elif self.ListNmbr == 8:
            with (open(self.filename, 'r') as input_file):
                #col_names = ['SNILS', 'FIO', 'STATUS_ILS', 'D_DATE',  'REG_NUM', 'FULL_NAME', 'INN',
                #             'KPP', 'KATEG', 'STATUS', 'KOD_SNYAT', 'DAT_SNYAT', 'A_REG_NUM',
                #             'A_NAME', 'AINN', 'A_KPP',  'JAN23', 'FEB23', 'MAR23',
                #             'APR23', 'MAY23', 'JUN23', 'JUL23', 'AUG23', 'SEP23', 'OKT23',
                #             'NOV23', 'DECM23','DATE_UV','KOD_L','KOD_P','KOD_U','KOD_RSV','KOD_RAZ','KOD_NO','COMMENT1','COMMENT','DAT_PR_RSV','KOD_ISK']
                col_names = ['SNILS', 'FIO', 'STATUS_ILS', 'D_DATE',  'REG_NUM', 'FULL_NAME', 'INN',
                             'KPP', 'KATEG', 'STATUS', 'KOD_SNYAT', 'DAT_SNYAT', 'A_REG_NUM',
                             'A_NAME', 'AINN', 'A_KPP', 'YER', 'JAN23', 'FEB23', 'MAR23',
                             'APR23', 'MAY23', 'JUN23', 'JUL23', 'AUG23', 'SEP23', 'OKT23',
                             'NOV23', 'DECM23']


                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                ##########################################
                # // Отметим  все звписи  как старые
                sqlStmtUpd = 'update DB2ADMIN.SVR_DT_LGOT_OBR23 set newrec=0'
                if not self.GetRecordasOld(sqlStmtUpd):
                    return
                returnCode = False

                fields=[]
                fields = next(csvFile)
                #my_list = ['5', 'х', 'X', 'ИЛС не требует отработки']

                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append('all: ' +str(j))
                    self.textEdit.update()
                    app.processEvents()
                    snils = str(row["SNILS"])
                    snils = snils.replace('-', '')
                    snils = snils[0:9]
                    snils = int(snils)
                    inn = str(row["INN"]).zfill(10)
                    yer=int(row['YER'])
                    if yer!=2023:
                        self.textEdit.append('Не 2023 год смотри что грузиш')
                        return
                    reg_num = int(row['REG_NUM'])

                    kod1_23 = ''
                    kod2_23 = ''
                    kod3_23 = ''
                    kod4_23 = ''
                    kod5_23 = ''
                    kod6_23 = ''
                    kod7_23 = ''
                    kod8_23 = ''
                    kod9_23 = ''
                    kod10_23 = ''
                    kod11_23 = ''
                    kod12_23 = ''
                    jan23 = None
                    feb23 = None
                    mar23 = None
                    apr23 = None
                    may23 = None
                    jun23 = None
                    jul23 = None
                    aug23 = None
                    sep23 = None
                    okt23 = None
                    nov23 = None
                    decm23 = None
                    if row['JAN23']:
                        parts = row['JAN23'].split(' ')
                        if len(parts) >= 1:
                            jan23 = parts[0]
                            if len(parts) >= 2:
                                kod1_23 = parts[1]
                            else:
                                kod1_23 = 'нет'
                    if row['FEB23']:
                        parts = row['FEB23'].split(' ')
                        if len(parts) >= 1:
                            feb23 = parts[0]
                            if len(parts) >= 2:
                                kod2_23 = parts[1]
                            else:
                                kod2_23 = 'нет'

                    if row['MAR23']:
                        parts = row['MAR23'].split(' ')
                        if len(parts) >= 1:
                            mar23 = parts[0]
                            if len(parts) >= 2:
                                kod3_23 = parts[1]
                            else:
                                kod3_23 = 'нет'

                    if row['APR23']:
                        parts = row['APR23'].split(' ')
                        if len(parts) >= 1:
                            apr23 = parts[0]
                            if len(parts) >= 2:
                                kod4_23 = parts[1]
                            else:
                                kod4_23 = 'нет'

                    if row['MAY23']:
                        parts = row['MAY23'].split(' ')
                        if len(parts) >= 1:
                            may23 = parts[0]
                            if len(parts) >= 2:
                                kod5_23 = parts[1]
                            else:
                                kod5_23 = 'нет'

                    if row['JUN23']:
                        parts = row['JUN23'].split(' ')
                        if len(parts) >= 1:
                            jun23 = parts[0]
                            if len(parts) >= 2:
                                kod6_23 = parts[1]
                            else:
                                kod6_23 = 'нет'

                    if row['JUL23']:
                        parts = row['JUL23'].split(' ')
                        if len(parts) >= 1:
                            jul23 = parts[0]
                            if len(parts) >= 2:
                                kod7_23 = parts[1]
                            else:
                                kod7_23 = 'нет'

                    if row['AUG23']:
                        parts = row['AUG23'].split(' ')
                        if len(parts) >= 1:
                            aug23 = parts[0]
                            if len(parts) >= 2:
                                kod8_23 = parts[1]
                            else:
                                kod8_23 = 'нет'

                    if row['SEP23']:
                        parts = row['SEP23'].split(' ')
                        if len(parts) >= 1:
                            sep23 = parts[0]
                            if len(parts) >= 2:
                                kod9_23 = parts[1]
                            else:
                                kod9_23 = 'нет'

                    if row['OKT23']:
                        parts = row['OKT23'].split(' ')
                        if len(parts) >= 1:
                            okt23 = parts[0]
                            if len(parts) >= 2:
                                kod10_23 = parts[1]
                            else:
                                kod10_23 = 'нет'

                    if row['NOV23']:
                        parts = row['NOV23'].split(' ')
                        if len(parts) >= 1:
                            nov23 = parts[0]
                            if len(parts) >= 2:
                                kod11_23 = parts[1]
                            else:
                                kod11_23 = 'нет'

                    if row['DECM23']:
                        parts = row['DECM23'].split(' ')
                        if len(parts) >= 1:
                            decm23 = parts[0]
                            if len(parts) >= 2:
                                kod12_23 = parts[1]
                            else:
                                kod12_23 = 'нет'
                    sqlStmtCheck = """SELECT * FROM DB2ADMIN.SVR_DT_LGOT_OBR23 WHERE SNILS=? and REG_NUM=? and INN=? and KOD1_23=? and KOD2_23=? and KOD3_23=? and KOD4_23=? and KOD5_23=? and KOD6_23=? and KOD7_23=? and KOD8_23=? and  KOD9_23=? and KOD10_23=? and KOD11_23=? and KOD12_23=? """
                    ##########################################################
                    # // проверка есть запись?
                    if jan23:
                        sqlStmtCheck = sqlStmtCheck + """ and JAN23=?"""
                    if feb23:
                        sqlStmtCheck = sqlStmtCheck + """ and FEB23=?"""
                    if mar23:
                        sqlStmtCheck = sqlStmtCheck + """ and MAR23=?"""
                    if apr23:
                        sqlStmtCheck = sqlStmtCheck + """ and APR23=?"""
                    if may23:
                       sqlStmtCheck = sqlStmtCheck + """ and MAY23=?"""
                    if jun23:
                        sqlStmtCheck = sqlStmtCheck + """ and JUN23=?"""
                    if jul23:
                        sqlStmtCheck = sqlStmtCheck + """ and JUL23=?"""
                    if aug23:
                        sqlStmtCheck = sqlStmtCheck + """ and AUG23=?"""
                    if sep23:
                        sqlStmtCheck = sqlStmtCheck + """ and SEP23=?"""
                    if okt23:
                        sqlStmtCheck = sqlStmtCheck + """ and OKT23=?"""
                    if nov23:
                        sqlStmtCheck = sqlStmtCheck + """ and NOV23=?"""
                    if decm23:
                        sqlStmtCheck = sqlStmtCheck + """ and DECM23=?"""

                    rows = self.null_check(sqlStmtCheck, snils, reg_num, inn,kod1_23,kod2_23,kod3_23,kod4_23,kod5_23,kod6_23,kod7_23, kod8_23,kod9_23, kod10_23,kod11_23,kod12_23, jan23,feb23,mar23,apr23,may23,jun23,jul23,aug23,sep23,okt23,nov23,decm23)



                    # ##// 'Нашёл!!!!'
                    #
                    if rows > 0:


                        returnCode = False



                        sqlStmtUpd = "update DB2ADMIN.SVR_DT_LGOT_OBR23 set NEWREC=1, DAT_LOAD=?  WHERE SNILS=? and REG_NUM=? and INN=? and KOD1_23=? and KOD2_23=? and KOD3_23=? and KOD4_23=? and KOD5_23=? and KOD6_23=? and KOD7_23=? and KOD8_23=? and  KOD9_23=? and KOD10_23=? and KOD11_23=? and KOD12_23=? "

                        if jan23:
                            sqlStmtUpd = sqlStmtUpd + """ and JAN23=?"""
                        if feb23:
                            sqlStmtUpd = sqlStmtUpd + """ and FEB23=?"""
                        if mar23:
                            sqlStmtUpd = sqlStmtUpd + """ and MAR23=?"""
                        if apr23:
                            sqlStmtUpd = sqlStmtUpd + """ and APR23=?"""
                        if may23:
                            sqlStmtUpd = sqlStmtUpd + """ and MAY23=?"""
                        if jun23:
                            sqlStmtUpd = sqlStmtUpd + """ and JUN23=?"""
                        if jul23:
                            sqlStmtUpd = sqlStmtUpd + """ and JUL23=?"""
                        if aug23:
                            sqlStmtUpd = sqlStmtUpd + """ and AUG23=?"""
                        if sep23:
                            sqlStmtUpd = sqlStmtUpd + """ and SEP23=?"""
                        if okt23:
                            sqlStmtUpd = sqlStmtUpd + """ and OKT23=?"""
                        if nov23:
                            sqlStmtUpd = sqlStmtUpd + """ and NOV23=?"""
                        if decm23:
                            sqlStmtUpd = sqlStmtUpd + """ and DECM23=?"""

                        if not self.null_check_upd(sqlStmtUpd,self.datload, snils, reg_num, inn, kod1_23,kod2_23,kod3_23,kod4_23,kod5_23,kod6_23,kod7_23, kod8_23,kod9_23, kod10_23,kod11_23,kod12_23,jan23, feb23, mar23, apr23, may23, jun23,
                                                   jul23, aug23, sep23, okt23, nov23, decm23):
                            message = f"{datetime.now()} - - № row {j}"
                            logging.info(message)
                            return
                        notload = notload + 1
                        self.textEdit.append('not loaded, record exist: ' + str(notload))
                        app.processEvents()
                        # if not self.SqlStmt(sqlStmtUpd, self.datload, snils, reg_num, inn):
                        #     message = f"{datetime.now()} - - № row {j}"
                        #     logging.info(message)
                        #     return

                        #####################################
                    # не нашел, добавляем
                    if rows == 0:



                        dptcod = str(reg_num)
                        dptcod = dptcod.zfill(12)
                        dptcod = dptcod[0:6]
                        dptcod = int(dptcod)
                        reg_num = int(reg_num)
                        kpp = str(row["KPP"])
                        inn = str(row["INN"]).zfill(10)
                        full_name = str(row["FULL_NAME"])
                        kod_snyat = str(row["KOD_SNYAT"])
                        dat_snyat = row['DAT_SNYAT']
                        if dat_snyat == '':
                            dat_snyat = None
                        kateg = str(row["KATEG"])
                        status = str(row["STATUS"])

                        a_reg_num = row["A_REG_NUM"]
                        if a_reg_num:
                            a_dptcod = str(a_reg_num)
                            a_dptcod = a_dptcod.zfill(12)
                            a_dptcod = a_dptcod[0:6]
                            a_dptcod = int(a_dptcod)
                            a_reg_num = int(a_reg_num)
                        else:
                            a_reg_num=None
                            a_dptcod=None

                        a_kpp = str(row["A_KPP"])
                        a_name = str(row["A_NAME"])
                        ainn = str(row["AINN"])

                        fio = str(row["FIO"])
                        d_date = row['D_DATE']
                        if d_date == '':
                            d_date = None
                        status_ils = str(row["STATUS_ILS"])

                        nspis = 1
                        # для первого списка 1 затем только для новых
                        inuved = 1
                        newrec = 1


                        sqlStatement = """INSERT INTO SVR_DT_LGOT_OBR23 (SNILS, FIO, STATUS_ILS, D_DATE,  REG_NUM, FULL_NAME, INN,
                                      KPP, KATEG, STATUS, KOD_SNYAT,DAT_SNYAT, A_REG_NUM,A_DPTCOD,
                                      A_NAME, AINN, A_KPP, JAN23, FEB23, MAR23,
                                     APR23, MAY23, JUN23, JUL23, AUG23, SEP23, OKT23,
                                     NOV23, DECM23, DPTCOD,NSPIS,DAT_LOAD,KOD1_23,KOD2_23,KOD3_23,KOD4_23,KOD5_23,KOD6_23,KOD7_23,KOD8_23,KOD9_23,KOD10_23,KOD11_23,KOD12_23,NEWREC) 
                                     VALUES (?,?,?,? ,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement, snils, fio, status_ils, d_date,  reg_num, full_name, inn,
                                      kpp, kateg, status, kod_snyat,dat_snyat, a_reg_num,a_dptcod,
                                      a_name, ainn, a_kpp, jan23, feb23, mar23,
                                     apr23, may23, jun23, jul23, aug23, sep23, okt23,
                                     nov23, decm23, dptcod,nspis,self.datload,kod1_23,kod2_23,kod3_23,kod4_23,kod5_23,kod6_23,kod7_23,kod8_23,kod9_23,kod10_23,kod11_23,kod12_23,newrec):
                            message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            message = f"{datetime.now()} - Can't run sql stmt insert,  - № row {j}"

                            logging.info(message)

                            return
                        load = load + 1
                        self.textEdit.append('loaded, new record: ' + str(load))
                        app.processEvents()
                self.textEdit.append('Есть доптариф за 2023 нет код оут..., обработано всего :' + str(
                    j) + '  из них загружено новые: ' + str(load))

                QApplication.restoreOverrideCursor()

        ###################################################################################################################
        #                -budg plan---
        ###################################################################################################################
        elif self.ListNmbr == 9:
            with open(self.filename, 'r') as input_file:
                col_names = ['ENTNMB' ]
                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')

                returnCode = False
                fields = []
                fields = next(csvFile)
                j=0
                load=0
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append(str(j))
                    self.textEdit.update()
                    app.processEvents()

                    entnmb = row["ENTNMB"]
                    dptcod = str(entnmb)
                    dptcod = dptcod.zfill(12)
                    dptcod = dptcod[0:6]
                    dptcod = int(dptcod)
                    entnmb = int(entnmb)
                    yer = 2025
                    mon = 8


                    rows=0


                    if rows == 0:
                        load = load + 1
                        nspis = 1
                        newrec = 1
                        sqlStatement = """INSERT INTO DB2ADMIN.SVR_SZV_BUDG (DPTCOD,ENTNMB, YER,  MON,DAT_LOAD) VALUES (?, ?, ?, ?,?)"""
                        if not self.SqlStmt(sqlStatement, dptcod, entnmb, yer, mon, self.datload):
                            # message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            message = f"{datetime.now()} - Can't run sql stmt insert, - № row {j}"

                            logging.info(message)

                            return
                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        #    ----- Есть КМ прием нет увольнения нет рсчета за следующие периоды 6 список ---------------
        ###################################################################################################################
        elif self.ListNmbr == 10:
            with (open(self.filename, 'r') as input_file):
                #col_names = ['ENTNMB','ACTUAL_ENTNMB','DPTCOD','PISMO','SNAT','INN','KPP',
                #             'NAME_ORG','KATEG', 'STATUS', 'KOD_SNYAT', 'DAT_SNYAT', 'FIO','SNILS',
                #             'STATUS_ILS','R_DATE','DAT_MEROPR','MEROPR','KOD_OKZ','DOC_N','DOC_DAT','UUID',
                #             'FO_NUM','FO_DAT_TXT','RSV_YER','RSV_KVART','RSV_MON','DATE_UV','KOD_L','KOD_P','KOD_U','KOD_RSV','KOD_RAZ','KOD_NO','COMMENT1','COMMENT','DAT_PR_RSV','KOD_ISK']

                col_names = ['ENTNMB','INN','KPP',
                             'NAME_ORG','KATEG', 'STATUS', 'KOD_SNYAT', 'DAT_SNYAT', 'FIO','SNILS',
                             'STATUS_ILS','R_DATE','DAT_MEROPR','MEROPR','KOD_OKZ','DOC_N','DOC_DAT','UUID',
                             'FO_NUM','FO_DAT_TXT','RSV_YER','RSV_KVART','RSV_MON']



                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                ##########################################
                # // Отметим  все звписи  как старые
                sqlStmtUpd = 'update DB2ADMIN.SVR_NOKM_NOFNS set newrec=0'
                if not self.GetRecordasOld(sqlStmtUpd):
                    return
                returnCode = False

                fields = []
                fields = next(csvFile)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append('all: ' + str(j))
                    self.textEdit.update()
                    app.processEvents()

                    ##########################################################

                    #my_list = ['5', 'х', 'X', 'ИЛС не требует отработки']
                    #res_notwork = None
                    #res_work = None
                    #res = None
                    uuid = str(row["UUID"])
                    fo_num = str(row["FO_NUM"])
                    sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_NOKM_NOFNS WHERE UUID=? and FO_NUM=? '
                    rows = self.isRecordNewCheck(sqlStmtCheck, uuid, fo_num)
                    #date_uv = row['DATE_UV']
                    #if date_uv and date_uv !='п' :
                    #    res = 1
                    #    res_work = 1
                    #else:
                    #    date_uv = None
                    #comment = str(row['COMMENT'])
                    #comment1 = str(row['COMMENT1'])

                    #kod_l = str(row['KOD_L'])

                    #kod_p = str(row['KOD_P'])
                    #kod_u = str(row['KOD_U'])
                    #kod_rsv = str(row['KOD_RSV'])
                    #if kod_rsv:
                    #    res = 2

                    #    res_work = None
                    #    res_notwork = None
                    #kod_raz = str(row['KOD_RAZ'])

                    #kod_no = str(row['KOD_NO'])
                    #if kod_no in my_list:
                    #    res = 4
                    #    res_notwork = 5
                    #    res_work = None

                    #kod_raz = str(row['KOD_RAZ'])


                    #dat_pr_rsv = row['DAT_PR_RSV']
                    #if dat_pr_rsv == '':
                    #    dat_pr_rsv = None

                    #kod_isk = str(row['KOD_ISK'])




                    # ##// 'Нашёл!!!!'

                    if rows > 0:


                        returnCode = False
                        sqlStmtUpd = ""
                        sqlStmtUpd = "update DB2ADMIN.SVR_NOKM_NOFNS set NEWREC=1, DAT_LOAD=? where UUID=? and FO_NUM=?"
                        if not self.SqlStmt(sqlStmtUpd, self.datload,  uuid,fo_num):
                            message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        notload = notload + 1
                        self.textEdit.append('not loaded, record exist: ' + str(notload))
                        self.textEdit.update()
                        app.processEvents()

                        #####################################
                    # не нашел, добавляем
                    if rows == 0:


                        entnmb =int(row["ENTNMB"])
                        #dptcod= int(row["DPTCOD"])

                        dptcod = str(entnmb)
                        dptcod = dptcod.zfill(12)
                        dptcod = dptcod[0:6]
                        dptcod = int(dptcod)
                        entnmb = int( entnmb)



                        #actual_entnmb = row["ACTUAL_ENTNMB"]
                        #if actual_entnmb:
                        #    actual_dptcod = str(actual_entnmb)
                        #    actual_dptcod = actual_dptcod.zfill(12)
                        #    actual_dptcod = actual_dptcod[0:6]
                        #    actual_dptcod = int(actual_dptcod)
                        #    actual_entnmb = int(actual_entnmb)
                        #else:
                        #    actual_entnmb = None
                        #    actual_dptcod = None


                        kpp = str(row["KPP"])
                        inn = str(row["INN"]).zfill(10)
                        name_org = str(row["NAME_ORG"])



                        kod_snyat = str(row["KOD_SNYAT"])

                        dat_snyat = row['DAT_SNYAT']
                        if dat_snyat=='':
                            dat_snyat = None

                        kateg = str(row["KATEG"])
                        status = str(row["STATUS"])

                        fo_dat_txt = str(row["FO_DAT_TXT"])
                        meropr = str(row["MEROPR"])

                        dat_meropr = row["DAT_MEROPR"]
                        if dat_meropr=='':
                            dat_meropr = None

                        doc_n = str(row["DOC_N"])

                        doc_dat = row["DOC_DAT"]
                        if doc_dat=='':
                            doc_dat = None





                        snils = str(row["SNILS"])
                        insnmb = snils.replace('-', '')

                        insnmb = insnmb[0:9]
                        insnmb = int(insnmb)

                        fio = str(row["FIO"])

                        r_date = row['R_DATE']
                        if r_date=='':
                            r_date = None

                        status_ils = str(row["STATUS_ILS"])
                        rsv_yer = str(row["RSV_YER"])
                        if rsv_yer=='':
                            rsv_yer = None
                        else:
                            rsv_yer = int(rsv_yer)

                        rsv_kvart = str(row["RSV_KVART"])
                        if rsv_kvart=='':
                            rsv_kvart = None
                        else:
                            rsv_kvart = int(rsv_kvart)

                        rsv_mon = str(row["RSV_MON"])
                        if rsv_mon=='':
                            rsv_mon = None
                        else:
                            rsv_mon=int(rsv_mon)

                        kod_okz = row["KOD_OKZ"]

                       


                        nspis = 1
                        # для первого списка 1 затем только для новых
                        inuved = 1
                        newrec = 1

                        sqlStatement = """INSERT INTO SVR_NOKM_NOFNS (ENTNMB, DPTCOD, INN, KPP,
                                    NAME_ORG, KATEG, STATUS, KOD_SNYAT, DAT_SNYAT, FIO, SNILSCS,
                                    STATUS_ILS, R_DATE, DAT_MEROPR, MEROPR, KOD_OKZ, DOC_N, DOC_DAT,
                                    UUID, FO_NUM, FO_DAT_TXT, RSV_YER, RSV_KVART, RSV_MON,INSNMB,DAT_LOAD,NSPIS,NEWREC,IN_UVED)
                                        VALUES (?,?,?,? ,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement, entnmb,  dptcod, inn, kpp,
                                           name_org, kateg, status, kod_snyat, dat_snyat, fio, snils,
                                           status_ils, r_date, dat_meropr, meropr, kod_okz, doc_n, doc_dat,
                                           uuid, fo_num, fo_dat_txt, rsv_yer, rsv_kvart, rsv_mon, insnmb,
                                           self.datload,nspis,newrec,inuved):

                            # message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            message = f"{datetime.now()} - Can't run sql stmt insert,  - № row {j}"

                            logging.info(message)

                            return
                        load = load + 1
                        self.textEdit.append('loaded, new record: ' + str(load))
                        self.textEdit.update()
                        app.processEvents()
                self.textEdit.append('Есть КМ прием нет увольнения нет рсчета за следующие..., обработано всего :' + str(
                    j) + '  из них загружено новые: ' + str(load))

                QApplication.restoreOverrideCursor()

        ###################################################################################################################
        #    ----- Педагоги, медики ---------------
        ###################################################################################################################
        elif self.ListNmbr == 11:
            with (open(self.filename, 'r') as input_file):
                col_names = ['SNILS', 'FIO', 'STATUS_ILS', 'D_DATE',  'REG_NUM', 'FULL_NAME', 'INN',
                             'KPP', 'KATEG', 'STATUS', 'KOD_SNYAT', 'DAT_SNYAT', 'A_REG_NUM',
                             'A_NAME', 'AINN', 'A_KPP',
                             'JAN', 'FEB', 'MAR',
                             'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OKT',
                             'NOV', 'DECM','DATE_KM','TIP_KM','UUID','FO_NUM','FO_DAT']
                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                ##########################################
                # // Отметим  все звписи  как старые
                yer = int(self.yerPedMed)

                sqlStmtUpd = 'update DB2ADMIN.SVR_DT_MEDPED set newrec=0 where yer=? '
                if not self.GetRecordasOld(sqlStmtUpd,yer):
                    return
                returnCode = False

                fields = []
                fields = next(csvFile)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append('all: ' + str(j))
                    app.processEvents()

                    ##########################################################
                    # //
                    reg_num = row["REG_NUM"]
                    uuid = row["UUID"]
                    fo_num = row["FO_NUM"]

                    snils = str(row["SNILS"])
                    snils = snils.replace('-', '')
                    snils = snils[0:9]
                    snils = int(snils)
                    dptcod = str(reg_num)
                    dptcod = dptcod.zfill(12)
                    dptcod = dptcod[0:6]
                    dptcod = int(dptcod)
                    reg_num = int(reg_num)
                    inn = str(row["INN"]).zfill(10)

                    a_reg_num = row["A_REG_NUM"]
                    ainn = str(row["AINN"])

                    kpp = str(row["KPP"])
                    a_kpp = str(row["A_KPP"])

                    a_dptcod = str(a_reg_num)
                    a_dptcod = a_dptcod.zfill(12)
                    a_dptcod = a_dptcod[0:6]
                    a_dptcod = int(a_dptcod)
                    a_reg_num = int(a_reg_num)
                    d_date = row['D_DATE']
                    if d_date == '':
                        d_date = None

                    jan = str(row["JAN"])
                    feb = str(row["FEB"])
                    mar = str(row["MAR"])
                    apr = str(row["APR"])
                    may = str(row["MAY"])
                    jun = str(row["JUN"])
                    jul = str(row["JUL"])
                    aug = str(row["AUG"])
                    sep = str(row["SEP"])
                    okt = str(row["OKT"])
                    nov = str(row["NOV"])
                    decm = str(row["DECM"])


                    if uuid:
                        sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_DT_MEDPED WHERE UUID=? and FO_NUM=?'
                        rows = self.isRecordNewCheck(sqlStmtCheck, uuid, fo_num)

                    else:
                        sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_DT_MEDPED WHERE SNILS=? and REG_NUM=? and INN=? and  KPP=? and  A_REG_NUM=? and AINN=? and  A_KPP=? and YER=? and JAN=? and FEB=? and MAR=? and APR=? and MAY=? and JUN=? and JUL=? and AUG=? and SEP=? and OKT=? and NOV=? and DECM=?'
                        rows = self.isRecordNewCheck(sqlStmtCheck, snils, reg_num, inn, kpp, a_reg_num, ainn, a_kpp,yer,jan, feb, mar, apr, may, jun,jul, aug, sep,okt, nov, decm )

                        # dat_meropr = row['DAT_MEROPR']
                    # if dat_meropr == '':
                    #    dat_meropr = None
                    # rows=0

                    # ##// 'Нашёл!!!!'
                    if rows > 0:


                        returnCode = False
                        sqlStmtUpd = ""
                        sqlStmtUpd = "update SVR_DT_MEDPED set NEWREC=1, DAT_LOAD=?  where UUID=? and FO_NUM=?"
                        if not self.SqlStmt(sqlStmtUpd, self.datload, uuid, fo_num):
                            message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        notload = notload + 1
                        self.textEdit.append('not loaded, record exist: ' + str(notload))
                        app.processEvents()
                        #####################################
                    # не нашел, добавляем
                    if rows == 0:
                        full_name = str(row["FULL_NAME"])
                        dat_snyat = row['DAT_SNYAT']
                        if dat_snyat == '':
                            dat_snyat = None
                        fio = str(row["FIO"])
                        status_ils = str(row["STATUS_ILS"])
                        status = str(row["STATUS"])
                        kateg = str(row["KATEG"])
                        kod_snyat = str(row["KOD_SNYAT"])
                        a_name = str(row["A_NAME"])
                        date_km = row['DATE_KM']
                        if date_km == '':
                            date_km = None
                        tip_km = row['TIP_KM']
                        fo_dat = row['FO_DAT']
                        if fo_dat == '':
                            fo_dat = None
                        nspis = 1
                        # для первого списка 1 затем только для новых
                        inuved = 1
                        newrec = 1
                        in_uved=1
                        sqlStatement = """INSERT INTO SVR_DT_MEDPED (SNILS, FIO, STATUS_ILS, D_DATE,  REG_NUM, FULL_NAME, INN,
                                          KPP,KATEG,STATUS,KOD_SNYAT,DAT_SNYAT, A_REG_NUM,A_NAME,AINN,A_KPP,
                                          JAN,FEB,MAR,APR,MAY,JUN,JUL,AUG,SEP,OKT,NOV,DECM,DATE_KM,TIP_KM,UUID,FO_NUM,FO_DAT,
                                          DAT_LOAD,  DPTCOD, NSPIS,NEWREC,A_DPTCOD,YER,IN_UVED) 
                                         VALUES (?,?,?,? ,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement, snils, fio, status_ils, d_date,  reg_num, full_name, inn,
                                          kpp,kateg,status,kod_snyat,dat_snyat, a_reg_num,a_name,ainn,a_kpp,
                                          jan,feb,mar,apr,may,jun,jul,aug,sep,okt,nov,decm,date_km,tip_km,uuid,fo_num,fo_dat,
                                          self.datload,  dptcod, nspis,newrec,a_dptcod,self.yerPedMed,in_uved):
                            # message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            message = f"{datetime.now()} - Can't run sql stmt insert,  - № row {j}"

                            logging.info(message)

                            return
                        else:
                            message = f"{datetime.now()} - done  - № row {j}"

                            logging.info(message)

                        load = load + 1
                        self.textEdit.append('loaded, new record: ' + str(load))
                        app.processEvents()
                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        ###################################################################################################################
        #    ----- МКС РКС ---------------
        ###################################################################################################################
        elif self.ListNmbr == 12:
            with (open(self.filename, 'r') as input_file):
                col_names = ['SNILS', 'FIO', 'STATUS_ILS', 'D_DATE', 'REG_NUM', 'FULL_NAME', 'INN',
                             'KPP', 'KATEG', 'STATUS', 'KOD_SNYAT', 'DAT_SNYAT', 'A_REG_NUM',
                             'A_NAME', 'AINN', 'A_KPP',
                             'TIP_KM','KOD_RKSMKS','DATE_KM','DOLG','KOD_OKZ',
                             'FO_NUM', 'FO_DAT', 'UUID',
                             'JAN', 'FEB', 'MAR',
                             'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OKT',
                             'NOV', 'DECM' ]
                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                ##########################################
                # // Отметим  все звписи  как старые
                yer = int(self.yerPedMed)

                sqlStmtUpd = 'update DB2ADMIN.SVR_DT_MKSRKS set newrec=0 where yer=? '
                if not self.GetRecordasOld(sqlStmtUpd, yer):
                    return
                returnCode = False

                fields = []
                fields = next(csvFile)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append('all: ' + str(j))
                    app.processEvents()

                    ##########################################################
                    # //
                    reg_num = row["REG_NUM"]
                    uuid = row["UUID"]
                    fo_num = row["FO_NUM"]

                    snils = str(row["SNILS"])
                    snils = snils.replace('-', '')
                    snils = snils[0:9]
                    snils = int(snils)
                    dptcod = str(reg_num)
                    dptcod = dptcod.zfill(12)
                    dptcod = dptcod[0:6]
                    dptcod = int(dptcod)
                    reg_num = int(reg_num)
                    inn = str(row["INN"]).zfill(10)

                    a_reg_num = row["A_REG_NUM"]
                    ainn = str(row["AINN"])

                    kpp = str(row["KPP"])
                    a_kpp = str(row["A_KPP"])

                    a_dptcod = str(a_reg_num)
                    a_dptcod = a_dptcod.zfill(12)
                    a_dptcod = a_dptcod[0:6]
                    a_dptcod = int(a_dptcod)
                    a_reg_num = int(a_reg_num)
                    d_date = row['D_DATE']
                    if d_date == '':
                        d_date = None

                    jan = str(row["JAN"])
                    feb = str(row["FEB"])
                    mar = str(row["MAR"])
                    apr = str(row["APR"])
                    may = str(row["MAY"])
                    jun = str(row["JUN"])
                    jul = str(row["JUL"])
                    aug = str(row["AUG"])
                    sep = str(row["SEP"])
                    okt = str(row["OKT"])
                    nov = str(row["NOV"])
                    decm = str(row["DECM"])

                    if uuid:
                        sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_DT_MKSRKS WHERE UUID=? and FO_NUM=?'
                        rows = self.isRecordNewCheck(sqlStmtCheck, uuid, fo_num)

                    else:
                        sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_DT_MKSRKS WHERE SNILS=? and REG_NUM=? and INN=? and  KPP=? and  A_REG_NUM=? and AINN=? and  A_KPP=? and YER=? and JAN=? and FEB=? and MAR=? and APR=? and MAY=? and JUN=? and JUL=? and AUG=? and SEP=? and OKT=? and NOV=? and DECM=?'
                        rows = self.isRecordNewCheck(sqlStmtCheck, snils, reg_num, inn, kpp, a_reg_num, ainn, a_kpp,
                                                     yer, jan, feb, mar, apr, may, jun, jul, aug, sep, okt, nov,
                                                     decm)

                        # dat_meropr = row['DAT_MEROPR']
                    # if dat_meropr == '':
                    #    dat_meropr = None
                    # rows=0

                    # ##// 'Нашёл!!!!'
                    if rows > 0:

                        returnCode = False
                        sqlStmtUpd = ""
                        sqlStmtUpd = "update SVR_DT_MKSRKS set NEWREC=1, DAT_LOAD=?  where UUID=? and FO_NUM=?"
                        if not self.SqlStmt(sqlStmtUpd, self.datload, uuid, fo_num):
                            message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        notload = notload + 1
                        self.textEdit.append('not loaded, record exist: ' + str(notload))
                        app.processEvents()
                        #####################################
                    # не нашел, добавляем
                    if rows == 0:
                        full_name = str(row["FULL_NAME"])
                        dat_snyat = row['DAT_SNYAT']
                        if dat_snyat == '':
                            dat_snyat = None
                        fio = str(row["FIO"])
                        status_ils = str(row["STATUS_ILS"])
                        status = str(row["STATUS"])
                        kateg = str(row["KATEG"])
                        kod_snyat = str(row["KOD_SNYAT"])
                        a_name = str(row["A_NAME"])
                        date_km = row['DATE_KM']
                        if date_km == '':
                            date_km = None
                        tip_km = row['TIP_KM']
                        fo_dat = row['FO_DAT']
                        if fo_dat == '':
                            fo_dat = None
                        dolg = row['DOLG']
                        kod_okz = row['KOD_OKZ']
                        kod_rksmks = row['KOD_RKSMKS']

                        nspis = 1
                        # для первого списка 1 затем только для новых
                        inuved = 1
                        newrec = 1
                        in_uved = 1



                        sqlStatement = """INSERT INTO SVR_DT_MKSRKS (SNILS, FIO, STATUS_ILS, D_DATE,  REG_NUM, FULL_NAME, INN,
                                                  KPP,KATEG,STATUS,KOD_SNYAT,DAT_SNYAT, A_REG_NUM,A_NAME,AINN,A_KPP,
                                                  TIP_KM, KOD_RKSMKS, DATE_KM, DOLG, KOD_OKZ,FO_NUM,FO_DAT,UUID,
                                                  JAN,FEB,MAR,APR,MAY,JUN,JUL,AUG,SEP,OKT,NOV,DECM,
                                                  DAT_LOAD,  DPTCOD, NSPIS,NEWREC,A_DPTCOD,YER,IN_UVED) 
                                                 VALUES (?,?,?,? ,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement, snils, fio, status_ils, d_date,  reg_num, full_name, inn,
                                              kpp,kateg,status,kod_snyat,dat_snyat, a_reg_num,a_name,ainn,a_kpp,
                                              tip_km, kod_rksmks, date_km, dolg, kod_okz,fo_num,fo_dat,uuid,
                                              jan,feb,mar,apr,may,jun,jul,aug,sep,okt,nov,decm,
                                              self.datload,  dptcod, nspis,newrec,a_dptcod,self.yerPedMed,in_uved):




                            # message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            message = f"{datetime.now()} - Can't run sql stmt insert,  - № row {j}"

                            logging.info(message)

                            return
                        else:
                            message = f"{datetime.now()} - done  - № row {j}"

                            logging.info(message)

                        load = load + 1
                        self.textEdit.append('loaded, new record: ' + str(load))
                        app.processEvents()
                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        #                      ----КМ с некорректными наименованиями организаций
        ###################################################################################################################
        elif self.ListNmbr == 13:
            with open(self.filename, 'r') as input_file:

                # row_count = len([row.rstrip() for row in input_file])

                col_names = ['SNILSCS','FIO','STATUS_ILS','D_DATE','PENS','NAME_ORG','INN', 'KPP','ENTNMB','KATEG',
                             'KOD_POSTAN',  'KOD_SNYAT', 'DAT_SNYAT','FO_DAT_TXT','FO_NUM','UUID',
                             'MEROPR','DAT_MEROPR','VID_TRUD','TIP_DOGOV',
                             'ACTUAL_ENTNMB', 'A_NAME_ORG', 'A_INN', 'A_KPP']

                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                ##########################################
                # // Отметим  все звписи  как старые
                sqlStmtUpd = 'update DB2ADMIN.SVR_NAME_ORG_INCORR set newrec=0'
                if not self.GetRecordasOld(sqlStmtUpd):
                    return
                returnCode = False

                fields = []
                fields = next(csvFile)

                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append(str(j))
                    self.textEdit.update()
                    app.processEvents()

                    uuid = str(row["UUID"])

                    # uuid = str(df.loc[ind, "UUID"])
                    fo_num = str(row["FO_NUM"])

                    # fo_num = str(df.loc[ind, "FO_NUM"])
                    ##########################################################
                    # // Проверка uuid + fo_num
                    sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_NAME_ORG_INCORR WHERE  UUID=? and FO_NUM=?'
                    rows = self.isRecordNewCheck(sqlStmtCheck, uuid, fo_num)
                    dat_meropr = row['DAT_MEROPR']

                    if dat_meropr == '':
                        dat_meropr = None

                    # ##// 'Нашёл!!!!'
                    if rows > 0:
                        notload = notload + 1
                        returnCode = False
                        sqlStmtUpd = ""
                        sqlStmtUpd = "update DB2ADMIN.SVR_NAME_ORG_INCORR set NEWREC=1, DAT_MEROPR=?  where UUID=? and FO_NUM=?"
                        if not self.SqlStmt(sqlStmtUpd, dat_meropr, uuid, fo_num):
                            message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        notload = notload + 1
                        self.textEdit.append('notloaded, record exist: ' + str(notload))
                        app.processEvents()
                    #####################################
                    # не нашел добавляем
                    if rows == 0:

                        entnmb = row["ENTNMB"]

                        dptcod = str(entnmb)
                        dptcod = dptcod.zfill(12)
                        dptcod = dptcod[0:6]
                        dptcod = int(dptcod)
                        entnmb = int(entnmb)



                        name_org = str(row["NAME_ORG"])
                        a_name_org = str(row["A_NAME_ORG"])

                        actual_entnmb = row["ACTUAL_ENTNMB"]
                        actual_dptcod = str(actual_entnmb)
                        actual_dptcod = actual_dptcod.zfill(12)
                        actual_dptcod = actual_dptcod[0:6]
                        actual_dptcod = int(actual_dptcod)
                        actual_entnmb = int(actual_entnmb)

                        inn = str(row["INN"]).zfill(10)
                        kpp = str(row["KPP"]).zfill(9)
                        a_inn = str(row["A_INN"]).zfill(10)
                        a_kpp = str(row["A_KPP"]).zfill(9)

                        kateg = str(row["KATEG"]).zfill(4)
                        status_ils = str(row["STATUS_ILS"])

                        kod_snyat = row['KOD_SNYAT']
                        kod_postan = row['KOD_POSTAN']

                        dat_snyat = row['DAT_SNYAT']
                        if dat_snyat == '':
                            dat_snyat = None

                        meropr = str(row["MEROPR"])
                        dat_meropr = str(row["DAT_MEROPR"])
                        if dat_meropr == '':
                            dat_meropr = None



                        vid_trud = row['VID_TRUD']
                        tip_dogov = str(row["TIP_DOGOV"])

                        snilscs = str(row["SNILSCS"])
                        insnmb = row["SNILSCS"]
                        insnmb = insnmb.replace('-', '')
                        insnmb = insnmb[0:9]
                        insnmb = int(insnmb)
                        fio = str(row["FIO"])
                        pens = str(row["PENS"])

                        d_date = row['D_DATE']
                        if d_date == '':
                            d_date = None

                        fo_dat_txt = str(row["FO_DAT_TXT"])


                        uuid = str(row["UUID"])

                        nspis = 1
                        # для первого списка 1 затем только для новых
                        in_uved = 1
                        dat_load = date.today()
                        newrec = 1
                        sqlStatement = """INSERT INTO SVR_NAME_ORG_INCORR (DPTCOD, ENTNMB, NAME_ORG,INN, KPP, STATUS_ILS,  KOD_POSTAN, KOD_SNYAT, DAT_SNYAT,
                                           INSNMB, SNILSCS,  FIO,  FO_DAT_TXT, FO_NUM, UUID, MEROPR, DAT_MEROPR, VID_TRUD, TIP_DOGOV, ACTUAL_ENTNMB, ACTUAL_DPTCOD, 
                                           A_INN,A_KPP, NSPIS , IN_UVED, DAT_LOAD, NEWREC,A_NAME_ORG,PENS, KATEG )
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement, dptcod, entnmb, name_org, inn, kpp, status_ils,  kod_postan, kod_snyat, dat_snyat,
                                           insnmb, snilscs,  fio,  fo_dat_txt, fo_num, uuid, meropr, dat_meropr, vid_trud, tip_dogov, actual_entnmb, actual_dptcod,
                                           a_inn,a_kpp, nspis , in_uved, self.datload, newrec,a_name_org,pens, kateg):
                            message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        load = load + 1
                        self.textEdit.append('loaded, new record: ' + str(load))
                        app.processEvents()
                self.textEdit.append('KM, с некорректными наименованиями организаций, обработано всего :' + str(
                    j) + '  из них загружено новые: ' + str(load))

                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        ###################################################################################################################
        #                -temp_regnum_kp---
        ###################################################################################################################
        elif self.ListNmbr == 14:
            with open(self.filename, 'r') as input_file:
                #col_names = ['DPTCOD','REG','DEP','RA','138','567','2s']
                col_names = ['DPTCOD','REG','NAME','NAMEOT','NAME_DPT']

                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')

                returnCode = False
                fields = []
                fields = next(csvFile)
                j = 0
                load = 0
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append(str(j))
                    self.textEdit.update()
                    app.processEvents()
                    dptcod = row["DPTCOD"]
                    dptcod = int(dptcod)

                    reg = row["REG"]
                    reg = int(reg)
                    name = row["NAME"]

                    ## mm=1 это значит из КП без оку 6226
                    ## mm=2 это значит из КП  оку 58294

                    mm = 1
                    # mm = int(mm)
                    # ff = row["2s"]
                    # ff = int(ff)
                    rows = 0
                    if rows == 0:
                        load = load + 1
                        nspis = 1
                        newrec = 1
                        #sqlStatement = """INSERT INTO DB2ADMIN.AA_TEMP_REGNUM_KP (DPTCOD,REG,NAME) VALUES (?,?,?)"""
                        sqlStatement = """INSERT INTO DB2ADMIN.AA_TEMP_REGNUM_KP (DPTCOD,REG,MM,NAME) VALUES (?,?,?,?)"""


                        #sqlStatement = """INSERT INTO DB2ADMIN.AA_TEMP_REGNUM_KP (DPTCOD,DEP,MM,DD,FF,RA,REG) VALUES (?,?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement, dptcod,reg,mm,name):
                            # message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            message = f"{datetime.now()} - Can't run sql stmt insert, - № row {j}"

                            logging.info(message)

                            return
                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        #                      ----Есть СЗВ-М за 2021-2023 год - нет стажа 21-2022-23----------------
        ###################################################################################################################
        elif self.ListNmbr == 15:
            with open(self.filename, 'r') as input_file:

                # row_count = len([row.rstrip() for row in input_file])

                col_names = ['ENTNMB','NAME_ORG','KATEG','KOD_SNYAT', 'DAT_SNYAT','INSNMB','FIO','YEAR','SZVM_MES','STAZH_MES','FNS_MES']

                ###### здесь остановилас !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                ##########################################
                # // Отметим  все звписи  как старые
                sqlStmtUpd = 'update DB2ADMIN.SVR_SVM_UV set newrec=0'
                if not self.GetRecordasOld(sqlStmtUpd):
                    return
                returnCode = False

                fields = []
                fields = next(csvFile)

                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append(str(j))
                    self.textEdit.update()
                    app.processEvents()

                    uuid = str(row["UUID"])

                    # uuid = str(df.loc[ind, "UUID"])
                    fo_num = str(row["FO_NUM"])

                    # fo_num = str(df.loc[ind, "FO_NUM"])
                    ##########################################################
                    # // Проверка uuid + fo_num
                    sqlStmtCheck = 'SELECT * FROM DB2ADMIN.SVR_SVM_UV WHERE  UUID=? and FO_NUM=?'
                    rows = self.isRecordNewCheck(sqlStmtCheck, uuid, fo_num)
                    dat_meropr = row['DAT_MEROPR']

                    if dat_meropr == '':
                        dat_meropr = None

                    # ##// 'Нашёл!!!!'
                    if rows > 0:
                        returnCode = False
                        sqlStmtUpd = ""

                        sqlStmtUpd = "update DB2ADMIN.SVR_SVM_UV set NEWREC=1, IN_UVED=0, DAT_MEROPR=?  where UUID=? and FO_NUM=?"
                        if not self.SqlStmt(sqlStmtUpd, dat_meropr, uuid, fo_num):
                            message = f"{datetime.now()} - Can't run sql stmt update, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        notload = notload + 1
                        self.textEdit.append('notloaded, record exist: ' + str(notload))
                        app.processEvents()
                    #####################################
                    # не нашел добавляем
                    if rows == 0:
                        entnmb = row["ENTNMB"]

                        # entnmb = df.loc[ind, "ENTNMB"]
                        dptcod = str(entnmb)
                        dptcod = dptcod.zfill(12)
                        dptcod = dptcod[0:6]
                        dptcod = int(dptcod)
                        entnmb = int(entnmb)

                        nameorg = str(row["NAME_ORG"])

                        actual_entnmb = row["ACTUAL_ENTNMB"]
                        actual_dptcod = str(actual_entnmb)
                        actual_dptcod = actual_dptcod.zfill(12)
                        actual_dptcod = actual_dptcod[0:6]
                        actual_dptcod = int(actual_dptcod)
                        actual_entnmb = int(actual_entnmb)

                        inn = str(row["INN"]).zfill(10)
                        kpp = str(row["KPP"]).zfill(9)

                        a_inn = str(row["AINN"]).zfill(10)
                        a_kpp = str(row["AKPP"]).zfill(9)
                        a_name_org = str(row["ANAME"])

                        status = str(row["STATUS"]).zfill(2)
                        kateg = str(row["KATEG"]).zfill(4)

                        kod_snyat = row['KOD_SNYAT']
                        if kod_snyat == '':
                            kod_snyat = None

                        dat_snyat = row['DAT_SNYAT']
                        if dat_snyat == '':
                            dat_snyat = None
                        akod_snyat = row['AKOD_SNYAT']
                        if akod_snyat == '':
                            akod_snyat = None

                        adat_snyat = row['ADAT_SNYAT']
                        if adat_snyat == '':
                            adat_snyat = None

                        meropr = str(row["MEROPR"])
                        dat_doc = row['DAT_DOC']
                        num_doc = str(row["NUM_DOC"])
                        snilscs = str(row["SNILSCS"])
                        insnmb = row["SNILSCS"]
                        insnmb = insnmb.replace('-', '')
                        insnmb = insnmb[0:9]
                        insnmb = int(insnmb)
                        fio = str(row["FIO"])
                        ils = str(row["ILS"])
                        d_date = row['D_DATE']
                        if d_date == '':
                            d_date = None

                        fo_dat_txt = str(row["FO_DAT_TXT"])

                        dat_meruv = row["DAT_MERUV"]
                        num_docuv = str(row["NUM_DOCUV"])
                        uuid_uv = str(row["UUID_UV"])
                        fo_num_uv = str(row["FO_NUM_UV"])
                        fo_datuv_t = str(row["FO_DATUV_T"])

                        nspis = 1
                        # для первого списка 1 затем только для новых
                        in_uved = 1
                        dat_load = date.today()
                        newrec = 1
                        sqlStatement = """INSERT INTO SVR_SVM_UV (DPTCOD, ACTUAL_ENTNMB, ACTUAL_DPTCOD, AKOD_SNYAT, ADAT_SNYAT, ENTNMB, NAME_ORG, INN, KPP, STATUS, KATEG, 
                                               KOD_SNYAT, DAT_SNYAT,  DAT_MEROPR, MEROPR, NUM_DOC, DAT_DOC,  SNILSCS, INSNMB, FIO, ILS, D_DATE, UUID, FO_NUM, FO_DAT_TXT, 
                                                DAT_MERUV, NUM_DOCUV, UUID_UV, FO_NUM_UV, FO_DATUV_T, NSPIS , IN_UVED, DAT_LOAD, NEWREC, DAT_MEROPR_T, A_INN, A_KPP, A_NAME_ORG) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement, dptcod, actual_entnmb, actual_dptcod, akod_snyat,
                                            adat_snyat, entnmb, nameorg, inn, kpp, status, kateg,
                                            kod_snyat, dat_snyat, dat_meropr, meropr, num_doc, dat_doc, snilscs,
                                            insnmb, fio,
                                            ils, d_date, uuid, fo_num, fo_dat_txt, dat_meruv, num_docuv, uuid_uv,
                                            fo_num_uv, fo_datuv_t, nspis, in_uved, self.datload, newrec,
                                            dat_meropr, a_inn, a_kpp, a_name_org):
                            message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            logging.info(message)

                            return
                        load = load + 1
                        self.textEdit.append('loaded, new record: ' + str(load))
                        app.processEvents()
                self.textEdit.append('ИС Совместители,  уволен с основ должн., обработано всего :' + str(
                    j) + '  из них загружено новые: ' + str(load))

                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        ##################################################################################################################
        #                -temp_kp_itog---
        ###################################################################################################################
        elif self.ListNmbr == 16:
            with open(self.filename, 'r') as input_file:
                # col_names = ['DPTCOD','REG','DEP','RA','138','567','2s']
                col_names = ['DPTCOD', 'ENTNMB', 'LIKV138','LIKV567','LIKV2','ENTNMB_KP']

                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')

                returnCode = False
                fields = []
                fields = next(csvFile)
                j = 0
                load = 0
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append(str(j))
                    self.textEdit.update()
                    app.processEvents()
                    dptcod = row["DPTCOD"]
                    dptcod = int(dptcod)

                    reg = row["ENTNMB"]
                    reg = int(reg)

                    likv138 = row["LIKV138"]
                    likv138 = int(likv138)

                    likv567 = row["LIKV567"]
                    likv567 = int(likv567)

                    likv2 = row["LIKV2"]
                    likv2 = int(likv2)

                    regkp = row["ENTNMB_KP"]
                    regkp = int(regkp)
                    year=2024


                    rows = 0
                    if rows == 0:
                        load = load + 1
                        nspis = 1
                        newrec = 1
                        sqlStatement = """INSERT INTO DB2ADMIN.PU_KP (DPTCOD,ENTNMB,YEAR,LIKV138,LIKV567,LIKV2,ENTNMB_KP) VALUES (?,?,?,?,?,?,?)"""

                        if not self.SqlStmt(sqlStatement, dptcod, reg, year,likv138, likv567,likv2,regkp):
                            # message = f"{datetime.now()} - Can't run sql stmt insert, uuid: {uuid} - fo_num:  {fo_num} - № row {j}"
                            message = f"{datetime.now()} - Can't run sql stmt insert, - № row {j}"

                            logging.info(message)

                            return
                QApplication.restoreOverrideCursor()
        ###################################################################################################################
        ###################################################################################################################
        #    ----- ЕСТЬ  РСВ НЕТ  КМ  ---------------
        ###################################################################################################################
        elif self.ListNmbr == 17:
            with (open(self.filename, 'r') as input_file):



                col_names = ['ENTNMB', 'INN' ,'KPP','NAME_ORG',  'KATEG', 'KOD_SNYAT', 'DAT_SNYAT','ACTUAL_ENTNMB',
                             'ACTUAL_INN','ACTUAL_KPP','ACTUAL_NAME',
                              'SNILSCS','FIO', 'ILS_STATUS', 'D_DATE', 'RSV_YER', 'RSV_MON']




                csvFile = csv.DictReader(input_file, fieldnames=col_names, delimiter=';')
                ##########################################
                # // Отметим  все звписи  как старые
                sqlStmtUpd = 'update DB2ADMIN.SVR_RSV_NO_KM set newrec=0'
                if not self.GetRecordasOld(sqlStmtUpd):
                    return

                returnCode = False
                fields = []
                fields = next(csvFile)
                j=0
                QApplication.setOverrideCursor(Qt.WaitCursor)
                for row in csvFile:
                    j = j + 1
                    self.textEdit.append('all: ' + str(j))
                    self.textEdit.update()
                    app.processEvents()
                    snilscs = str(row["SNILSCS"])
                    insnmb = snilscs.replace('-', '')
                    insnmb = insnmb[0:9]
                    insnmb = int(insnmb)
                    inn = str(row["INN"]).zfill(10)
                    entnmb = int(row['ENTNMB'])

                    actual_entnmb = row['ACTUAL_ENTNMB']

                    if actual_entnmb:
                        actual_entnmb = int(actual_entnmb)
                        if actual_entnmb == entnmb:
                            actual_entnmb = None
                            actual_dptcod = None
                        else:
                            actual_dptcod = str(actual_entnmb)
                            actual_dptcod = actual_dptcod.zfill(12)
                            actual_dptcod = actual_dptcod[0:6]
                            actual_dptcod = int(actual_dptcod)




                    ils_status = str(row["ILS_STATUS"])
                    kpp = str(row["KPP"])
                    kateg = str(row["KATEG"])
                    dat_snyat = row['DAT_SNYAT']

                    if dat_snyat == '':
                        dat_snyat = None
                    kod_snyat = str(row["KOD_SNYAT"])

                    if kod_snyat == '':
                        kod_snyat = None

                    d_date = row['D_DATE']
                    if d_date == '':
                        d_date = None
                    rsv_yer=int(row["RSV_YER"])
                    rsv_mon=int(row["RSV_MON"])


                    sqlStmtCheck = """SELECT * FROM DB2ADMIN.SVR_RSV_NO_KM WHERE INSNMB=? and ENTNMB=?  and RSV_YER=?  and RSV_MON=?  """

                    rows = self.isRecordNewCheck(sqlStmtCheck, insnmb, entnmb, rsv_yer, rsv_mon)


                    # ##// 'Нашёл!!!!'
                    #
                    if rows > 0:

                        returnCode = False


                        sqlStmtUpd = ("update DB2ADMIN.SVR_RSV_NO_KM set NEWREC=1, DAT_LOAD=?,  INN=? , KPP=? , KATEG=?, ILS_STATUS=? , KOD_SNYAT=? , D_DATE=?, DAT_SNYAT=?  WHERE INSNMB=? and ENTNMB=?  "
                                      " and RSV_YER=?   and RSV_MON=?  ")



                        if not self.SqlStmt(sqlStmtUpd, self.datload, inn, kpp, kateg, ils_status, kod_snyat,
                                                   d_date, dat_snyat, insnmb, entnmb, rsv_yer, rsv_mon):

                            message = f"{datetime.now()} - - № row {j}"
                            logging.info(message)
                            return
                        notload = notload + 1
                        self.textEdit.append('not loaded, record exist: ' + str(notload))
                        app.processEvents()


                        #####################################
                    # не нашел, добавляем
                    if rows == 0:

                        dptcod = str(entnmb)
                        dptcod = dptcod.zfill(12)
                        dptcod = dptcod[0:6]
                        dptcod = int(dptcod)
                        name_org = str(row["NAME_ORG"])
                        fio = str(row["FIO"])
                        nspis = 1

                        # для первого списка 1 затем только для новых
                        in_uved = 1
                        newrec = 1

                        sqlStatement = """INSERT INTO SVR_RSV_NO_KM ( ENTNMB, INN ,KPP, NAME_ORG,  KATEG, KOD_SNYAT, DAT_SNYAT,
                              SNILSCS, INSNMB, FIO, ILS_STATUS, D_DATE, RSV_YER, RSV_MON, DPTCOD, NSPIS, DAT_LOAD, NEWREC, IN_UVED , ACTUAL_ENTNMB, ACTUAL_DPTCOD) 
                                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                        if not self.SqlStmt(sqlStatement,  entnmb, inn ,kpp, name_org,  kateg, kod_snyat, dat_snyat,
                              snilscs,insnmb,fio, ils_status, d_date, rsv_yer, rsv_mon, dptcod, nspis, self.datload, newrec, in_uved,actual_entnmb, actual_dptcod):
                            message = f"{datetime.now()} - Can't run sql stmt insert,  - № row {j}"

                            logging.info(message)

                            return
                        load = load + 1
                        self.textEdit.append('loaded, new record: ' + str(load))
                        app.processEvents()
                self.textEdit.append('Есть РСВ нет КМ, обработано всего :' + str(
                    j) + '  из них загружено новые: ' + str(load))

                QApplication.restoreOverrideCursor()

    ###################################################################################################################






        else:
            print("please select  List")
            return
        if j>0:
            message = f"{datetime.now()} - Done - Всего в списке: {j} - loaded, new record: {load} - not loaded, record exist: {notload}"
            logging.info(message)

        msgBox = QMessageBox()
        msgBox.setText("Всего в списке:"+" " +str(j) + "\n"+ "loaded, new record:" + " "+str(load) + "\n"+"not loaded:" +" "+ str(notload))
        msgBox.exec()





if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

