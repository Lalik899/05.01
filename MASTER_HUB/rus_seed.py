import datetime
from db import get_connection

conn = get_connection()
cur = conn.cursor()

for r in ["Заказчик", "Исполнитель", "Администратор"]:
    cur.execute("INSERT INTO [Роли] ([Название]) VALUES (?)", (r,))

for l in ["Начинающий", "Специалист", "Эксперт"]:
    cur.execute("INSERT INTO [УровниСпециалиста] ([Название]) VALUES (?)", (l,))

for s in ["Активно", "Снято"]:
    cur.execute("INSERT INTO [СтатусыОбъявлений] ([Название]) VALUES (?)", (s,))

for s in ["Оплачен", "Выполнен", "Отменен"]:
    cur.execute("INSERT INTO [СтатусыЗаказов] ([Название]) VALUES (?)", (s,))

dirs = [
    ("Программирование", ["Сайты на Python", "Telegram-боты", "Базы данных"]),
    ("Дизайн", ["Логотипы", "Веб-дизайн", "Презентации"]),
    ("Репетиторство", ["Математика", "Английский язык", "Информатика"])
]
for d_name, cats in dirs:
    cur.execute("INSERT INTO [Направления] ([Название]) VALUES (?)", (d_name,))
    cur.execute("SELECT @@IDENTITY")
    did = int(cur.fetchone()[0])
    for c_name in cats:
        cur.execute("INSERT INTO [Категории] ([КодНаправления], [Название]) VALUES (?, ?)", (did, c_name))

now = datetime.datetime.now()
users = [
    ("admin", "admin@masterhub.ru", "admin123", 3, 50000),
    ("alex_dev", "alex@masterhub.ru", "12345", 2, 12000),
    ("maria_art", "maria@masterhub.ru", "12345", 2, 8500),
    ("ivan_client", "ivan@masterhub.ru", "12345", 1, 25000)
]
for u in users:
    cur.execute("INSERT INTO [Пользователи] ([Логин], [Email], [Пароль], [КодРоли], [Баланс], [ДатаРегистрации], [Заблокирован]) VALUES (?, ?, ?, ?, ?, ?, ?)", (*u, now, False))

ads = [
    (1, 2, 3, "Telegram-бот под ключ на Python", "Разработка бота с подключением к БД и админкой.", 2, 4500, 3, 3),
    (1, 1, 2, "Верстка лендинга или сайта на Flask", "Адаптивный сайт с формой заявки.", 2, 6000, 2, 5),
    (2, 4, 3, "Минималистичный логотип и стиль", "3 концепции на выбор, исходники в векторе.", 3, 3000, 5, 2),
    (3, 9, 2, "Подготовка к ЕГЭ и ОГЭ по информатике", "Индивидуальное занятие 60 минут.", 3, 1500, 10, 1)
]
for d_id, c_id, l_id, title, desc, seller, price, slots, days in ads:
    cur.execute("INSERT INTO [Услуги] ([КодНаправления], [КодКатегории], [КодУровня], [Название], [Описание], [URLИзображения]) VALUES (?, ?, ?, ?, ?, ?)", (d_id, c_id, l_id, title, desc, ""))
    cur.execute("SELECT @@IDENTITY")
    sid = int(cur.fetchone()[0])
    cur.execute("INSERT INTO [Объявления] ([КодИсполнителя], [КодУслуги], [Цена], [Слоты], [СрокДней], [КодСтатуса], [ДатаСоздания]) VALUES (?, ?, ?, ?, ?, ?, ?)", (seller, sid, price, slots, days, 1, now))

conn.commit()
conn.close()
print("Русские справочники и демо-данные добавлены!")
