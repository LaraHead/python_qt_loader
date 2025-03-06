# Ввод данных

def check_all_students_passed(scores_input, names_input):
    scores = list(map(int, scores_input.split(',')))
    names = names_input.split(',')

    # Проходной балл
    passing_score = 35
    # Список студентов, не сдавших
    failing_students = []

    # Список студентов, не сдавших

    # # Проверка каждого студента
    for score, name in zip(scores, names):
        if score < passing_score:
            failing_students.append(name)


    # Вывод результата
    if not failing_students:
        return "Все сдали"
    else:
        result = "Есть не сдавшие"
        for student in failing_students:
            result += "\n " + student
        return result


# Ввод данных
scores_input = '30,20,50'  # Ввод баллов
names_input = 'rr,mmm,t'    # Ввод имен
#scores_input = input()
#names_input = input()



# Получение результата и вывод
result = check_all_students_passed(scores_input, names_input)
print(result)




