import pandas as pd
import glob
def qi():
    File1 = pd.read_excel('ИС. Есть СЗВ-М за 2021-2023 год - нет стажа 2021.xlsx')
    df6 = pd.DataFrame(File1)
    # Нахождение повторяющихся значений по столбцам 'A' и 'B'
    duplicates = df6[df6.duplicated(subset=['Регномер', 'СНИЛС'], keep=False)]
    print(duplicates)




# подсчет уник вхождений
def quick():
    File = pd.read_excel('Есть РСВ - нет КМ.xlsx')
    df = pd.DataFrame(File)

    # Подсчет количества вхождений каждого рег номера
    reg_number_counts = df['Регномер страхователя'].value_counts().reset_index()
    # переименование столбцов
    reg_number_counts.columns = ['Регномер страхователя', 'Количество вхождений']
    # Сохранение результата в файл Excel
    output_file = "res2.xlsx"
    reg_number_counts.to_excel(output_file, index=False)


    # Подсчет количества вхождений каждого снилс
    reg_number_counts = df['СНИЛС'].value_counts().reset_index()
    # переименование столбцов
    reg_number_counts.columns = ['СНИЛС', 'Количество вхождений']
    # Сохранение результата в файл Excel
    output_file = "res3.xlsx"
    reg_number_counts.to_excel(output_file, index=False)

    # Подсчет уникальных СНИЛС по каждому  номеру страхователя
    result = df.groupby('Регномер страхователя')['СНИЛС'].nunique().reset_index()
    # Переименуем столбцы для удобства
    result.columns = ['Регномер страхователя', 'Количество уникальных СНИЛС']
    # Вывод результата
    result.to_excel(f'res.xlsx', index=False)


    # Подсчет количества вхождений каждого снилс по каждому  номеру страхователя
    result1 = df.groupby(['Регномер страхователя','СНИЛС']).size().reset_index()
    # Переименуем столбцы для удобства
    result1.columns = ['Регномер страхователя', 'СНИЛС','Количество вхожденийСНИЛС']
    # Вывод результата
    result1.to_excel(f'res4.xlsx', index=False)




    # Подсчет уникальных рег номеров страхователей
    unique_reg_numbers = df['Регномер страхователя'].nunique()

    # Вывод результата
    print(f"Количество уникальных рег номеров: {unique_reg_numbers}")



#выборка ушел пришел
def quicknew():
    Filenew = pd.read_excel('Есть РСВ - нет КМ_new.xlsx')
    df_new = pd.DataFrame(Filenew)
    Fileold = pd.read_excel('Есть РСВ - нет_old.xlsx')
    df_old = pd.DataFrame(Fileold)

    # Выбираем записи из df_old, которых нет в df_new по полю 'регномер'
    result = df_old[~df_old['Регномер страхователя'].isin(df_new['Регномер страхователя'])]
    # наоборот
    result_obr = df_new[~df_new['Регномер страхователя'].isin(df_old['Регномер страхователя'])]

    result.to_excel(f'res_ушли.xlsx', index=False)
    result_obr.to_excel(f'res_пришли.xlsx', index=False)

    #non_matching_records.to_excel(f'res.xlsx', index=False)



# добавление акт рег
def quickactnomera():
    Filenew = pd.read_excel('Есть РСВ - нет КМ_new.xlsx')
    df_new = pd.DataFrame(Filenew)
    Fileold = pd.read_excel('ГульназКопия ИС. Есть РСВ - нет КМ ДУБЛЬ6.xlsx')
    df_old = pd.DataFrame(Fileold)

    # Объединяем df_new с df_old по полю 'регномер'
    df_merged = pd.merge(df_new, df_old[['regnom', 'actregnom']], on='regnom', how='left', suffixes=('', '_old'))

    # Обновляем столбец 'акт_регномер' в df_new
    df_new['actregnom'] = df_merged['actregnom_old']

    df_new.to_excel(f'res_c актномерами.xlsx', index=False)

    #non_matching_records.to_excel(f'res.xlsx', index=False)



# сравнение  акт рег
def quickactsrav():

    # Загрузка данных из Excel файлов
    my = pd.read_excel('наш.xlsx')
    my_df = pd.DataFrame(my)

    msk = pd.read_excel('мск.xlsx')
    msk_df = pd.DataFrame(msk)
    # Выводим названия столбцов для проверки
    print("Столбцы в df1:", my_df.columns.tolist())
    print("Столбцы в df2:", msk_df.columns.tolist())
    # # Объединим данные по 'рег' и 'акт' для обоих DataFrame
    # merged_df = pd.merge(msk_df,  my_df[['regnom', 'akt']], on='regnom',  how='left',suffixes=('_1', '_2'))
    #
    # # Найдем записи, где 'акт' различается
    # diff_akt = merged_df[merged_df['akt_1'] != merged_df['akt_2']]
    #
    # # Сохраним результаты в отдельный список (DataFrame)
    # different_records = diff_akt[['regnom', 'akt_1', 'akt_2']]
    #
    # # 2. Записи, где 'акт' в первом списке пустой
    # empty_akt = my_df[my_df['akt'].isnull() | (my_df['akt'] == '')]
    #
    # # Сохранение результатов в новые Excel файлы
    # diff_list.to_excel('различия.xlsx', index=False)
    # empty_akt_list.to_excel('пустые_акты.xlsx', index=False)


quickactsrav()