import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_connection

app = Flask(__name__)
app.secret_key = "masterhub_secret_key"

def current_user():
    if "user_id" not in session:
        return None
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT [КодПользователя], [Логин], [Email], [КодРоли], [Баланс], [Заблокирован] FROM [Пользователи] WHERE [КодПользователя] = ?", (session["user_id"],))
    row = cur.fetchone()
    conn.close()
    if not row or row.Заблокирован:
        session.clear()
        return None
    return {"id": row.КодПользователя, "login": row.Логин, "email": row.Email, "role": row.КодРоли, "balance": float(row.Баланс)}

@app.context_processor
def inject_user():
    return {"user": current_user()}

@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    dir_id = request.args.get("dir_id", "")
    level_id = request.args.get("level_id", "")
    sort = request.args.get("sort", "new")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT [КодНаправления] AS DirID, [Название] AS DirName FROM [Направления]")
    directions = cur.fetchall()
    cur.execute("SELECT [КодУровня] AS LevelID, [Название] AS LevelName FROM [УровниСпециалиста]")
    levels = cur.fetchall()

    sql = """
        SELECT a.[КодОбъявления] AS AdID, s.[Название] AS Title, s.[Описание] AS Description,
               a.[Цена] AS Price, a.[Слоты] AS Slots, a.[СрокДней] AS Days,
               d.[Название] AS DirName, c.[Название] AS CatName, l.[Название] AS LevelName, u.[Логин] AS SellerLogin
        FROM ((((([Объявления] a
        INNER JOIN [Услуги] s ON a.[КодУслуги] = s.[КодУслуги])
        INNER JOIN [Направления] d ON s.[КодНаправления] = d.[КодНаправления])
        INNER JOIN [Категории] c ON s.[КодКатегории] = c.[КодКатегории])
        INNER JOIN [УровниСпециалиста] l ON s.[КодУровня] = l.[КодУровня])
        INNER JOIN [Пользователи] u ON a.[КодИсполнителя] = u.[КодПользователя])
        WHERE a.[КодСтатуса] = 1 AND a.[Слоты] > 0
    """
    params = []
    if q:
        sql += " AND (s.[Название] LIKE ? OR s.[Описание] LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    if dir_id.isdigit():
        sql += " AND s.[КодНаправления] = ?"
        params.append(int(dir_id))
    if level_id.isdigit():
        sql += " AND s.[КодУровня] = ?"
        params.append(int(level_id))

    if sort == "cheap":
        sql += " ORDER BY a.[Цена] ASC"
    elif sort == "expensive":
        sql += " ORDER BY a.[Цена] DESC"
    else:
        sql += " ORDER BY a.[КодОбъявления] DESC"

    cur.execute(sql, params)
    ads = cur.fetchall()
    conn.close()
    return render_template("index.html", ads=ads, directions=directions, levels=levels, q=q, dir_id=dir_id, level_id=level_id, sort=sort)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_val = request.form.get("login", "").strip()
        pwd = request.form.get("password", "").strip()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT [КодПользователя], [Заблокирован] FROM [Пользователи] WHERE [Логин] = ? AND [Пароль] = ?", (login_val, pwd))
        row = cur.fetchone()
        conn.close()
        if not row:
            flash("Неверный логин или пароль", "danger")
        elif row.Заблокирован:
            flash("Ваш аккаунт заблокирован администратором", "danger")
        else:
            session["user_id"] = row.КодПользователя
            return redirect(url_for("index"))
    return render_template("auth.html", mode="login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login_val = request.form.get("login", "").strip()
        email = request.form.get("email", "").strip()
        pwd = request.form.get("password", "").strip()
        role_id = int(request.form.get("role_id", 1))
        if role_id not in (1, 2):
            role_id = 1
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT [КодПользователя] FROM [Пользователи] WHERE [Логин] = ?", (login_val,))
        if cur.fetchone():
            flash("Такой логин уже занят", "danger")
            conn.close()
            return render_template("auth.html", mode="register")
        cur.execute(
            "INSERT INTO [Пользователи] ([Логин], [Email], [Пароль], [КодРоли], [Баланс], [ДатаРегистрации], [Заблокирован]) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (login_val, email, pwd, role_id, 5000, datetime.datetime.now(), False)
        )
        conn.commit()
        conn.close()
        flash("Регистрация успешна! Начислен стартовый бонус 5000 ₽. Войдите в аккаунт.", "success")
        return redirect(url_for("login"))
    return render_template("auth.html", mode="register")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
@app.route("/service/<int:ad_id>", methods=["GET", "POST"])
def service_detail(ad_id):
    user = current_user()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.[КодОбъявления] AS AdID, a.[КодИсполнителя] AS SellerID, s.[Название] AS Title, s.[Описание] AS Description,
               a.[Цена] AS Price, a.[Слоты] AS Slots, a.[СрокДней] AS Days,
               d.[Название] AS DirName, c.[Название] AS CatName, l.[Название] AS LevelName, u.[Логин] AS SellerLogin
        FROM ((((([Объявления] a
        INNER JOIN [Услуги] s ON a.[КодУслуги] = s.[КодУслуги])
        INNER JOIN [Направления] d ON s.[КодНаправления] = d.[КодНаправления])
        INNER JOIN [Категории] c ON s.[КодКатегории] = c.[КодКатегории])
        INNER JOIN [УровниСпециалиста] l ON s.[КодУровня] = l.[КодУровня])
        INNER JOIN [Пользователи] u ON a.[КодИсполнителя] = u.[КодПользователя])
        WHERE a.[КодОбъявления] = ?
    """, (ad_id,))
    ad = cur.fetchone()
    if not ad:
        conn.close()
        return "Услуга не найдена", 404

    if request.method == "POST":
        if not user:
            conn.close()
            return redirect(url_for("login"))
        if user["id"] == ad.SellerID:
            flash("Нельзя заказать собственную услугу", "warning")
        elif ad.Slots < 1:
            flash("Свободных мест больше нет", "danger")
        elif user["balance"] < float(ad.Price):
            flash("Недостаточно средств на балансе", "danger")
        else:
            comment = request.form.get("comment", "").strip()
            now = datetime.datetime.now()
            cur.execute("UPDATE [Пользователи] SET [Баланс] = [Баланс] - ? WHERE [КодПользователя] = ?", (ad.Price, user["id"]))
            cur.execute("UPDATE [Объявления] SET [Слоты] = [Слоты] - 1 WHERE [КодОбъявления] = ?", (ad_id,))
            cur.execute(
                "INSERT INTO [Заказы] ([КодЗаказчика], [КодОбъявления], [Количество], [Сумма], [Комментарий], [ДатаЗаказа], [КодСтатуса]) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user["id"], ad_id, 1, ad.Price, comment, now, 1)
            )
            cur.execute("SELECT @@IDENTITY")
            order_id = int(cur.fetchone()[0])
            cur.execute(
                "INSERT INTO [Транзакции] ([КодПользователя], [КодЗаказа], [Тип], [Сумма], [Дата]) VALUES (?, ?, ?, ?, ?)",
                (user["id"], order_id, "Оплата заказа (заморозка)", -float(ad.Price), now)
            )
            conn.commit()
            conn.close()
            flash("Заказ оплачен! Деньги заморожены до выполнения работы.", "success")
            return redirect(url_for("profile"))

    cur.execute("""
        SELECT r.[Оценка] AS Rating, r.[Комментарий] AS Comment, r.[ДатаОтзыва] AS ReviewDate, u.[Логин] AS Login
        FROM (([Отзывы] r
        INNER JOIN [Заказы] o ON r.[КодЗаказа] = o.[КодЗаказа])
        INNER JOIN [Пользователи] u ON o.[КодЗаказчика] = u.[КодПользователя])
        WHERE o.[КодОбъявления] = ?
        ORDER BY r.[КодОтзыва] DESC
    """, (ad_id,))
    reviews = cur.fetchall()
    conn.close()
    return render_template("service.html", ad=ad, reviews=reviews)

@app.route("/profile")
def profile():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT o.[КодЗаказа] AS OrderID, s.[Название] AS Title, o.[Сумма] AS TotalAmount, o.[Комментарий] AS Comment,
               o.[ДатаЗаказа] AS OrderDate, o.[КодСтатуса] AS StatusID, st.[Название] AS StatusName, u.[Логин] AS SellerLogin,
               (SELECT COUNT(*) FROM [Отзывы] r WHERE r.[КодЗаказа] = o.[КодЗаказа]) AS HasReview
        FROM (((([Заказы] o
        INNER JOIN [Объявления] a ON o.[КодОбъявления] = a.[КодОбъявления])
        INNER JOIN [Услуги] s ON a.[КодУслуги] = s.[КодУслуги])
        INNER JOIN [СтатусыЗаказов] st ON o.[КодСтатуса] = st.[КодСтатуса])
        INNER JOIN [Пользователи] u ON a.[КодИсполнителя] = u.[КодПользователя])
        WHERE o.[КодЗаказчика] = ?
        ORDER BY o.[КодЗаказа] DESC
    """, (user["id"],))
    my_purchases = cur.fetchall()

    cur.execute("""
        SELECT o.[КодЗаказа] AS OrderID, s.[Название] AS Title, o.[Сумма] AS TotalAmount, o.[Комментарий] AS Comment,
               o.[ДатаЗаказа] AS OrderDate, o.[КодСтатуса] AS StatusID, st.[Название] AS StatusName, u.[Логин] AS BuyerLogin
        FROM (((([Заказы] o
        INNER JOIN [Объявления] a ON o.[КодОбъявления] = a.[КодОбъявления])
        INNER JOIN [Услуги] s ON a.[КодУслуги] = s.[КодУслуги])
        INNER JOIN [СтатусыЗаказов] st ON o.[КодСтатуса] = st.[КодСтатуса])
        INNER JOIN [Пользователи] u ON o.[КодЗаказчика] = u.[КодПользователя])
        WHERE a.[КодИсполнителя] = ?
        ORDER BY o.[КодЗаказа] DESC
    """, (user["id"],))
    my_sales = cur.fetchall()

    cur.execute("""
        SELECT a.[КодОбъявления] AS AdID, s.[Название] AS Title, a.[Цена] AS Price, a.[Слоты] AS Slots, a.[СрокДней] AS Days, st.[Название] AS StatusName
        FROM (([Объявления] a
        INNER JOIN [Услуги] s ON a.[КодУслуги] = s.[КодУслуги])
        INNER JOIN [СтатусыОбъявлений] st ON a.[КодСтатуса] = st.[КодСтатуса])
        WHERE a.[КодИсполнителя] = ?
        ORDER BY a.[КодОбъявления] DESC
    """, (user["id"],))
    my_ads = cur.fetchall()

    cur.execute("SELECT [Тип] AS TxType, [Сумма] AS Amount, [Дата] AS TxDate FROM [Транзакции] WHERE [КодПользователя] = ? ORDER BY [КодТранзакции] DESC", (user["id"],))
    txs = cur.fetchall()

    conn.close()
    return render_template("profile.html", my_purchases=my_purchases, my_sales=my_sales, my_ads=my_ads, txs=txs)

@app.route("/topup", methods=["POST"])
def topup():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    amount = float(request.form.get("amount", 0))
    if 0 < amount <= 100000:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE [Пользователи] SET [Баланс] = [Баланс] + ? WHERE [КодПользователя] = ?", (amount, user["id"]))
        cur.execute("INSERT INTO [Транзакции] ([КодПользователя], [КодЗаказа], [Тип], [Сумма], [Дата]) VALUES (?, ?, ?, ?, ?)",
                    (user["id"], None, "Пополнение демо-баланса", amount, datetime.datetime.now()))
        conn.commit()
        conn.close()
        flash(f"Баланс пополнен на {amount:.0f} ₽", "success")
    return redirect(url_for("profile"))
@app.route("/order/<int:order_id>/complete", methods=["POST"])
def complete_order(order_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.[КодЗаказа] AS OrderID, o.[Сумма] AS TotalAmount, o.[КодСтатуса] AS StatusID, a.[КодИсполнителя] AS SellerID
        FROM [Заказы] o INNER JOIN [Объявления] a ON o.[КодОбъявления] = a.[КодОбъявления]
        WHERE o.[КодЗаказа] = ?
    """, (order_id,))
    order = cur.fetchone()
    if order and order.StatusID == 1 and order.SellerID == user["id"]:
        now = datetime.datetime.now()
        cur.execute("UPDATE [Заказы] SET [КодСтатуса] = 2 WHERE [КодЗаказа] = ?", (order_id,))
        cur.execute("UPDATE [Пользователи] SET [Баланс] = [Баланс] + ? WHERE [КодПользователя] = ?", (order.TotalAmount, user["id"]))
        cur.execute("INSERT INTO [Транзакции] ([КодПользователя], [КодЗаказа], [Тип], [Сумма], [Дата]) VALUES (?, ?, ?, ?, ?)",
                    (user["id"], order_id, "Выплата за выполненный заказ", float(order.TotalAmount), now))
        conn.commit()
        flash("Заказ выполнен! Средства зачислены на ваш баланс.", "success")
    conn.close()
    return redirect(url_for("profile"))

@app.route("/order/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.[КодЗаказа] AS OrderID, o.[КодЗаказчика] AS BuyerID, o.[КодОбъявления] AS AdID,
               o.[Количество] AS Qty, o.[Сумма] AS TotalAmount, o.[КодСтатуса] AS StatusID, a.[КодИсполнителя] AS SellerID
        FROM [Заказы] o INNER JOIN [Объявления] a ON o.[КодОбъявления] = a.[КодОбъявления]
        WHERE o.[КодЗаказа] = ?
    """, (order_id,))
    order = cur.fetchone()
    if order and order.StatusID == 1 and (order.BuyerID == user["id"] or order.SellerID == user["id"]):
        now = datetime.datetime.now()
        cur.execute("UPDATE [Заказы] SET [КодСтатуса] = 3 WHERE [КодЗаказа] = ?", (order_id,))
        cur.execute("UPDATE [Пользователи] SET [Баланс] = [Баланс] + ? WHERE [КодПользователя] = ?", (order.TotalAmount, order.BuyerID))
        cur.execute("UPDATE [Объявления] SET [Слоты] = [Слоты] + ? WHERE [КодОбъявления] = ?", (order.Qty, order.AdID))
        cur.execute("INSERT INTO [Транзакции] ([КодПользователя], [КодЗаказа], [Тип], [Сумма], [Дата]) VALUES (?, ?, ?, ?, ?)",
                    (order.BuyerID, order_id, "Возврат средств при отмене заказа", float(order.TotalAmount), now))
        conn.commit()
        flash("Заказ отменен, средства возвращены заказчику.", "info")
    conn.close()
    return redirect(url_for("profile"))

@app.route("/order/<int:order_id>/review", methods=["POST"])
def add_review(order_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    rating = int(request.form.get("rating", 5))
    comment = request.form.get("comment", "").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT [КодЗаказа] FROM [Заказы] WHERE [КодЗаказа] = ? AND [КодЗаказчика] = ? AND [КодСтатуса] = 2", (order_id, user["id"]))
    if cur.fetchone():
        cur.execute("SELECT [КодОтзыва] FROM [Отзывы] WHERE [КодЗаказа] = ?", (order_id,))
        if not cur.fetchone():
            cur.execute("INSERT INTO [Отзывы] ([КодЗаказа], [Оценка], [Комментарий], [ДатаОтзыва]) VALUES (?, ?, ?, ?)",
                        (order_id, rating, comment, datetime.datetime.now()))
            conn.commit()
            flash("Спасибо за отзыв!", "success")
    conn.close()
    return redirect(url_for("profile"))

@app.route("/create_ad", methods=["GET", "POST"])
def create_ad():
    user = current_user()
    if not user or user["role"] not in (2, 3):
        flash("Создавать услуги могут только исполнители", "warning")
        return redirect(url_for("index"))
    conn = get_connection()
    cur = conn.cursor()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        desc = request.form.get("description", "").strip()
        dir_id = int(request.form.get("dir_id", 1))
        cat_id = int(request.form.get("cat_id", 1))
        level_id = int(request.form.get("level_id", 2))
        price = float(request.form.get("price", 1000))
        slots = int(request.form.get("slots", 3))
        days = int(request.form.get("days", 3))

        cur.execute("INSERT INTO [Услуги] ([КодНаправления], [КодКатегории], [КодУровня], [Название], [Описание], [URLИзображения]) VALUES (?, ?, ?, ?, ?, ?)",
                    (dir_id, cat_id, level_id, title, desc, ""))
        cur.execute("SELECT @@IDENTITY")
        srv_id = int(cur.fetchone())
        cur.execute("INSERT INTO [Объявления] ([КодИсполнителя], [КодУслуги], [Цена], [Слоты], [СрокДней], [КодСтатуса], [ДатаСоздания]) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user["id"], srv_id, price, slots, days, 1, datetime.datetime.now()))
        conn.commit()
        conn.close()
        flash("Объявление опубликовано в каталоге!", "success")
        return redirect(url_for("profile"))

    cur.execute("SELECT [КодНаправления] AS DirID, [Название] AS DirName FROM [Направления]")
    directions = cur.fetchall()
    cur.execute("SELECT [КодКатегории] AS CatID, [КодНаправления] AS DirID, [Название] AS CatName FROM [Категории]")
    categories = cur.fetchall()
    cur.execute("SELECT [КодУровня] AS LevelID, [Название] AS LevelName FROM [УровниСпециалиста]")
    levels = cur.fetchall()
    conn.close()
    return render_template("create_ad.html", directions=directions, categories=categories, levels=levels)

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    user = current_user()
    if not user or user["role"] != 3:
        return "Доступ запрещен", 403
    conn = get_connection()
    cur = conn.cursor()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "toggle_block":
            uid = int(request.form.get("user_id"))
            if uid != user["id"]:
                cur.execute("UPDATE [Пользователи] SET [Заблокирован] = NOT [Заблокирован] WHERE [КодПользователя] = ?", (uid,))
        elif action == "hide_ad":
            aid = int(request.form.get("ad_id"))
            cur.execute("UPDATE [Объявления] SET [КодСтатуса] = 2 WHERE [КодОбъявления] = ?", (aid,))
        conn.commit()

    cur.execute("SELECT u.[КодПользователя] AS UserID, u.[Логин] AS Login, u.[Email] AS Email, r.[Название] AS RoleName, u.[Баланс] AS Balance, u.[Заблокирован] AS IsBlocked FROM [Пользователи] u INNER JOIN [Роли] r ON u.[КодРоли] = r.[КодРоли]")
    users = cur.fetchall()
    cur.execute("""
        SELECT a.[КодОбъявления] AS AdID, s.[Название] AS Title, u.[Логин] AS Login, a.[Цена] AS Price, st.[Название] AS StatusName
        FROM ((([Объявления] a INNER JOIN [Услуги] s ON a.[КодУслуги] = s.[КодУслуги])
        INNER JOIN [Пользователи] u ON a.[КодИсполнителя] = u.[КодПользователя])
        INNER JOIN [СтатусыОбъявлений] st ON a.[КодСтатуса] = st.[КодСтатуса])
    """)
    ads = cur.fetchall()
    conn.close()
    return render_template("admin.html", users=users, ads=ads)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
