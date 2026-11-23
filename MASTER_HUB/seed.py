import datetime
from db import get_connection

def seed():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Роли
    for r in ["Заказчик", "Исполнитель", "Администратор"]:
        cur.execute("INSERT INTO Roles (RoleName) VALUES (?)", (r,))

    # 2. Уровни специалиста
    for l in ["Начинающий", "Специалист", "Эксперт"]:
        cur.execute("INSERT INTO Levels (LevelName) VALUES (?)", (l,))

    # 3. Статусы объявлений и заказов
    for s in ["Активно", "Снято"]:
        cur.execute("INSERT INTO AdStatuses (StatusName) VALUES (?)", (s,))
    for s in ["Оплачен", "Выполнен", "Отменен"]:
        cur.execute("INSERT INTO OrderStatuses (StatusName) VALUES (?)", (s,))

    # 4. Направления и категории
    dirs = [
        ("Программирование", ["Сайты на Python", "Telegram-боты", "Базы данных"]),
        ("Дизайн", ["Логотипы", "Веб-дизайн", "Презентации"]),
        ("Репетиторство", ["Математика", "Английский язык", "Информатика"])
    ]
    for d_name, cats in dirs:
        cur.execute("INSERT INTO Directions (DirName) VALUES (?)", (d_name,))
        cur.execute("SELECT @@IDENTITY")
        dir_id = int(cur.fetchone()[0])
        for c_name in cats:
            cur.execute("INSERT INTO Categories (DirID, CatName) VALUES (?, ?)", (dir_id, c_name))

    # 5. Пользователи (пароли открытым текстом для удобной демонстрации)
    now = datetime.datetime.now()
    users = [
        ("admin", "admin@masterhub.ru", "admin123", 3, 50000),
        ("alex_dev", "alex@masterhub.ru", "12345", 2, 12000),
        ("maria_art", "maria@masterhub.ru", "12345", 2, 8500),
        ("ivan_client", "ivan@masterhub.ru", "12345", 1, 25000)
    ]
    for login, email, pwd, role_id, bal in users:
        cur.execute(
            "INSERT INTO Users (Login, Email, PasswordHash, RoleID, Balance, RegDate, IsBlocked) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (login, email, pwd, role_id, bal, now, False)
        )

    # 6. Услуги и объявления (кворки)
    demo_ads = [
        (1, 2, 3, "Telegram-бот под ключ на Python", "Разработка бота с подключением к базе данных и админ-панелью.", 2, 4500, 3, 3),
        (1, 1, 2, "Верстка лендинга или сайта на Flask", "Адаптивный сайт на Bootstrap 5 с формой заявки.", 2, 6000, 2, 5),
        (2, 4, 3, "Минималистичный логотип и фирменный стиль", "3 концепции на выбор, исходники в векторе.", 3, 3000, 5, 2),
        (3, 9, 2, "Подготовка к ЕГЭ и ОГЭ по информатике", "Индивидуальное занятие 60 минут, разбор второй части.", 3, 1500, 10, 1)
    ]
    for d_id, c_id, l_id, title, desc, seller_id, price, slots, days in demo_ads:
        cur.execute(
            "INSERT INTO Services (DirID, CatID, LevelID, Title, Description, ImageURL) VALUES (?, ?, ?, ?, ?, ?)",
            (d_id, c_id, l_id, title, desc, "")
        )
        cur.execute("SELECT @@IDENTITY")
        srv_id = int(cur.fetchone()[0])
        cur.execute(
            "INSERT INTO Ads (SellerID, ServiceID, Price, Slots, Days, StatusID, CreatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (seller_id, srv_id, price, slots, days, 1, now)
        )

    conn.commit()
    conn.close()
    print("Демо-данные и справочники успешно добавлены!")

if __name__ == "__main__":
    seed()
