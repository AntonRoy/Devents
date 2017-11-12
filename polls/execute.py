
from polls.models import User

User.delete()

'''
import sqlite3

cnn = sqlite3.connect('db.sqlite3')

cur = cnn.cursor()

cur.execute("DELETE FROM User")
cnn.commit()

cnn.close()
'''