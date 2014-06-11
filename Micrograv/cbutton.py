# checkbutton class wrapper to make life easier
import Tkinter

class Cbutton:
  def __init__(self, master, label):
    self.value = Tkinter.IntVar()
    self.button = Tkinter.Checkbutton(master, text=label, variable=self.value)

  def query(self):
    return self.value.get()

  def set(self):
    self.button.select()
    self.button.update()

  def unset(self):
    self.button.deselect()
    self.button.update()

  def toggle(self):
    self.button.toggle()
    self.button.update()

