import sys
import os
import glob

#from bs4 import BeautifulSoup
from PySide6.QtCore import (Qt,QFileInfo)

from lxml import etree
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFileDialog,
    QGridLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QCheckBox
)
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Выписка ЕЦП из XML в HTML')
        self.setGeometry(500, 500, 500, 450)
        self.layout = QGridLayout()
        self.setLayout(self.layout)


        self.labelFile = QLabel("файл: ")
        self.layout.addWidget(self.labelFile)


        self.btnFopn = QPushButton("открыть файл")
        self.layout.addWidget(self.btnFopn)
        self.btnFopn.clicked.connect(self.fopn1)


        self.checkbox = QCheckBox("Преобразовать все файлы в папке? ")
        self.checkbox.stateChanged.connect(self.checkbox_changed)
        self.layout.addWidget(self.checkbox)





        self.btnStart = QPushButton("СТАРТ")
        self.layout.addWidget(self.btnStart)
        self.btnStart.clicked.connect(self.slivaem1)
        self.btnStart.setEnabled(False)

        self.filename = None
        self.Allfiles = 1

    def checkbox_changed(self, checkbox_state):
        if checkbox_state == 2:  # Checked
            self.Allfiles=2
        else:
            self.Allfiles=1

    def fopn1(self):
        self.filename = QFileDialog.getOpenFileName(self, "Открыть файл", "", "XML файл (*.xml)")[0]
        self.labelFile.setText(u"файл: "+self.filename)
        self.btnStart.setEnabled(True)

    def slivaem1(self):
        xml_files=[]
        xml_files.append(self.filename)
        if self.Allfiles == 2:
            folder_path = os.path.dirname(self.filename)
            search_path = os.path.join(folder_path, "*.xml")
            xml_files = glob.glob(search_path)
            QApplication.setOverrideCursor(Qt.WaitCursor)

        self.process_xml_files(xml_files)
        QApplication.restoreOverrideCursor()
        msgBox = QMessageBox()
        msgBox.setText("ФсЁ")
        msgBox.exec()

    def process_xml_files(self,xml_files):
        if not xml_files:
            return
        # Рекурсивный случай: обработать первый XML-файл
        xml_file = xml_files[0]
        with open(xml_file, 'r',encoding='utf-8') as f:
            xml_content = f.read()
        xml_tree = etree.XML(xml_content)
        svul=xml_tree.findall('СвЮЛ')
        svip=xml_tree.findall('СвИП')
        if svul:
            for sv in svul:
                ogrn_value = sv.get('ОГРН')
            if len(ogrn_value)==13:
                xslt_file = 'vo_rugf_asv.xsl'
                #xslt_file = 'ul_asv.xsl'

            else:
                xslt_file='vo_rigf_asv.xsl'
        if svip:
            for sv in svip:
                ogrn_value = sv.get('ОГРНИП')
            if len(ogrn_value)==13:
                xslt_file = 'vo_rugf_asv.xsl'
            else:
                xslt_file='vo_rigf_asv.xsl'
                #xslt_file='ip_asv.xsl'

        with open(xslt_file, 'rb') as f:
            xslt_content = f.read()
        xslt_tree = etree.XML(xslt_content)
        # Преобразование
        transform = etree.XSLT(xslt_tree)
        result_tree = transform(xml_tree)
        # Получаем имя файла без расширения
        filename_without_extension = os.path.splitext(xml_file)[0]
        filename_out =  filename_without_extension +'.html'
        # Сохранение результата в HTML файл
        with open(filename_out , 'wb') as f:
            f.write(etree.tostring(result_tree, pretty_print=True, encoding='Windows-1251'))
        # with open(filename_out, 'rb') as f:
        #     html_content = f.read()  # Ваш HTML-код здесь
        #     try:
        #         soup = BeautifulSoup(html_content, 'html.parser')
        #     except Exception as e:
        #         msgBox = QMessageBox()
        #         msgBox.setText("Ошибка в HTML")
        #         msgBox.exec()
        self.process_xml_files(xml_files[1:])

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())