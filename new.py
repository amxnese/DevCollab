from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QPushButton, QLabel, QListWidgetItem, QHBoxLayout
from PyQt5.QtCore import pyqtSlot

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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # creating a vertical layout
        self.layout = QVBoxLayout(self)
        
        # Creating like and dislike buttons 
        self.like_button = QPushButton('Like')
        self.dislike_button = QPushButton('Dislike')

        # Adding the buttons to the layout
        self.layout.addWidget(self.like_button)
        self.layout.addWidget(self.dislike_button)
        
        # Creating a list widget and adding it to the layout
        self.list_widget = QListWidget(self)
        self.layout.addWidget(self.list_widget)
        
        # connecting buttons to their functions
        self.like_button.clicked.connect(self.like_selected_task)
        self.dislike_button.clicked.connect(self.dislike_selected_task)
        
        # Populating the list with some tasks
        self.add_task('Task 1')
        self.add_task('Task 2')
        self.add_task('Task 3')

    def add_task(self, task_name, likes=0, dislikes=0):
        # creating an instance of the class TaskWidget
        task_widget = TaskWidget(task_name, likes, dislikes) # horizontal layout
        # creating an item to put it on the listWidget
        list_item = QListWidgetItem(self.list_widget)
        # giving the item a proper size
        list_item.setSizeHint(task_widget.sizeHint())
        # adding the task to the list widget
        self.list_widget.addItem(list_item)
        # setint the task_widget as the widget to be displayed within list_item
        self.list_widget.setItemWidget(list_item, task_widget)

    def like_selected_task(self):
        selected = self.list_widget.currentItem()
        if selected:
            task_widget = self.list_widget.itemWidget(selected)
            task_widget.add_like()

    def dislike_selected_task(self):
        selected = self.list_widget.currentItem()
        if selected:
          task_widget = self.list_widget.itemWidget(selected)
          task_widget.add_dislike()

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
