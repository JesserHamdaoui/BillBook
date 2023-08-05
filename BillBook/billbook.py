import sqlite3
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from datetime import datetime

conn = sqlite3.connect('billbook.db')
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS books(
        ISBN TEXT,
        title TEXT,
        author TEXT,
        price REAL
    );
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        name TEXT,
        VAT_code TEXT,
        Adress TEXT
    );
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT,
        password TEXT,
        birth_date TEXT
    );
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS invoices(
        number TEXT,
        client TEXT,
        date TEXT,
        books TEXT,
        qte TEXT,
        total REAL
    );
""")

conn.commit()




#---------------------------Main Window---------------------------
def login():
    user_name = window.userNameInput.text()
    password = window.passwordInput.text()
    c.execute("SELECT password FROM users WHERE username = ?",(user_name,))
    passwordToCheck = c.fetchone()
    if not passwordToCheck:
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText('There is no user with this user name.')
        error.setWindowTitle('Error')
        error.exec_()
        window.userNameInput.clear()
        window.passwordInput.clear()
        return False
    elif passwordToCheck[0] != password:
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText('This password is wrong.')
        error.setWindowTitle('Error')
        error.exec_()
        window.passwordInput.clear()
        return False
    else:
        messege = QMessageBox()
        messege.setIcon(QMessageBox.Information)
        messege.setText('You loged in successfuly.')
        messege.setWindowTitle('Login')
        messege.exec_()
        window.userNameInput.setEnabled(False)
        window.passwordInput.setEnabled(False)
        window.loginBtn.setEnabled(False)
        window.signinBtn.setEnabled(False)
        window.invoiceBtn.setEnabled(True)
        window.reportBtn.setEnabled(True)
        window.manageBookBtn.setEnabled(True)

def showGenerateInvoice():
    invoiceWindow.show()
    c.execute("SELECT number FROM invoices ORDER BY number DESC")
    previous_number = c.fetchone()
    if not previous_number:
        number = 1
    else:
        number = int([0]) + 1
    number = str(number)
    while len(number) != 4:
        number = '0' + number
    invoiceWindow.invoiceNumberText.setText('Invoice number: '+ number)
    today = datetime.now()
    date_string = today.strftime("%d/%m/%Y")
    invoiceWindow.dateText.setText(date_string)
    window.close()

def showReport():
    reportWindow.show()
    window.close()

def showManagenBooks():
    manageWindow.show()
    window.close()        

#---------------------------Sign in Window---------------------------

def signin():
    def validDate(date):
        if len(date) != 10:
            return False
        try:
            day, month, year = map(int, date.split('/'))

            if day < 1 or day > 31:
                return False
            if month < 1 or month > 12:
                return False
            if year < 0:
                return False

            if month in [2, 4, 6, 9, 11]:
                if day > 30:
                    return False
            elif month == 2:
                if day > 29:
                    return False
                if year % 4 != 0:
                    if day > 28:
                        return False
                else:
                    if (year % 100 == 0) and (year % 400 != 0):
                        if day > 28:
                            return False
            return True
        except:
            return False

    def usernameExistance(username):
        if username == "":
            return False
        c.execute("SELECT * FROM users WHERE username = ?",(username,))
        usersArray = c.fetchall()
        if len(usersArray) == 0:
            return False
        else:
            return True

    user_name = signWindow.userNameInput.text()
    if usernameExistance(user_name):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText('This username exist before.')
        error.setWindowTitle('Error')
        error.exec_()
        return False
    birth_date = signWindow.birthDateInput.text()
    if not validDate(birth_date):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText('This date is not valid.')
        error.setWindowTitle('Error')
        error.exec_()
        return False
    password = signWindow.passwordInput.text()
    re_password = signWindow.rePasswordInput.text()
    if password != re_password or password == "":
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText('There is an error with password.')
        error.setWindowTitle('Error')
        error.exec_()
        return False
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText('You signed in successfuly.')
    msg.setWindowTitle('Sign In')
    msg.exec_()

    c.execute("""
        INSERT INTO users (username, birth_date, password)
        VALUES (?, ?, ?)
    """,(user_name, birth_date, password))
    conn.commit()

    signWindow.close()


#---------------------------Generate invoice Window---------------------------

def showBookTab():
    addBookWindow.show()
    c.execute("SELECT * FROM books")
    booksArray = c.fetchall()
    for i in range(len(booksArray)):
        addBookWindow.bookTab.insertRow(i)
        addBookWindow.bookTab.setItem(i, 0, QTableWidgetItem(booksArray[i][0]))
        addBookWindow.bookTab.setItem(i, 1, QTableWidgetItem(booksArray[i][1]))
        addBookWindow.bookTab.setItem(i, 2, QTableWidgetItem(booksArray[i][2]))
        addBookWindow.bookTab.setItem(i, 3, QTableWidgetItem(str(booksArray[i][3])))

def deleteBook():
    pass

def confirmInvoice():
    pass

#---------------------------add a book to invoice Window---------------------------

def searchBooks():
    search = addBookWindow.searchInput.text()
    if not search:
        c.execute("SELECT * FROM books")
        booksArray = c.fetchall()
    else:
        addBookWindow.bookTab.setRowCount(0)
        search = '%' + search + '%'
        c.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", (search, search))
        booksArray = c.fetchall()
    for i in range(len(booksArray)):
        addBookWindow.bookTab.insertRow(i)
        addBookWindow.bookTab.setItem(i, 0, QTableWidgetItem(booksArray[i][0]))
        addBookWindow.bookTab.setItem(i, 1, QTableWidgetItem(booksArray[i][1]))
        addBookWindow.bookTab.setItem(i, 2, QTableWidgetItem(booksArray[i][2]))
        addBookWindow.bookTab.setItem(i, 3, QTableWidgetItem(str(booksArray[i][3])))

def addBookToInvoice():
    row = addBookWindow.bookTab.currentRow()
    newRow = invoiceWindow.bookTab.rowCount()
    for i in range(4):
        item = addBookWindow.bookTab.item(row, i)
        newItem = QTableWidgetItem(item.text())
        invoiceWindow.bookTab.setItem(newRow, i, newItem)
    addBookWindow.close()


app = QApplication([])
window = loadUi('USER_INTERFACES/main.ui')
signWindow = loadUi('USER_INTERFACES/sign_in.ui')
invoiceWindow = loadUi('USER_INTERFACES/generate_invoice.ui')
reportWindow = loadUi('USER_INTERFACES/report.ui')
manageWindow = loadUi('USER_INTERFACES/manage_books.ui')
addBookWindow = loadUi('USER_INTERFACES/add_book.ui')

window.signinBtn.clicked.connect(signWindow.show)
window.loginBtn.clicked.connect(login)
window.invoiceBtn.clicked.connect(showGenerateInvoice)
window.reportBtn.clicked.connect(showReport)
window.manageBookBtn.clicked.connect(showManagenBooks)

signWindow.signinBtn.clicked.connect(signin)

invoiceWindow.addBtn.clicked.connect(showBookTab)

addBookWindow.searchInput.textChanged.connect(searchBooks)
addBookWindow.addBtn.clicked.connect(addBookToInvoice)

window.show()
app.exec_()