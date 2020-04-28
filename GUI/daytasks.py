import  sys
from datetime import  date
from pydispatch import dispatcher


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from API.DayPlanner import DayPlanner
from API.Objects.Task import  Task
from GUI.widgets import TabWidget, LeftSideWidget, RightSideWidget

TASK_PICKED = 'task-picked'
DATE_PICKED = 'date-picked'

class TasksListItem(QListWidgetItem):
    def __init__(self,uuid, parent=None):
        super(TasksListItem, self).__init__(parent)
        self.uuid = uuid

class PickedTaskWidget(RightSideWidget):
    def __init__(self, parent=None):
        super(PickedTaskWidget, self).__init__(parent)
        self.__datachanged = False
        self.__editedtask = None
        self.hide()

    @property
    def editedtask(self):
        return self.__editedtask
    @editedtask.setter
    def editedtask(self,value):
        self.__editedtask = value

    def raisedatachanged(self):
        self.__datachanged = True
        self.editedtask.name = self.nameedit.text()
        self.editedtask.datetime = self.datetimeedit.dateTime().toPyDateTime()
        self.editedtask.description = self.descriptionedit.toPlainText()
        self.editedtask.done = True if self.isdoneedit.checkState()==2 else False
        print(self.editedtask.__str__())

    def initUI(self, layout : QFormLayout):
        namelabel = QLabel("Name: ")
        self.nameedit = QLineEdit()


        datetimelabel = QLabel("Date: ")
        self.datetimeedit = QDateTimeEdit()

        descriptionlabel = QLabel("Description: ")
        self.descriptionedit = QTextEdit()

        isdonelabel = QLabel("Is task done: ")
        self.isdoneedit = QCheckBox()
        self.isdoneedit.setTristate(on=False)

        self.cancelbutton = QPushButton("Cancel")
        self.cancelbutton.clicked.connect(self.hide)
        self.applybutton = QPushButton("Save")
        self.applybutton.clicked.connect(self.apply_button_clicked)

        buttonslayout = QHBoxLayout()

        layout.addRow(namelabel, self.nameedit)
        layout.addRow(datetimelabel, self.datetimeedit)
        layout.addRow(descriptionlabel, self.descriptionedit)
        layout.addRow(isdonelabel, self.isdoneedit)
        buttonslayout.addWidget(self.cancelbutton)
        buttonslayout.addWidget(self.applybutton)
        layout.addRow(buttonslayout)


    def updateItem(self, task:Task):
        self.editedtask = task

        self.nameedit.setText(task.name)
        self.datetimeedit.setDateTime(task.datetime)
        self.descriptionedit.setText(task.description)
        self.isdoneedit.setChecked(task.done)


        self.nameedit.textChanged.connect(self.raisedatachanged)
        self.datetimeedit.dateTimeChanged.connect(self.raisedatachanged)
        self.descriptionedit.textChanged.connect(self.raisedatachanged)
        self.isdoneedit.stateChanged.connect(self.raisedatachanged)

        self.show()

    def hide(self):
        try:
            self.nameedit.textChanged.disconnect()
            self.datetimeedit.dateTimeChanged.disconnect()
            self.descriptionedit.textChanged.disconnect()
            self.isdoneedit.stateChanged.disconnect()
            self.__datachanged = False
        except TypeError:
            print("not connected")
        super().hide()


    def apply_button_clicked(self):
        if self.__datachanged:
            print("SAVING DATA")
            self.__datachanged = False
            dp = DayPlanner()
            dp.save_task(self.editedtask)
            dispatcher.send(signal=DATE_PICKED, sender=self)
    def cancel_button_clicked(self):
        self.hide()

class DayTasksListWidget(LeftSideWidget):
    def __init__(self,parent=None):
        super(DayTasksListWidget, self).__init__(parent)
        self.__selectedtask  = None
        self.tasksListWidget.setSelectionMode(QAbstractItemView.ContiguousSelection)

    @property
    def selectedtask(self):
        return self.__selectedtask

    @selectedtask.setter
    def selectedtask(self, value):
        self.__selectedtask = value
        dispatcher.send(signal=TASK_PICKED, sender=self)

    def initUI(self, layout):

        # headLabel  = QLabel()
        # headLabel.setText("Today")
        # headLabel.setAlignment(Qt.AlignLeft)

        self.tasksListWidget = QListWidget()

        self.updateItems()

        self.tasksListWidget.itemClicked.connect(self.taskClicked)
        self.tasksListWidget.itemSelectionChanged.connect(self.selectionChanged)
        self.tasksListWidget.show()

        # layout.addWidget(headLabel)
        layout.addWidget(self.tasksListWidget)

    def selectionChanged(self):
        if len(self.tasksListWidget.selectedItems()) == 0:
            self.selectedtask = None

    def taskClicked(self):
        sender = self.sender()
        dp = DayPlanner()
        self.selectedtask = dp.find_task_by_uuid_str(sender.selectedItems()[0].uuid)


    def updateItems(self):
        dp = DayPlanner()
        current_date_tasks = dp.get_tasks_filtered_by_date(date.today())
        self.tasksListWidget.clear()

        for task in current_date_tasks:
            task_time = task.datetime.strftime("%H:%M")
            newItem = TasksListItem(task.uuid)
            newItem.setText(f"{task_time} {task.name}")
            self.tasksListWidget.addItem(newItem)

class DayTasksWidget(TabWidget):
    def __init__(self,parent=None):
        super(DayTasksWidget, self).__init__(parent)
        self.currentdate = date.today()

    @property
    def currentdate(self):
        return self.__curentdate
    @currentdate.setter
    def currentdate(self, value):
        self.__curentdate = value
        self.pickdatebutton.setText(self.__curentdate.__str__())


    def initUI(self,layout):
        self.leftside = DayTasksListWidget()
        self.rightside = PickedTaskWidget()
        layout.addWidget(self.leftside)
        layout.addWidget(self.rightside)


        dispatcher.connect(self.task_picked_handler, signal=TASK_PICKED, sender=dispatcher.Any)
        dispatcher.connect(self.date_picked_handler, signal=DATE_PICKED, sender=dispatcher.Any)

    def initHeader(self, headerlayout:QHBoxLayout):
        self.pickdatebutton = QPushButton()
        
        headerlayout.addWidget(self.pickdatebutton)

    def task_picked_handler(self,sender):
        if(sender.selectedtask != None):
            self.rightside.hide()
            self.rightside.updateItem(sender.selectedtask)
        else:
            self.rightside.hide()

    def date_picked_handler(self, sender):
        self.leftside.updateItems()