from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QListWidgetItem, QMessageBox
from PyQt5 import uic, QtGui
import sqlite3
import globals
from PyQt5.QtCore import QTimer

class TaskWidget(QWidget):
    def __init__(self, task_name, likes=0, dislikes=0, task_id=None):
        super().__init__()
        # collecting infos
        self.task_name = task_name
        self.likes = likes
        self.dislikes = dislikes
        self.task_id = task_id
        
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

    def take_like(self):
        self.likes -= 1
        self.likes_label.setText(f'Likes: {self.likes}')

    def add_dislike(self):
      self.dislikes += 1
      self.dislikes_label.setText(f'Dislikes: {self.dislikes}')

    def take_dislike(self):
      self.dislikes -= 1
      self.dislikes_label.setText(f'Dislikes: {self.dislikes}')
    
    def get_id(self):
      return self.task_id

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
    # Checking for messages from other windows
    if globals.message:
      # Delaying the message so it won't appear before the window
      QTimer.singleShot(50, self.show_message)

    # fetching tasks related to the room
    conn = sqlite3.connect('myDb.db')
    cur = conn.cursor()
    tasks = cur.execute(f'select * from tasks where project_id={globals.current_project}').fetchall()
    for task in tasks:
      task_id = task[0]
      likes = task[3]
      dislikes = task[4]
      status = task[5]
      task_content = task[6]
      task_widget = TaskWidget(task[6], likes, dislikes, task_id)
      list_item = QListWidgetItem(self.tasks_widget)
      list_item.setSizeHint(task_widget.sizeHint())
      self.tasks_widget.addItem(list_item)
      self.tasks_widget.setItemWidget(list_item, task_widget)
      if status:
        if status == 'woi':
          list_item.setBackground(QtGui.QColor(253, 255, 93))
        elif status == 'completed':
          list_item.setBackground(QtGui.QColor(0, 255, 0))

    # changing the room name label
    project_name = cur.execute(f'select name from Projects where project_id={globals.current_project}').fetchone()[0]
    self.room_name_label.setText(f"{project_name}")
          
  def show_message(self):
        if globals.message and globals.message[0] == 'information':
            QMessageBox.information(self, 'information', globals.message[1])
            globals.message = None

  # event for the add task button
  def add_task(self, likes=0, dislikes=0,task_id=None):
        # getting the user's input
        task = self.task_input.text()
        if not task:
          return

        # adding the task to the database
        conn = sqlite3.connect('myDb.db')
        cur = conn.cursor()
        cur.execute('''
          insert into Tasks (project_id, username, content, likes, dislikes) values (?, ?, ?, ?, ?)
        ''',(globals.current_project, globals.current_user, task, likes, dislikes))
        task_id = cur.lastrowid
        print(task_id)
        conn.commit()
        conn.close()

        # creating an instance of the class TaskWidget
        task_widget = TaskWidget(task, likes, dislikes, task_id) # horizontal layout
        # creating an item to put it on the listWidget
        list_item = QListWidgetItem(self.tasks_widget)
        # giving the item a proper size
        list_item.setSizeHint(task_widget.sizeHint())
        # adding the task to the list widget
        self.tasks_widget.addItem(list_item)
        # setting the task_widget as the widget to be displayed within list_item
        self.tasks_widget.setItemWidget(list_item, task_widget)
        # clearing the input
        self.task_input.clear()
        
  def like_selected_task(self):
      selected = self.tasks_widget.currentItem()
      # checking if the user selected any task
      if selected:
        conn = sqlite3.connect('myDb.db')
        cur = conn.cursor()

        # getting the task's id
        task_widget = self.tasks_widget.itemWidget(selected)
        task_id = task_widget.get_id()

        # checking if the user already liked that task
        interacted = cur.execute('''
        select type from interactions where username=? and task_id=?
        ''', (globals.current_user, task_id)).fetchone()
        # case where user hasn't interacted with the task
        if not interacted:
          cur.execute('''
            insert into Interactions (task_id, username, type) values(?, ?, ?)
            ''',(task_id, globals.current_user, 'like'))

          # incrementing likes
          task_widget.add_like()

          # updating likes on database
          cur.execute('update tasks set likes=likes+1 where task_id=?',(task_id,))
          cur.execute('''
          insert  into interactions (task_id, username, type) values(?, ?, ?)
          ''',(task_id, globals.current_user, 'like'))
        
        elif interacted[0] == 'dislike':
          # changing the type of interaction in database
          cur.execute(f"update interactions set type='like' where task_id={task_id} and username='{globals.current_user}'")
          # incrementing likes and decrementing dislikes
          task_widget.add_like()
          task_widget.take_dislike()
        
        # case where already liked, remving the like
        elif interacted[0] == 'like':
          # deleting interaction from database
          cur.execute(f"delete from interactions where task_id={task_id} and username='{globals.current_user}'")
          # decrementing the task's likes
          cur.execute(f"update tasks set likes=likes-1 where task_id=?", (task_id,))
          # decrementing likes
          task_widget.take_like()

        conn.commit()
        conn.close()

  def dislike_selected_task(self):
      selected = self.tasks_widget.currentItem()
      # checking if the user selected any task
      if selected:
        conn = sqlite3.connect('myDb.db')
        cur = conn.cursor()

        # getting the task's id
        task_widget = self.tasks_widget.itemWidget(selected)
        task_id = task_widget.get_id()

        # checking if the user already disliked that task
        interacted = cur.execute('''
        select type from interactions where username=? and task_id=?
        ''', (globals.current_user, task_id)).fetchone()
        # case where user hasn't interacted with the task
        if not interacted:
          cur.execute('''
            insert into Interactions (task_id, username, type) values(?, ?, ?)
            ''',(task_id, globals.current_user, 'dislike'))

          # incrementing dislikes
          task_widget.add_dislike()

          # updating dislikes on database
          cur.execute('update tasks set dislikes=dislikes+1 where task_id=?',(task_id,))
          cur.execute('''
          insert  into interactions (task_id, username, type) values(?, ?, ?)
          ''',(task_id, globals.current_user, 'dislike'))
        
        elif interacted[0] == 'like':
          # changing the type of interaction in database
          cur.execute(f"update interactions set type='dislike' where task_id={task_id} and username='{globals.current_user}'")
          # incrementing dislikes and decrementing likes
          task_widget.add_dislike()
          task_widget.take_like()

        # case where already disliked, removing the dislike
        elif interacted[0] == 'dislike':
          # deleting interaction from database
          cur.execute(f"delete from interactions where task_id={task_id} and username='{globals.current_user}'")
          # decrementing the task's dislikes
          cur.execute(f"update tasks set dislikes=dislikes-1 where task_id=?", (task_id,))
          # decrementing dislikes
          task_widget.take_dislike()

        conn.commit()
        conn.close()

  # event for remove button
  def remove_task(self):
    selected = self.tasks_widget.currentItem()
    if selected:
      task_widget = self.tasks_widget.itemWidget(selected)
      task_id = task_widget.get_id()

      # checking if the user can delete the task
      conn = sqlite3.connect('myDb.db')
      cur = conn.cursor()
      owner = cur.execute('select username from tasks where task_id=?', (task_id,)).fetchone()[0]
      admin = cur.execute('select username from projects where project_id=?', (globals.current_project,)).fetchone()[0]
      print(f"owner is {owner}")
      print(f"adming is {admin}")
      if owner == globals.current_user or admin == globals.current_user:
        # removing task
        row = self.tasks_widget.row(selected)
        self.tasks_widget.takeItem(row)
        # removing task from database
        cur.execute('delete from tasks where task_id=?',(task_id,))
        conn.commit()
        conn.close()
      else:
        QMessageBox.warning(self,'Invalid', 'only the owner of the task and the admin can delete this task')

  def working_on_it(self):
    selected = self.tasks_widget.currentItem()
    if selected:
      selected.setBackground(QtGui.QColor(253, 255, 93))
      task_id = self.tasks_widget.itemWidget(selected).get_id()
      # updating database
      conn = sqlite3.connect('myDb.db')
      cur = conn.cursor()
      woi = cur.execute('select status from tasks where task_id=?', (task_id,)).fetchone()[0]
      if woi == 'woi':
        QMessageBox.warning(self, 'Invalid', 'task is already being worked on')
        return
      cur.execute('update tasks set status=? where task_id=?',('woi', task_id))
      conn.commit()
      conn.close()

  def completed(self):
    selected = self.tasks_widget.currentItem()
    if selected:
      selected.setBackground(QtGui.QColor(0, 255, 0))
      # updating database
      conn = sqlite3.connect('myDb.db')
      cur = conn.cursor()
      task_id = self.tasks_widget.itemWidget(selected).get_id()
      cmplt = cur.execute('select status from tasks where task_id=?', (task_id,)).fetchone()[0]
      if cmplt == 'completed':
        QMessageBox.warning(self, 'Invalid', 'task is already completed')
        return
      cur.execute('update tasks set status=? where task_id=?',('completed', task_id))
      conn.commit()
      conn.close()
