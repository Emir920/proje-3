import sys
import os
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QListWidget,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor

KULLANICILAR_DOSYA = "kullanicilar.txt"

PENCERELER = []   # 🔥 GLOBAL – AÇILIP KAPANMAYI ENGELLER


# ---------------- DOSYA ----------------
def kullanici_dosya_kontrol():
    if not os.path.exists(KULLANICILAR_DOSYA):
        open(KULLANICILAR_DOSYA, "w", encoding="utf-8").close()


def kullanicilari_yukle():
    kullanici_dosya_kontrol()
    k = {}
    with open(KULLANICILAR_DOSYA, "r", encoding="utf-8") as f:
        for s in f:
            if "|" in s:
                a, b = s.strip().split("|", 1)
                k[a] = b
    return k


def kullanici_kaydet(a, b):
    with open(KULLANICILAR_DOSYA, "a", encoding="utf-8") as f:
        f.write(f"{a}|{b}\n")


def gorev_dosyasi(k):
    return f"todo_{k}.txt"


# ---------------- KAYIT ----------------
class KayitOl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kayıt Ol")

        self.k = QLineEdit(placeholderText="Kullanıcı Adı")
        self.s = QLineEdit(placeholderText="Şifre")
        self.s.setEchoMode(QLineEdit.EchoMode.Password)

        b = QPushButton("Hesap Oluştur")
        b.clicked.connect(self.kaydet)

        l = QVBoxLayout(self)
        l.addWidget(self.k)
        l.addWidget(self.s)
        l.addWidget(b)

    def kaydet(self):
        if not self.k.text() or not self.s.text():
            QMessageBox.warning(self, "Hata", "Alanları doldur")
            return

        if self.k.text() in kullanicilari_yukle():
            QMessageBox.warning(self, "Hata", "Kullanıcı var")
            return

        kullanici_kaydet(self.k.text(), self.s.text())
        open(gorev_dosyasi(self.k.text()), "w").close()
        QMessageBox.information(self, "OK", "Hesap oluşturuldu")
        self.hide()


# ---------------- GİRİŞ ----------------
class Giris(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Giriş")

        self.k = QLineEdit(placeholderText="Kullanıcı")
        self.s = QLineEdit(placeholderText="Şifre")
        self.s.setEchoMode(QLineEdit.EchoMode.Password)

        g = QPushButton("Giriş")
        g.clicked.connect(self.giris)

        r = QPushButton("Kayıt Ol")
        r.clicked.connect(self.kayit)

        l = QVBoxLayout(self)
        l.addWidget(self.k)
        l.addWidget(self.s)
        l.addWidget(g)
        l.addWidget(r)

    def kayit(self):
        self.kayit_p = KayitOl()
        PENCERELER.append(self.kayit_p)
        self.kayit_p.show()

    def giris(self):
        if kullanicilari_yukle().get(self.k.text()) == self.s.text():
            self.menu = Menu(self.k.text())
            PENCERELER.append(self.menu)
            self.menu.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Hata", "Yanlış giriş")


# ---------------- MENÜ ----------------
class Menu(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Menü")

        l = QVBoxLayout(self)
        l.addWidget(QLabel(f"Hoş geldin {user}"))

        t = QPushButton("📝 Yapılacaklar")
        o = QPushButton("🎮 Oyunlar")

        t.clicked.connect(self.todo)
        o.clicked.connect(self.oyunlar)

        l.addWidget(t)
        l.addWidget(o)

    def todo(self):
        self.t = Yapilacaklar(self.user)
        PENCERELER.append(self.t)
        self.t.show()

    def oyunlar(self):
        self.o = OyunListesi()
        PENCERELER.append(self.o)
        self.o.show()


# ---------------- TODO ----------------
class Yapilacaklar(QWidget):
    def __init__(self, k):
        super().__init__()
        self.d = gorev_dosyasi(k)
        self.setWindowTitle("Yapılacaklar")

        self.g = QLineEdit()
        e = QPushButton("Ekle")
        e.clicked.connect(self.ekle)

        self.l = QListWidget()
        s = QPushButton("Sil")
        s.clicked.connect(self.sil)

        v = QVBoxLayout(self)
        for w in (self.g, e, self.l, s):
            v.addWidget(w)

        self.yukle()

    def yukle(self):
        self.l.clear()
        if os.path.exists(self.d):
            with open(self.d) as f:
                for x in f:
                    self.l.addItem(x.strip())

    def ekle(self):
        with open(self.d, "a") as f:
            f.write(self.g.text() + "\n")
        self.g.clear()
        self.yukle()

    def sil(self):
        if not self.l.currentItem():
            return
        with open(self.d) as f:
            x = [i.strip() for i in f if i.strip() != self.l.currentItem().text()]
        with open(self.d, "w") as f:
            for i in x:
                f.write(i + "\n")
        self.yukle()


# ---------------- OYUN LİSTESİ ----------------
class OyunListesi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oyunlar")

        self.l = QListWidget()
        self.l.addItem("🐍 Yılan Oyunu")
        self.l.addItem("🔥 Canavar Savaşı")

        b = QPushButton("Aç")
        b.clicked.connect(self.baslat)

        v = QVBoxLayout(self)
        v.addWidget(self.l)
        v.addWidget(b)

    def baslat(self):
        if not self.l.currentItem():
            return

        if "Yılan" in self.l.currentItem().text():
            self.o = YilanOyunu()
        else:
            self.o = PokemonBenzeri()

        PENCERELER.append(self.o)
        self.o.show()


# ---------------- YILAN ----------------
class YilanOyunu(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)
        self.y = [(200, 200)]
        self.yon = Qt.Key.Key_Right
        self.yem = (100, 100)

        self.t = QTimer()
        self.t.timeout.connect(self.guncelle)
        self.t.start(120)

    def keyPressEvent(self, e):
        self.yon = e.key()

    def guncelle(self):
        x, y = self.y[0]
        if self.yon == Qt.Key.Key_Left: x -= 20
        if self.yon == Qt.Key.Key_Right: x += 20
        if self.yon == Qt.Key.Key_Up: y -= 20
        if self.yon == Qt.Key.Key_Down: y += 20
        n = (x, y)

        if n in self.y or not (0 <= x < 400 and 0 <= y < 400):
            self.t.stop()
            QMessageBox.information(self, "Bitti", "Kaybettin")
            self.hide()
            return

        self.y.insert(0, n)
        if n == self.yem:
            self.yem = (random.randrange(0, 400, 20), random.randrange(0, 400, 20))
        else:
            self.y.pop()
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setBrush(QColor("green"))
        for a, b in self.y:
            p.drawRect(a, b, 20, 20)
        p.setBrush(QColor("red"))
        p.drawRect(*self.yem, 20, 20)


# ---------------- POKEMON ----------------
class PokemonBenzeri(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Canavar")

        self.o = 100
        self.d = 100

        self.ob = QProgressBar()
        self.db = QProgressBar()
        self.ob.setValue(100)
        self.db.setValue(100)

        b = QPushButton("Saldır")
        b.clicked.connect(self.saldir)

        v = QVBoxLayout(self)
        for w in ("Sen", self.ob, "Düşman", self.db, b):
            v.addWidget(QLabel(w) if isinstance(w, str) else w)

    def saldir(self):
        self.d -= random.randint(10, 20)
        self.db.setValue(self.d)
        if self.d <= 0:
            QMessageBox.information(self, "Kazandın", "Tebrikler")
            self.hide()
            return

        self.o -= random.randint(5, 15)
        self.ob.setValue(self.o)
        if self.o <= 0:
            QMessageBox.information(self, "Kaybettin", "Üzgünüm")
            self.hide()


# ---------------- BAŞLAT ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    g = Giris()
    PENCERELER.append(g)
    g.show()

    sys.exit(app.exec())
