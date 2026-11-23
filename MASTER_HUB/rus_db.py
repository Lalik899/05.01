import datetime
from db import get_connection

conn = get_connection()
cur = conn.cursor()

old = ["Reviews", "Transactions", "Orders", "Ads", "Services",
       "Users", "OrderStatuses", "AdStatuses", "Levels",
       "Categories", "Directions", "Roles"]

for t in old:
    try:
        cur.execute(f"DROP TABLE [{t}]")
    except Exception:
        pass
s1 = [
    "CREATE TABLE [Роли] ([КодРоли] AUTOINCREMENT PRIMARY KEY, [Название] TEXT(50))",
    "CREATE TABLE [Направления] ([КодНаправления] AUTOINCREMENT PRIMARY KEY, [Название] TEXT(100))",
    "CREATE TABLE [Категории] ([КодКатегории] AUTOINCREMENT PRIMARY KEY, [КодНаправления] LONG, [Название] TEXT(100))",
    "CREATE TABLE [УровниСпециалиста] ([КодУровня] AUTOINCREMENT PRIMARY KEY, [Название] TEXT(50))",
    "CREATE TABLE [СтатусыОбъявлений] ([КодСтатуса] AUTOINCREMENT PRIMARY KEY, [Название] TEXT(50))",
    "CREATE TABLE [СтатусыЗаказов] ([КодСтатуса] AUTOINCREMENT PRIMARY KEY, [Название] TEXT(50))"
]
for q in s1:
    cur.execute(q)
s2 = [
    "CREATE TABLE [Пользователи] ([КодПользователя] AUTOINCREMENT PRIMARY KEY, [Логин] TEXT(50), [Email] TEXT(100), [Пароль] TEXT(255), [КодРоли] LONG, [Баланс] CURRENCY, [ДатаРегистрации] DATETIME, [Заблокирован] YESNO)",
    "CREATE TABLE [Услуги] ([КодУслуги] AUTOINCREMENT PRIMARY KEY, [КодНаправления] LONG, [КодКатегории] LONG, [КодУровня] LONG, [Название] TEXT(150), [Описание] MEMO, [URLИзображения] TEXT(255))",
    "CREATE TABLE [Объявления] ([КодОбъявления] AUTOINCREMENT PRIMARY KEY, [КодИсполнителя] LONG, [КодУслуги] LONG, [Цена] CURRENCY, [Слоты] LONG, [СрокДней] LONG, [КодСтатуса] LONG, [ДатаСоздания] DATETIME)"
]
for q in s2:
    cur.execute(q)
s3 = [
    "CREATE TABLE [Заказы] ([КодЗаказа] AUTOINCREMENT PRIMARY KEY, [КодЗаказчика] LONG, [КодОбъявления] LONG, [Количество] LONG, [Сумма] CURRENCY, [Комментарий] MEMO, [ДатаЗаказа] DATETIME, [КодСтатуса] LONG)",
    "CREATE TABLE [Транзакции] ([КодТранзакции] AUTOINCREMENT PRIMARY KEY, [КодПользователя] LONG, [КодЗаказа] LONG, [Тип] TEXT(50), [Сумма] CURRENCY, [Дата] DATETIME)",
    "CREATE TABLE [Отзывы] ([КодОтзыва] AUTOINCREMENT PRIMARY KEY, [КодЗаказа] LONG, [Оценка] LONG, [Комментарий] MEMO, [ДатаОтзыва] DATETIME)"
]
for q in s3:
    cur.execute(q)

conn.commit()
conn.close()
print("12 русских таблиц созданы!")
