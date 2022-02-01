import sys		# sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QCursor

import design	# конвертированный файл дизайна

COUNT = 10
WIN_COUNT = 5
SIZE = 50


# ----------------------------------------------------
#       Кастом класс для рисования виджета с ХО 
# 
class Example_Text(QWidget):
    theSignal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        

    def initUI(self):
        # turn 1/0 === X/O.  Initial = O
        self.turn = 0
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        # Основное игровое поле
        self.field = [[-1 for x in range(COUNT)] for y in range(COUNT)] 
        self.setGeometry(SIZE*COUNT + 2, SIZE*COUNT + 2, 0, 0)
        self.show()
        

    # Событие перерисовки виджета
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawGridLines(event, qp)
        self.drawXO(event, qp)
        qp.end()

    # Рисование игровой сетки
    def drawGridLines(self, event, qp):
        qp.setPen(Qt.black)
        for i in range (COUNT):
            for j in range (COUNT):
                qp.drawRect(SIZE*i + 1, SIZE*j + 1, SIZE, SIZE)

    # Рисование ХО
    def drawXO(self, event, qp):
        for i in range (COUNT):
            for j in range (COUNT):
                # Рисование O
                if (self.field[i][j] == 0):
                    qp.setPen(Qt.green)
                    qp.drawEllipse(SIZE*i + 11, SIZE*j + 11, (SIZE-20), (SIZE-20))
                # Рисование X
                elif (self.field[i][j] == 1):
                    qp.setPen(Qt.red)
                    qp.drawLine(SIZE*i + 11, SIZE*j + 11, SIZE*i + (SIZE-9), SIZE*j + (SIZE-9))
                    qp.drawLine(SIZE*i + 11, SIZE*j + (SIZE-9), SIZE*i + (SIZE-9), SIZE*j + 11)

    # Обработчик нажатия на мышку
    def mousePressEvent(self, event):
        # Ищем индексы нажатой клетки
        x_ind = int((event.localPos().x()-1)/SIZE)
        y_ind = int((event.localPos().y()-1)/SIZE)
        if (x_ind in range (COUNT) and y_ind in range (COUNT)):
            # Если поле пустое, ставим в него Х или О
            if (self.field[x_ind][y_ind] == -1):
                self.field[x_ind][y_ind] = self.turn

                # Проверка на победителя после очередного хода
                result = self.checkWinner()

                # Выдача результатов в случае если победили Крестики или Нолики
                if (result == 1):
                    reTurn = self.turn
                    winners = "Нолики"
                    if (self.turn == 1):
                        winners = "Крестики"

                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Игра окончена")
                    msg.setText(f'Победили {winners}')
                    msg.exec_()

                    self.gameReset()
                    self.theSignal.emit(reTurn)
                    return
                
                # Выдача результатов в случае ничьей
                if (result == 2):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Игра окончена")
                    msg.setText("Ничья :)")
                    msg.exec_()
                    self.gameReset()
                    self.theSignal.emit(2)
                    return

                # Смена очерёдности хода и вида курсора(Рука для ноликов и Кретик для крестиков)
                if (self.turn == 1):
                    self.turn = 0
                    self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
                else:
                    self.turn = 1
                    self.setCursor(QCursor(QtCore.Qt.CrossCursor))

                self.update()


    # Проверяет победителя
    def checkWinner(self):
        # game field
        gf = self.field
        turn = self.turn
        empty_counter = 0
        for i in range (COUNT):
            for j in range (COUNT):
                # Начинаем проверку только в клетках содержащих текущую актуальную фигуру
                if (gf[i][j] == turn):
                    # переменная для подсчёта кол-ва "правильных" клеток в ряд
                    
                    # 1. Проверка для каждой клетки игрового поля вниз
                    in_line = 1
                    for k in range (1, WIN_COUNT):
                        # next value of j
                        n = j + k
                        if (n >= COUNT) or (gf[i][n] != turn):
                            break
                        in_line = in_line + 1
                    if (in_line == WIN_COUNT):
                        return 1

                    # 2. Проверка для каждой клетки игрового поля вправо
                    in_line = 1
                    for k in range (1, WIN_COUNT):
                        # next value of i
                        n = i + k
                        if (n >= COUNT) or (gf[n][j] != turn):
                            break
                        in_line = in_line + 1
                    if (in_line == WIN_COUNT):
                        return 1

                    # 3. Проверка для каждой клетки игрового поля вниз и вправо
                    in_line = 1
                    for k in range (1, WIN_COUNT):
                        # next value of i
                        ni = i + k
                        # next value of j
                        nj = j + k
                        if (ni >= COUNT) or (nj >= COUNT) or (gf[ni][nj] != turn):
                            break
                        in_line = in_line + 1
                    if (in_line == WIN_COUNT):
                        return 1

                    # 4. Проверка для каждой клетки игрового поля вверх и вправо
                    in_line = 1
                    for k in range (1, WIN_COUNT):
                        # next value of i
                        ni = i + k
                        # next value of j
                        nj = j - k
                        if (ni >= COUNT) or (nj < 0) or (gf[ni][nj] != turn):
                            break
                        in_line = in_line + 1
                    if (in_line == WIN_COUNT):
                        return 1

                # Считаем пустые клетки на поле для обозначения ничьей 
                elif (gf[i][j] == -1):
                    empty_counter = empty_counter + 1
        if (empty_counter == 0):
            return 2
        return 0


    def gameReset(self):
        self.field = [[-1 for x in range(COUNT)] for y in range(COUNT)] 
        self.turn = 0
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.update()

# ----------------------------------------------------


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    resetSignal = QtCore.pyqtSignal()

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)      # Это нужно для инициализации нашего дизайна
        self.initUiComponents() # Инициализация привязок к элементам главного окна


    # Инициализируем все компоненты находящиеся на экране
    def initUiComponents(self):
        # Добавление виджета рисования текста в QFrame->HorizontalLayout_2
        self.textWidget = Example_Text(self)
        self.horizontalLayout_2.addWidget(self.textWidget)
        self.showMain()

        self.createConnection() # Соединение с БД
        self.createModel()      # Создание модели для работы с БД
        self.tableView.setModel(self.model) 
        self.tableView.hideColumn(0)   # Скрываем столбец с id
        self.labelRules.setText('''
        Крестики-нолики — логическая игра между двумя противниками\n
        на квадратном поле 10 на 10 клеток.\n
        Один из игроков играет «крестиками», второй — «ноликами».\n
        Игроки по очереди ставят на свободные клетки поля 10x10 знаки \n
        (один всегда крестики, другой всегда нолики). Первый, выстроивший\n
        в ряд 5 своих фигур по вертикали, горизонтали или диагонали, выигрывает.\n
        Первый ход делает игрок, ставящий нолики. ''')

        # Связываем сигналы и слоты текущего и дочернего классов
        self.textWidget.theSignal.connect(self.theSlot)
        self.resetSignal.connect(self.textWidget.gameReset)
        # Обработчики нажатий различных кнопок
        self.btnNew.clicked.connect(self.showGame)
        self.btnRules.clicked.connect(self.showRules)
        self.btnRecords.clicked.connect(self.showRecords)
        self.btnMenu.clicked.connect(self.showMain)
        self.btnMenu2.clicked.connect(self.showMain)
        self.btnMenu3.clicked.connect(self.showMain)
        self.btnOk.clicked.connect(self.checkNames)
        self.btnCancel.clicked.connect(self.showMain)

    # Подключение к базе данных
    # В случае неудачи появится messageBox с ошибкой
    def createConnection(self):
        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName("players_database.db")
        if not con.open():
            QMessageBox.critical(None, "QTableView Example - Error!",
                                 "Database Error: %s" % con.lastError().databasetext(), )
            return False
        return True

    # Создание модели для работы с базой данных
    def createModel(self):
        self.model = QSqlTableModel()
        self.model.setTable('players')  # Привязываем имя таблицы к модели
        # Переименовываем отображение заголовков столбцов
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, 'Имя')
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, 'Побед')
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, 'Поражений')
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, 'Ничьих')
        self.model.select()

    # Основные запросы к Базе Данных
    def getQuery(self, theName = 'Nobody', result = 77):
        query = QSqlQuery()
        # Запрос на поиск указанного имени в таблице БД
        query.exec(f"""SELECT * FROM players WHERE name = '{theName}'""")

        # Обновляем уже существующего игрока в зависимости от результата игры
        if (query.first()):
            wins = query.value(2)
            loses = query.value(3)
            draws = query.value(4)
            
            queryUpdate = QSqlQuery()
            if (result == 1):
                wins = wins + 1
                # Запрос с обновлением текущей записи в таблице
                queryUpdate.exec(f"""UPDATE players SET Win='{wins}' where name='{theName}'""")
            elif (result == 0):
                loses = loses + 1
                queryUpdate.exec(f"""UPDATE players SET Lose='{loses}' where name='{theName}'""")
            elif (result == 2):
                draws = draws + 1
                queryUpdate.exec(f"""UPDATE players SET Draw='{draws}' where name='{theName}'""")

        # Создаём запись в таблице для нового игрока если до этого такое имя не встречалось
        else:
            wins = 0
            loses = 0
            draws = 0
            if (result == 1):
                wins = 1
            elif (result == 0):
                loses = 1
            elif (result == 2):
                draws = 1
            
            queryInsert = QSqlQuery()
            # Запрос с созданием новой записи в таблицу БД
            queryInsert.exec(f"""INSERT INTO players (name, win, lose, draw) VALUES ('{theName}', '{wins}', '{loses}', '{draws}')""")
        
        self.model.select()
        self.showRecords()

    # Проверяем введённые имена игроков
    def checkNames(self):
        nameX = self.lineEditX.text().strip()
        nameO = self.lineEditO.text().strip()

        # Если одно из полей пустое - выдаётся предупреждение
        if (nameX == "" or nameO == ""):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Ошибка в именах")
            msg.setText("Имена не должны быть пустыми")
            msg.exec_()
            return

        # Если имена совпадают - выдаётся предупреждение
        if (nameX == nameO):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Ошибка в именах")
            msg.setText("Имена не должны совпадать")
            msg.exec_()
            return

        # Если имена введены корректно, отправляем запросы к БД на
        # обновление текущей записи или добавление новой
        if (self.game_result == 1):
            self.getQuery(nameX, 1)
            self.getQuery(nameO, 0)
        elif (self.game_result == 0):
            self.getQuery(nameX, 0)
            self.getQuery(nameO, 1) 
        else:
            self.getQuery(nameX, 2)
            self.getQuery(nameO, 2)  


    # Слот вызывается когда от виджета с игрой приходит сигнал окончания игры
    def theSlot(self, value):
        self.game_result = value
        self.showPlayers()
    
    # Отображение главного экрана - приветствия
    def showMain(self):
        self.setMinHeight()
        self.frameMain.show()
        self.frameGame.hide()
        self.frameRules.hide()
        self.frameRecords.hide()
        self.framePlayers.hide()
        self.lineEditO.clear()
        self.lineEditX.clear()
        self.resetSignal.emit()

    # Отображение игрового поля
    def showGame(self):
        self.resize(523, 570)
        self.frameMain.hide()
        self.frameGame.show()
        self.frameRules.hide()
        self.frameRecords.hide()
        self.framePlayers.hide()

    # Отображение правил игры
    def showRules(self):
        self.setMaxHeight()
        self.frameMain.hide()
        self.frameGame.hide()
        self.frameRules.show()
        self.frameRecords.hide()
        self.framePlayers.hide()

    # Отображение рекордов
    def showRecords(self):
        self.setMaxHeight()
        self.frameMain.hide()
        self.frameGame.hide()
        self.frameRules.hide()
        self.frameRecords.show()
        self.framePlayers.hide()

    # Отображение окна для ввода имени игроков
    def showPlayers(self):
        self.setMinHeight()
        self.frameMain.hide()
        self.frameGame.hide()
        self.frameRules.hide()
        self.frameRecords.hide()
        self.framePlayers.show()

    # Установка минимальной высоты отображаемого окна
    def setMinHeight(self):
        self.resize(523, 200)

    # Установка максимальной высоты отображаемого окна
    def setMaxHeight(self):
        self.resize(523, 525)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()   # Создаём объект класса ExampleApp
    window.show()           # Показываем окно
    app.exec_()             # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
