from server.backend.database import create_db
from server.services.event_crud import create_event
from server.services.record_crud import create_record
from server.services.user_crud import create_user

create_db()

user_nikita = create_user('Муляр Никита Михайлович', 2025, 'Математико-программистский')
print(user_nikita.id)
events = [
    create_event('Олимпиада по промышленной разработке PROD',
                 'Промышленное программирование', 9999, 2025, None,
                 'PROD', 'PROD', 'ЗЭ', 'Заключительный',
                 'prod', 'finals'),
    create_event('ОГЭ по математике', 'Математика', -89, 2023, None,
                 'ОГЭ', 'ОГЭ', 'ОГЭ', 'ОГЭ', 'oge',
                 'oge'),
    create_event('ОГЭ по русскому языку', 'Русский язык', -89, 2023, None,
                 'ОГЭ', 'ОГЭ', 'ОГЭ', 'ОГЭ', 'oge',
                 'oge'),
    create_event('ОГЭ по информатике', 'Информатика', -89, 2023, None,
                 'ОГЭ', 'ОГЭ', 'ОГЭ', 'ОГЭ', 'oge',
                 'oge'),
    create_event('ОГЭ по английскому языку', 'Английский язык', -89, 2023, None,
                 'ОГЭ', 'ОГЭ', 'ОГЭ', 'ОГЭ', 'oge',
                 'oge'),
    create_event('ЕГЭ по математике', 'Математика', -90, 2025, None,
                 'ЕГЭ', 'ЕГЭ', 'ЕГЭ', 'ЕГЭ', 'ege',
                 'ege'),
    create_event('ЕГЭ по русскому языку', 'Русский язык', -90, 2025, None,
                 'ЕГЭ', 'ЕГЭ', 'ЕГЭ', 'ЕГЭ', 'ege',
                 'ege'),
    create_event(f'РЭ ВсОШ по Информатика', 'Информатика', -99, 2025, None,
                 'ВсОШ', 'РЭ ВсОШ', 'РЭ', 'Региональный',
                 'vos', 'region'),
    create_event(f'МЭ ВсОШ по Информатика', 'Информатика', -98, 2024, None,
                       'ВсОШ', 'МЭ ВсОШ', 'МЭ', 'Муниципальный',
                       'vos', 'municip'),
    create_event(f'ШЭ ВсОШ по Информатика', 'Информатика', -97, 2024, None,
                 'ВсОШ', 'ШЭ ВсОШ', 'ШЭ', 'Школьный',
                 'vos', 'school')
]
for i in range(len(events)):
    if i == 0:
        create_record(user_nikita.id, events[i].id, 'Призер', 81, '2 степень')
    elif 1 <= i <= 4:
        create_record(user_nikita.id, events[i].id, 'Сдано', 5, None)
    elif i == 5:
        create_record(user_nikita.id, events[i].id, 'Сдано', 95, None)
    elif i == 6:
        create_record(user_nikita.id, events[i].id, 'Сдано', 91, None)
    elif i == 7:
        create_record(user_nikita.id, events[i].id, 'Участник', None, None)
    elif i == 8:
        create_record(user_nikita.id, events[i].id, 'Призер', None, None)
    elif i == 9:
        create_record(user_nikita.id, events[i].id, 'Победитель', None, None)
