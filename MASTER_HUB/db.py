import os
import pyodbc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.accdb")

def get_connection():
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={DB_PATH};"
    )
    return pyodbc.connect(conn_str, autocommit=True)
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    tables = [
        "CREATE TABLE Roles (RoleID AUTOINCREMENT PRIMARY KEY, RoleName TEXT(50))",
        "CREATE TABLE Directions (DirID AUTOINCREMENT PRIMARY KEY, DirName TEXT(100))",
        "CREATE TABLE Categories (CatID AUTOINCREMENT PRIMARY KEY, DirID LONG, CatName TEXT(100))",
        "CREATE TABLE Levels (LevelID AUTOINCREMENT PRIMARY KEY, LevelName TEXT(50))",
        "CREATE TABLE AdStatuses (StatusID AUTOINCREMENT PRIMARY KEY, StatusName TEXT(50))",
        "CREATE TABLE OrderStatuses (StatusID AUTOINCREMENT PRIMARY KEY, StatusName TEXT(50))",
        """CREATE TABLE Users (
            UserID AUTOINCREMENT PRIMARY KEY,
            Login TEXT(50),
            Email TEXT(100),
            PasswordHash TEXT(255),
            RoleID LONG,
            Balance CURRENCY,
            RegDate DATETIME,
            IsBlocked YESNO
        )""",
        """CREATE TABLE Services (
            ServiceID AUTOINCREMENT PRIMARY KEY,
            DirID LONG,
            CatID LONG,
            LevelID LONG,
            Title TEXT(150),
            Description MEMO,
            ImageURL TEXT(255)
        )""",
        """CREATE TABLE Ads (
            AdID AUTOINCREMENT PRIMARY KEY,
            SellerID LONG,
            ServiceID LONG,
            Price CURRENCY,
            Slots LONG,
            Days LONG,
            StatusID LONG,
            CreatedAt DATETIME
        )""",
        """CREATE TABLE Orders (
            OrderID AUTOINCREMENT PRIMARY KEY,
            BuyerID LONG,
            AdID LONG,
            Qty LONG,
            TotalAmount CURRENCY,
            Comment MEMO,
            OrderDate DATETIME,
            StatusID LONG
        )""",
        """CREATE TABLE Transactions (
            TxID AUTOINCREMENT PRIMARY KEY,
            UserID LONG,
            OrderID LONG,
            TxType TEXT(50),
            Amount CURRENCY,
            TxDate DATETIME
        )""",
        """CREATE TABLE Reviews (
            ReviewID AUTOINCREMENT PRIMARY KEY,
            OrderID LONG,
            Rating LONG,
            Comment MEMO,
            ReviewDate DATETIME
        )"""
    ]

    for sql in tables:
        try:
            cur.execute(sql)
        except Exception as e:
            print("Пропуск (возможно, таблица уже есть):", e)

    conn.commit()
    conn.close()
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    init_db()