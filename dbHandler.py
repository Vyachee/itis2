import os
import sqlite3

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

con = db_connect()
cur = con.cursor()

def createGoodsTable():
    goods_table = """
    CREATE TABLE IF NOT EXISTS "goods" (
        "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
        "goodname"	TEXT NOT NULL,
        "categorie"	TEXT NOT NULL
    )"""
    cur.execute(goods_table)

def createTransactionsTable():
    transactions_table = """
    CREATE TABLE IF NOT EXISTS "transactions" (
        "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
        "date"  TEXT NOT NULL,
        "goodsid"	INTEGER NOT NULL,
        "amount"	INTEGER NOT NULL,
        "cartid"	INTEGER NOT NULL,
        "ip"	TEXT NOT NULL
    )"""
    cur.execute(transactions_table)

def createActionsTable():
    actions_table = """
    CREATE TABLE IF NOT EXISTS "actions" (
        "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
        "action"	TEXT NOT NULL,
        "ip"	INTEGER NOT NULL,
        "date"  TEXT NOT NULL,
        "country" TEXT NOT NULL
    )
    """
    cur.execute(actions_table)


def createGoodsItem(goodName, categorie):
    goods_item = """
    INSERT INTO "goods" (
        "goodname", "categorie"
    ) 
    VALUES (
        ?, ?
    )"""
    cur.execute(goods_item, (goodName, categorie))

def createTransactionItem(date, goodId, amount, cartId, ip):
    transactionItem = """
    INSERT INTO "transactions" (
        "date", "goodsid", "amount", "cartid", "ip"
    ) 
    VALUES (
        ?, ?, ?, ?, ?
    )"""
    cur.execute(transactionItem, (date, goodId, amount, cartId, ip))

def createActionItem(date, action, ip, country):
    actionitem = """
    INSERT INTO "actions" (
        "action", "ip", "date", "country"
    ) 
    VALUES (
        ?, ?, ?, ?
    )"""
    cur.execute(actionitem, (action, ip, date, country))


def save():
    con.commit()
    con.close()