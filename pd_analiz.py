# анализ с помощью пандас cool
import pandas as pd
import glob
import os
import datetime
def  quck():
    csvFile1 = pd.read_csv('Приложение 2.csv',  delimiter=';', encoding='cp1251')
    df1 = pd.DataFrame(csvFile1)

    portalcsv = pd.read_csv('journal_dt-есть допт нет стажа lgot_obr00-2024-12-17-2024-12-17.csv', delimiter=';', encoding='cp1251')
    df_por = pd.DataFrame(portalcsv)
    df1['match_value'] = ''
    df_per=pd.merge(df1,df_por,how='left', on='reg')

    #for value_to_find in my['СНИЛС']:

    # Проверяем наличие значения во втором файле
    # if value_to_find in df2['СНИЛС'].values:
    #   df2.loc[df2['СНИЛС'] == value_to_find, 'mark'] = 1
    #     matched_value = my.loc[my['СНИЛС'] == value_to_find, 'Результат проведенной работы'].values[0]
    #        matched_value = str(matched_value)
     #       df2.loc[df2['СНИЛС'] == value_to_find, 'Результат проведенной работы'] = matched_value

            # Приведение столбца 'Результат проведенной работы' к строковому значению
      #      df2['Результат проведенной работы'] = df2['Результат проведенной работы'].astype(str)

            # Сохраняем измененный файл
    df_per.to_csv('res.csv', sep=';' ,index=False, encoding='cp1251')
def  quck2():
    csvFile1 = pd.read_csv('Приложение 2.csv',  delimiter=';', encoding='cp1251')
    df1 = pd.DataFrame(csvFile1)

    csvFile2 = pd.read_csv('journal_dt-есть допт нет стажа lgot_obr00-2024-12-17-2024-12-17 (1).csv', delimiter=';', encoding='cp1251')
    df2 = pd.DataFrame(csvFile2)
    #df_diff = df2[~df2['reg'].isin(df1['reg'])]
    df_combined = pd.concat([df1, df2]).drop_duplicates(subset='reg').reset_index(drop=True)
    df_combined .to_csv('res.csv', sep=';' ,index=False, encoding='cp1251')
def  quck1():
    # можно одно поле прочитать
    csvFile1 = pd.read_csv('2_etk_szvtd_2024_06_25.csv',  delimiter=';', encoding='cp1251')
   # csvFile1 = pd.read_csv('1.csv', delimiter=';', encoding='cp1251')
    #File1 = pd.read_excel('Копия ИС. Есть КМ Прием - нет увольнения, нет РСВ за следующие периоды deaeff52 Cписок 6 Новый.xlsx')
    df1 = pd.DataFrame(csvFile1)


    #File2 = pd.read_excel('Копия ИС. Есть КМ Прием - нет увольнения, нет РСВ за 2023 год ae2ae039 Список 6+.xlsx')

    csvFile2 = pd.read_csv('2_etk_szvtd_2024_11_12.csv',  delimiter=';', encoding='cp1251')
    df2 = pd.DataFrame(csvFile2)
    res = pd.merge(df1,df2,how='left',on='Графа 4')

    #res.to_excel('res.xlsx')
    res.to_csv('res.csv', sep=';' ,index=False, encoding='cp1251',float_format='%.0f')



  #  csvFile3 = pd.read_csv('3.csv',  delimiter=';', encoding='cp1251')
  #   df3 = pd.DataFrame(csvFile3)
  #
  #   csvFile4 = pd.read_csv('4.csv',  delimiter=';', encoding='cp1251')
  #   df4 = pd.DataFrame(csvFile4)
  #
  #   csvFile5 = pd.read_csv('5.csv',  delimiter=';', encoding='cp1251')
  #   df5 = pd.DataFrame(csvFile5)
  #
  #   csvFile6 = pd.read_csv('6.csv',  delimiter=';', encoding='cp1251')
  #   df6 = pd.DataFrame(csvFile6)


    #res = pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(df1, df2, on='СНИЛС'), df3, on='СНИЛС'), df4, on='СНИЛС'), df5, on='СНИЛС'), df6,on='СНИЛС')
    #res = pd.merge(df1, df2, on='СНИЛС')


    #res = pd.merge(df1, df6, on='СНИЛС')
    #res = pd.merge(pd.merge(df2, df3, on='СНИЛС'), df5, on='СНИЛС')
    #res = pd.merge(pd.merge(pd.merge(df2, df3, on='СНИЛС'), df5, on='СНИЛС'), df6, on='СНИЛС')

    #    for value_to_find in my['СНИЛС']:

        # Проверяем наличие значения во втором файле
 #       if value_to_find in df2['СНИЛС'].values:

  #          df2.loc[df2['СНИЛС'] == value_to_find, 'mark'] = 1

   #         matched_value = my.loc[my['СНИЛС'] == value_to_find, 'Результат проведенной работы'].values[0]
    #        matched_value = str(matched_value)
     #       df2.loc[df2['СНИЛС'] == value_to_find, 'Результат проведенной работы'] = matched_value

            # Приведение столбца 'Результат проведенной работы' к строковому значению
      #      df2['Результат проведенной работы'] = df2['Результат проведенной работы'].astype(str)

            # Сохраняем измененный файл
#    res.to_csv('res.csv', sep=';' ,index=False, encoding='cp1251')
def  nareska():
    File6 = pd.read_excel('Список 2_Есть доптариф за 2023 год, нет стажа с ОУТ fab856ab Список 3+.xlsx',dtype={'Дата смерти':str,'Дата снятия с учета в РО': str})
    df6 = pd.DataFrame(File6)
    df6['Дата смерти'] = pd.to_datetime(df6['Дата смерти'])
    df6['Дата снятия с учета в РО'] = pd.to_datetime(df6['Дата снятия с учета в РО'])

    grouped = df6.groupby('код района')
    for name, group in grouped:
        group['Дата смерти'] = group['Дата смерти'].dt.strftime('%d.%m.%Y')
        group['Дата снятия с учета в РО'] = group['Дата снятия с учета в РО'].dt.strftime('%d.%m.%Y')

        group.to_excel(f'{name}_Список 2_Есть доптариф за 2023 год, нет стажа с ОУТ fab856ab Список 3+.xlsx', index=False)

def  nareska4():
    File6 = pd.read_excel('Копия ИС. Есть стаж с РКС_МКС за 2022-2023 год, нет стажа с ТУ за 2023-2024 год bd34a5a9.xlsx',dtype={'Дата смерти':str,'Дата снятия с учета в РО': str,'Дата КМ=': str,'Дата пакета=': str})
    df6 = pd.DataFrame(File6)
    df6['Дата смерти'] = pd.to_datetime(df6['Дата смерти'])
    df6['Дата снятия с учета в РО'] = pd.to_datetime(df6['Дата снятия с учета в РО'])
    df6['Дата КМ'] = pd.to_datetime(df6['Дата КМ'])
    df6['Дата пакета'] = pd.to_datetime(df6['Дата пакета'])

    grouped = df6.groupby('код района')
    for name, group in grouped:
        group['Дата смерти'] = group['Дата смерти'].dt.strftime('%d.%m.%Y')
        group['Дата снятия с учета в РО'] = group['Дата снятия с учета в РО'].dt.strftime('%d.%m.%Y')
        group['Дата КМ'] = group['Дата КМ'].dt.strftime('%d.%m.%Y')
        group['Дата пакета'] = group['Дата пакета'].dt.strftime('%d.%m.%Y')

        group.to_excel(f'{name}_ИС. Есть стаж с РКС_МКС за 2022 год, нет стажа с ТУ за 2023 год.xlsx', index=False)

def  nareska1():
    File6 = pd.read_excel('ИС. Стаж за 2022 не до 31.12, нет КМ Увольнение 5f28f589.xlsx',dtype={'Дата смерти':str,'Дата снятия с учета': str,'Стаж_с=': str,'Стаж_по=': str,'Дата постановки на учет': str})
    df6 = pd.DataFrame(File6)
    df6['Дата постановки на учет'] = pd.to_datetime(df6['Дата постановки на учет'])


    df6['Дата смерти'] = pd.to_datetime(df6['Дата смерти'])
    df6['Дата снятия с учета'] = pd.to_datetime(df6['Дата снятия с учета'])

    df6['Стаж_с'] = pd.to_datetime(df6['Стаж_с'])
    df6['Стаж_по'] = pd.to_datetime(df6['Стаж_по'])

    grouped = df6.groupby('код района')
    for name, group in grouped:
        group['Дата смерти'] = group['Дата смерти'].dt.strftime('%d.%m.%Y')
        group['Дата снятия с учета'] = group['Дата снятия с учета'].dt.strftime('%d.%m.%Y')
        group['Дата постановки на учет'] = group['Дата постановки на учет'].dt.strftime('%d.%m.%Y')

        group['Стаж_с'] = group['Стаж_с'].dt.strftime('%d.%m.%Y')
        group['Стаж_по'] = group['Стаж_по'].dt.strftime('%d.%m.%Y')

        group.to_excel(f'{name}_ИС. Стаж за 2022 не до 31.12, нет КМ Увольнение 5f28f589.xlsx', index=False)

def  nareska5():
    File6 = pd.read_excel('ИС. Педагоги, медики, творческие профессии - нет стажа за 2023 год bdc5da46.xlsx',dtype={'Дата смерти':str,'Дата снятия с учета в РО': str,'Дата последнего КМ=': str,'Дата поступления': str})
    df6 = pd.DataFrame(File6)
    df6['Дата смерти'] = pd.to_datetime(df6['Дата смерти'])

    df6['Дата поступления'] = pd.to_datetime(df6['Дата поступления'])


    df6['Дата снятия с учета в РО'] = pd.to_datetime(df6['Дата снятия с учета в РО'])

    df6['Дата последнего КМ'] = pd.to_datetime(df6['Дата последнего КМ'])

    grouped = df6.groupby('код района')
    for name, group in grouped:
        group['Дата смерти'] = group['Дата смерти'].dt.strftime('%d.%m.%Y')
        group['Дата снятия с учета в РО'] = group['Дата снятия с учета в РО'].dt.strftime('%d.%m.%Y')
        group['Дата поступления'] = group['Дата поступления'].dt.strftime('%d.%m.%Y')

        group['Дата последнего КМ'] = group['Дата последнего КМ'].dt.strftime('%d.%m.%Y')

        group.to_excel(f'{name}_Педагоги, медики, творческие профессии - нет стажа за 2023 год bdc5da46.xlsx', index=False)

def  nareska6():
    File6 = pd.read_excel('Список 5 Есть КМ Прием - нет увольнения, нет РСВ за следующие периоды deaeff52 Cписок 6 Новый.xlsx',dtype={'Дата смерти':str,'Дата снятия с учета в РО': str,'Дата КМ=': str,'Дата приказа': str, 'Код выполняемой функции' : str})
    df6 = pd.DataFrame(File6)
    df6['Дата смерти'] = pd.to_datetime(df6['Дата смерти'])

    df6['Дата КМ'] = pd.to_datetime(df6['Дата КМ'])


    df6['Дата снятия с учета в РО'] = pd.to_datetime(df6['Дата снятия с учета в РО'])

    df6['Дата приказа'] = pd.to_datetime(df6['Дата приказа'])
    df6['Дата регистрации пакета'] = pd.to_datetime(df6['Дата регистрации пакета'])

    grouped = df6.groupby('код района')
    for name, group in grouped:
        group['Дата смерти'] = group['Дата смерти'].dt.strftime('%d.%m.%Y')
        group['Дата снятия с учета в РО'] = group['Дата снятия с учета в РО'].dt.strftime('%d.%m.%Y')
        group['Дата КМ'] = group['Дата КМ'].dt.strftime('%d.%m.%Y')

        group['Дата приказа'] = group['Дата приказа'].dt.strftime('%d.%m.%Y')

        group['Дата регистрации пакета'] = group['Дата регистрации пакета'].dt.strftime('%d.%m.%Y %H:%M:%S')

        group.to_excel(f'{name}_Список 5 Есть КМ Прием - нет увольнения, нет РСВ за следующие периоды deaeff52 Cписок 6 Новый.xlsx', index=False)

def slivaem1():
    excel_files = glob.glob("*.xlsx")
    # Создать пустой DataFrame
    combined_data = pd.DataFrame()
    # Цикл для чтения и объединения всех файлов Excel
    for file in excel_files:
        data = pd.read_excel(file)
        combined_data = pd.concat([combined_data, data])



    count_non_null = combined_data.notnull().sum()

    new_row = pd.DataFrame([count_non_null.values], columns=count_non_null.index)
    combined_data = pd.concat([combined_data, new_row], ignore_index=True)

    # Сохранить объединенные данные в новый Excel файл
    combined_data.to_excel("combined_data.xlsx", index=False)
    #combined_data = pd.DataFrame()


def  quckbudg():
    # можно одно поле прочитать
    File1 = pd.read_excel('2_etk_szvtd_2024_06_25.xlsx')
   # csvFile1 = pd.read_csv('1.csv', delimiter=';', encoding='cp1251')
    #File1 = pd.read_excel('Копия ИС. Есть КМ Прием - нет увольнения, нет РСВ за следующие периоды deaeff52 Cписок 6 Новый.xlsx')
    df1 = pd.DataFrame(File1)



    File2 = pd.read_excel('2_etk_szvtd_2024_07_30.xlsx')
    df2 = pd.DataFrame(File2)
    #res = pd.merge(df2, df1, how='left',on='ENTNMB')
    df_diff = df2[~df2['Графа 4'].isin(df1['Графа 4'])]
    df_diff.to_excel('resoldjun.xlsx')

# сливаем для Эльвиры
def slivaemElv():
    # Путь к папке с файлами Excel
    #path = 'C:/pythonProject/2/pythonProject/Сибай/*.xls*'
    #path = 'C:/pythonProject/2/pythonProject/№9/*.xls*'
    #path = 'C:/pythonProject/2/pythonProject/№1/*.xls*'
    #path = 'C:/pythonProject/2/pythonProject/№3/всевместе/*.xls*'
    #path = 'C:/pythonProject/2/pythonProject/№6/все вместе/*.xls*'
    path = 'C:/pythonProject/2/pythonProject/№11/всевместе/*.xls*'

    output_file='объединенный_файл.xlsx'
    output_file_summary='статистика.xlsx'
    output_file_deleted4='удаленные4.xlsx'
    output_file_deleted5='удаленные5.xlsx'

    all_files = glob.glob(path)

    file_count = 0
    # Создаем пустой DataFrame для объединения данных
    combined_data = pd.DataFrame()
    combined_data_stat = pd.DataFrame()
    combined_data_deleted = pd.DataFrame()
    for file in all_files:
        df_dirty = pd.read_excel(file, skiprows=9)  # Пропускаем 10 строк
        row_11 = df_dirty.iloc[0]

        df_dirty = pd.read_excel(file, skiprows=10)  # Пропускаем 11 строк
        # Получаем 12-ю строку (индекс 11, так как индексация начинается с 0)
        row_12 = df_dirty.iloc[0]

        # Проверяем, содержит ли строка требуемый текст
        contains_text11 = row_11.astype(str).str.contains("Наименование страхователя", na=False).any()
        contains_text12 = row_12.astype(str).str.contains("Наименование страхователя", na=False).any()

        if  contains_text11 or contains_text12:
            #df = pd.read_excel(file, skiprows=12)  # Пропускаем 12 строк
            # Получаем 14-ю строку
            #row_13 = df.iloc[0]
            # еще раз проверяем, содержит ли строка требуемый текст
            #contains_text1 = row_13.astype(str).str.contains("12", na=False).any()
            #if contains_text1:
            if contains_text11:
                df = pd.read_excel(file, skiprows=12)  # Пропускаем 12 строк
            if contains_text12:
                df = pd.read_excel(file, skiprows=13)  # Пропускаем 13 строк

            df['имя файла'] = os.path.basename(file)

            contains_text = row_11.astype(str).str.contains("Наименование страхователя", na=False).any()
            # Фильтрация строк, содержащих подстроку "содержит X файлов" во всех столбцах
            #filtered_df = df[df.applymap(lambda x: isinstance(x, str) and "В данный раздел описи внесено дел:" in x).any(axis=1)]

            # Фильтрация строк, содержащих подстроку "В данный раздел описи внесено дел:" во всех столбцах
            #filtered_df = df[df.stack().str.contains("В данный раздел описи внесено дел:").groupby(level=0).any()]
            # Фильтрация строк, содержащих подстроку "содержит X файлов"
            #filtered_df = df[df.iloc[:,0].str.contains('В данный раздел описи внесено дел', regex=True,na=False)]
            filtered_df = df[df[1].str.replace(' ', '', regex=False).str.contains('Вданныйразделописивнесенодел:', na=False)]
            # Оставляем только цифры
            #filtered_df['only_numbers'] =  filtered_df[filtered_df[4].str.replace(r'D', '', regex=True)]

            combined_data = pd.concat([combined_data, df], ignore_index=True)
            combined_data_stat= pd.concat([ combined_data_stat, filtered_df], ignore_index=True)
            file_count += 1
        else:
            mess="нарушена структура файла "+ os.path.basename(file)
            print(mess)
    # Удаляем строки, где столбец  пустой

    #combined_data = combined_data[combined_data.iloc[:, 1].notnull()]
    combined_data_deleted4 = combined_data[combined_data.iloc[:, 4].isnull()]
    combined_data_deleted5 = combined_data[combined_data.iloc[:, 5].isnull()]


    combined_data = combined_data[combined_data.iloc[:, 4].notnull()]
    combined_data = combined_data[combined_data.iloc[:, 5].notnull()]
    #df_summary = combined_data[combined_data.apply(lambda row: row.astype(str).str.contains("В данный раздел описи внесено дел:", na=False).any(), axis=1)]
    #combined_data_summary = combined_data.loc[combined_data.iloc[:, 4].isnull()]
    # Удаляем строки с указанным текстом
    #df = df[~df.iloc[:, 0].str.contains("В данный раздел описи внесено  дел:", na=False, case=False)]
    # Сохраняем результат в новый Excel файл
    combined_data.to_excel(output_file, index=False)
    combined_data_stat.to_excel(output_file_summary, index=False)
    combined_data_deleted4.to_excel(output_file_deleted4, index=False)
    combined_data_deleted5.to_excel(output_file_deleted5, index=False)

    #df_summary.to_excel(output_file, index=False,sheet_name='Summary_a')

    with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
        pd.DataFrame({'Количество файлов': [file_count]}).to_excel(writer, index=False, sheet_name='Summary')
def slivaemElv_test():
    # Путь к папке с файлами Excel
    #path = 'C:/pythonProject/2/pythonProject/Сибай/*.xls*'
    #path = 'C:/pythonProject/2/pythonProject/№9/всевместе/*.xls*'
    #path = 'C:/pythonProject/2/pythonProject/№1/*.xls'
    #path = 'C:/pythonProject/2/pythonProject/№3/всевместе/*.xls*'
    #path = 'C:/pythonProject/2/pythonProject/№6/все вместе/*.xls*'
    #path = 'C:/pythonProject/2/pythonProject/№11/всевместе/*.xls*'
    path = 'C:/pythonProject/2/pythonProject/№13/всевместе/*.xls*'
    output_file='объединенный_файл.xlsx'
    output_file_summary_my='статистика_my.xlsx'
    output_file_summary_rn='статистика_rn.xlsx'


    all_files = glob.glob(path)

    file_count = 0
    row_cnt=0
    # Создаем пустой DataFrame для объединения данных
    combined_data = pd.DataFrame()
    combined_data_stat_my = pd.DataFrame(columns=['Номер строки'])
    combined_data_stat_rn = pd.DataFrame()

    for file in all_files:
        df_dirty = pd.read_excel(file)


        matching_rows_start = df_dirty[df_dirty.apply(lambda row: row.astype(str).str.contains('Наименование страхователя').any(), axis=1)]


        # Получение индексов найденных строк
        if not matching_rows_start.empty:
            # Индекс (номер строки) первой найденной строки
            row_index_start = matching_rows_start.index[0]
            matching_rows = df_dirty[df_dirty.apply(lambda row: row.astype(str).str.contains('В данный раздел описи внесено').any(), axis=1)]

            # Получение индексов найденных строк
            if not matching_rows.empty:
                # Индекс (номер строки) первой найденной строки
                row_index = matching_rows.index[0]

                row_check = df_dirty.iloc[row_index - 1]
                # Проверка на пустоту
                is_empty = row_check.isna().all() or row_check.astype(str).str.strip().eq("").all()
                #есть пустая строка
                if is_empty:
                    row_cnt=row_index-1-row_index_start-3
                else:
                    row_cnt=row_index-1-row_index_start-2

                output_data = {'номер строки ':[row_cnt] if row_cnt is not None else ['Не найдено']    }
                print(f"{row_cnt} ")
            else:
                print(f"Текст В данный раздел описи внесено не найдено {file}" )
                return


            row_index_start=row_index_start+3
            df = pd.read_excel(file, skiprows=row_index_start,nrows=row_cnt)
            df['имя файла'] = os.path.basename(file)

            combined_data = pd.concat([combined_data, df], ignore_index=True)

            # Создание DataFrame для вывода
            new_df = pd.DataFrame(output_data)

            df_dirty['имя файла'] = os.path.basename(file)
            # Фильтрация DataFrame: оставляем только записи, содержащие текст "в данной описи"
            filtered_df = df_dirty[df_dirty.apply(lambda row: row.astype(str).str.contains('В данный раздел описи внесено').any(), axis=1)]



            # Объединение
            combined_data_stat_my = pd.concat([combined_data_stat_my, new_df], ignore_index=True)
            combined_data_stat_rn= pd.concat([ combined_data_stat_rn, filtered_df], ignore_index=True)

            file_count += 1
        else:
            mess="нарушена структура файла "+ os.path.basename(file)
            print(mess)
    combined_data.to_excel(output_file, index=False)
    combined_data_stat_my.to_excel(output_file_summary_my, index=False)
    combined_data_stat_rn.to_excel(output_file_summary_rn, index=False)

    with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
        pd.DataFrame({'Количество файлов': [file_count]}).to_excel(writer, index=False, sheet_name='Summary')


def slivaemElv_1():
    # Путь к папке с файлами Excel
    # path = 'C:/pythonProject/2/pythonProject/Сибай/*.xls*'
    # path = 'C:/pythonProject/2/pythonProject/№9/всевместе/*.xls*'
    # path = 'C:/pythonProject/2/pythonProject/№1/*.xls'
    # path = 'C:/pythonProject/2/pythonProject/№3/всевместе/*.xls*'
    # path = 'C:/pythonProject/2/pythonProject/№6/все вместе/*.xls*'
    path = 'C:/pythonProject/2/pythonProject/№11/всевместе/*.xls*'

    output_file = 'объединенный_файл.xlsx'
    output_file_summary = 'статистика.xlsx'

    all_files = glob.glob(path)

    file_count = 0
    # Создаем пустой DataFrame для объединения данных
    combined_data = pd.DataFrame()
    combined_data_stat = pd.DataFrame()
    combined_data_deleted = pd.DataFrame()
    for file in all_files:
        df_dirty = pd.read_excel(file, skiprows=9)  # Пропускаем 10 строк
        row_11 = df_dirty.iloc[0]

        df_dirty = pd.read_excel(file, skiprows=10)  # Пропускаем 11 строк
        # Получаем 12-ю строку (индекс 11, так как индексация начинается с 0)
        row_12 = df_dirty.iloc[0]
        # Проверяем, содержит ли строка требуемый текст
        contains_text11 = row_11.astype(str).str.contains("Наименование страхователя", na=False).any()
        contains_text12 = row_12.astype(str).str.contains("Наименование страхователя", na=False).any()
        if  contains_text11 or contains_text12:
            #df = pd.read_excel(file, skiprows=12)  # Пропускаем 12 строк
            # Получаем 14-ю строку
            row_13 = df.iloc[0]
            # еще раз проверяем, содержит ли строка требуемый текст
            #contains_text1 = row_13.astype(str).str.contains("12", na=False).any()
            # if contains_text1:

            # Поиск строк, содержащих нужный текст
            matching_rows = df_dirty[
                df_dirty.apply(lambda row: row.astype(str).str.contains('В данный раздел описи внесено').any(), axis=1)]

            # Получение индексов найденных строк
            if not matching_rows.empty:
                # Индекс (номер строки) первой найденной строки

                row_index = matching_rows.index[0]
                if contains_text11:
                    # Подготовка данных для записи в Excel
                    output_data = {'номер строки ': [row_index - 3] if row_index is not None else ['Не найдено']}

                    print(f"{row_index - 3} ")
                else:
                    output_data = {'номер строки ': [row_index - 4] if row_index is not None else ['Не найдено']}

                    print(f"{row_index - 4} ")

            else:
                print(f"Текст В данный раздел описи внесено не найдено {file}")
                return

            if contains_text11:
                row_index = row_index - 3

                df = pd.read_excel(file, skiprows=12, nrows=row_index)  # Пропускаем 12 строк
            if contains_text12:
                row_index = row_index - 4

                df = pd.read_excel(file, skiprows=13, nrows=row_index)  # Пропускаем 13 строк

            df['имя файла'] = os.path.basename(file)

            # contains_text_end = row_11.astype(str).str.contains("Наименование страхователя", na=False).any()
            # Фильтрация строк, содержащих подстроку "содержит X файлов" во всех столбцах
            # filtered_df = df[df.applymap(lambda x: isinstance(x, str) and "В данный раздел описи внесено дел:" in x).any(axis=1)]

            # Фильтрация строк, содержащих подстроку "В данный раздел описи внесено дел:" во всех столбцах
            # filtered_df = df[df.stack().str.contains("В данный раздел описи внесено дел:").groupby(level=0).any()]
            # Фильтрация строк, содержащих подстроку "содержит X файлов"
            # filtered_df = df[df.iloc[:,0].str.contains('В данный раздел описи внесено дел', regex=True,na=False)]
            # filtered_df = df[df[1].str.replace(' ', '', regex=False).str.contains('Вданныйразделописивнесенодел:', na=False)]
            # Оставляем только цифры
            # filtered_df['only_numbers'] =  filtered_df[filtered_df[4].str.replace(r'D', '', regex=True)]

            combined_data = pd.concat([combined_data, df], ignore_index=True)
            # Создание DataFrame для вывода
            combined_data_stat = pd.DataFrame(output_data)

            combined_data_stat.to_excel(output_file_summary, index=False)
            # combined_data_stat= pd.concat([ combined_data_stat, filtered_df], ignore_index=True)
            file_count += 1
        else:
            mess = "нарушена структура файла " + os.path.basename(file)
            print(mess)
    # Удаляем строки, где столбец  пустой

    # combined_data = combined_data[combined_data.iloc[:, 1].notnull()]
    # combined_data_deleted4 = combined_data[combined_data.iloc[:, 4].isnull()]
    # combined_data_deleted5 = combined_data[combined_data.iloc[:, 5].isnull()]

    # combined_data = combined_data[combined_data.iloc[:, 4].notnull()]
    # combined_data = combined_data[combined_data.iloc[:, 5].notnull()]
    # df_summary = combined_data[combined_data.apply(lambda row: row.astype(str).str.contains("В данный раздел описи внесено дел:", na=False).any(), axis=1)]
    # combined_data_summary = combined_data.loc[combined_data.iloc[:, 4].isnull()]
    # Удаляем строки с указанным текстом
    # df = df[~df.iloc[:, 0].str.contains("В данный раздел описи внесено  дел:", na=False, case=False)]
    # Сохраняем результат в новый Excel файл
    combined_data.to_excel(output_file, index=False)
    # combined_data_stat.to_excel(output_file_summary, index=False)
    # combined_data_deleted4.to_excel(output_file_deleted4, index=False)
    # combined_data_deleted5.to_excel(output_file_deleted5, index=False)

    # df_summary.to_excel(output_file, index=False,sheet_name='Summary_a')

    with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
        pd.DataFrame({'Количество файлов': [file_count]}).to_excel(writer, index=False, sheet_name='Summary')

def renamefiles():
    # Укажите путь к папке, в которой нужно переименовать файлы
    folder_path = 'C:/pythonProject/2/pythonProject/№13/Стерлитамакский р-н_844/Описи ЮЛ/'  # Замените на путь к вашей папке

    # Получите список всех файлов в папке
    files = os.listdir(folder_path)

    # Переименование файлов
    for index, old_filename in enumerate(files):
        # Создаем новое имя файла (например, добавляем префикс или суффикс)
        # Пример: добавим "new_" в начало имени каждого файла
        new_filename = f"844 стерлит рн_{old_filename}"

        # Формируем полный путь к старому и новому файлу
        old_file_path = os.path.join(folder_path, old_filename)
        new_file_path = os.path.join(folder_path, new_filename)

        # Переименование файла
        os.rename(old_file_path, new_file_path)

    print("Файлы успешно переименованы.")

#slivaemElv()
slivaemElv_test()
#renamefiles()
#quck2()
#nareska4()
#nareska1()