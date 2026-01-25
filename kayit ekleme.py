import mysql.connector
vt = mysql.connector.connect(host="localhost",user="Emir920",password="xx4455xx6677",database="python")

# ad = x.ad_input.text() # pyqt QLineEdit içindeki veri
# nu = x.numara_input.text() # pyqt QLineEdit içindeki veri
a = input("Ad gir     :")
b = input("telefon gir:")
mycursor = vt.cursor()
mycursor.execute(f'INSERT INTO python.python1 (ad,telefon) values ("{a}","{b}")')
vt.commit()
