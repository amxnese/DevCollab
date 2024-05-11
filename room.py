from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QListWidgetItem
from PyQt5 import uic, QtGui

class TaskWidget(QWidget):
    def __init__(self, task_name, likes=0, dislikes=0):
        super().__init__()
        # collecting infos
        self.task_name = task_name
        self.likes = likes
        self.dislikes = dislikes
        
        # creating a horizontal layout
        self.layout = QHBoxLayout(self)
        
        # creating objects that will be put in the task
        self.task_label = QLabel(self.task_name)
        self.likes_label = QLabel(f'Likes: {self.likes}')
        self.dislikes_label = QLabel(f'Dislikes: {self.dislikes}')
        
        # adding objects to the horizontal layout and now we have a task widget
        self.layout.addWidget(self.task_label)
        self.layout.addWidget(self.likes_label)
        self.layout.addWidget(self.dislikes_label)

    def add_like(self):
        self.likes += 1
        self.likes_label.setText(f'Likes: {self.likes}')

    def add_dislike(self):
      self.dislikes += 1
      self.dislikes_label.setText(f'Dislikes: {self.dislikes}')

class Room(QMainWindow):
  def __init__(self):
    super(Room, self).__init__()
    uic.loadUi("room.ui", self)
    self.add_task_button.clicked.connect(self.add_task)
    self.remove_button.clicked.connect(self.remove_task)
    self.woi_button.clicked.connect(self.working_on_it)
    self.completed_button.clicked.connect(self.completed)
    self.like_button.clicked.connect(self.like_selected_task)
    self.dislike_button.clicked.connect(self.dislike_selected_task)

  # event for the add task button
  def add_task(self, task_name, likes=0, dislikes=0):
        # getting the user's input
        task = self.task_input.text()
        # creating an instance of the class TaskWidget
        task_widget = TaskWidget(task, likes, dislikes) # horizontal layout
        # creating an item to put it on the listWidget
        list_item = QListWidgetItem(self.tasks_widget)
        # giving the item a proper size
        list_item.setSizeHint(task_widget.sizeHint())
        # adding the task to the list widget
        self.tasks_widget.addItem(list_item)
        # setint the task_widget as the widget to be displayed within list_item
        self.tasks_widget.setItemWidget(list_item, task_widget)
        # clearing the input
        self.task_input.clear()

  def like_selected_task(self):
        selected = self.tasks_widget.currentItem()
        if selected:
            task_widget = self.tasks_widget.itemWidget(selected)
            task_widget.add_like()

  def dislike_selected_task(self):
        selected = self.tasks_widget.currentItem()
        if selected:
          task_widget = self.tasks_widget.itemWidget(selected)
          task_widget.add_dislike()

  # event for remove button
  def remove_task(self):
    selected = self.tasks_widget.currentItem()
    if selected:
      row = self.tasks_widget.row(selected)
      self.tasks_widget.takeItem(row)

  def working_on_it(self):
    selected = self.tasks_widget.currentItem()
    if selected:
      selected.setBackground(QtGui.QColor(253, 255, 93))

  def completed(self):
    selected = self.tasks_widget.currentItem()
    if selected:
      selected.setBackground(QtGui.QColor(0, 255, 0))
