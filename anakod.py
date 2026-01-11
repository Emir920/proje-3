import sys
import sqlite3
import hashlib
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QListWidget, QMessageBox
)

# ---------------- VERİTABANI ----------------
veritabani_yolu = "veritabani.db"
baglanti = sqlite3.connect(veritabani_yolu)
imlec = baglanti.cursor()

# Kullanıcılar tablosu
imlec.execute("""
CREATE TABLE IF NOT EXISTS kullanicilar (
    kullanici_adi TEXT PRIMARY KEY,
    sifre TEXT
)
""")

# Yapılacaklar tablosu
imlec.execute("""
CREATE TABLE IF NOT EXISTS yapilacaklar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kullanici_adi TEXT,
    gorev TEXT
)
""")

def sifre_hashle(sifre):
    return hashlib.sha256(sifre.encode()).hexdigest()

# ---------------- KAYIT OL ----------------
class KayitOl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kayıt Ol")
        self.setGeometry(300, 300, 300, 200)

        self.kullanici = QLineEdit()
        self.kullanici.setPlaceholderText("Kullanıcı Adı")

        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.EchoMode.Password)

        self.buton = QPushButton("Kayıt Ol")
        self.buton.clicked.connect(self.kayit)

        layout = QVBoxLayout()
        layout.addWidget(self.kullanici)
        layout.addWidget(self.sifre)
        layout.addWidget(self.buton)
        self.setLayout(layout)

    def kayit(self):
        try:
            imlec.execute(
                "INSERT INTO kullanicilar VALUES (?, ?)",
                (self.kullanici.text(), sifre_hashle(self.sifre.text()))
            )
            baglanti.commit()
            QMessageBox.information(self, "Başarılı", "Kayıt oluşturuldu")
            self.close()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı zaten var")

# ---------------- GİRİŞ ----------------
class Giris(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Giriş Yap")
        self.setGeometry(300, 300, 300, 220)

        self.kullanici = QLineEdit()
        self.kullanici.setPlaceholderText("Kullanıcı Adı")

        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.EchoMode.Password)

        self.giris_buton = QPushButton("Giriş Yap")
        self.giris_buton.clicked.connect(self.giris)

        self.kayit_buton = QPushButton("Kayıt Ol")
        self.kayit_buton.clicked.connect(self.kayit_ac)

        layout = QVBoxLayout()
        layout.addWidget(self.kullanici)
        layout.addWidget(self.sifre)
        layout.addWidget(self.giris_buton)
        layout.addWidget(self.kayit_buton)
        self.setLayout(layout)

    def kayit_ac(self):
        self.kayit = KayitOl()
        self.kayit.show()

    def giris(self):
        imlec.execute(
            "SELECT * FROM kullanicilar WHERE kullanici_adi=? AND sifre=?",
            (self.kullanici.text(), sifre_hashle(self.sifre.text()))
        )
        if imlec.fetchone():
            self.ana = AnaEkran(self.kullanici.text())
            self.ana.show()
            self.close()
        else:
            QMessageBox.warning(self, "Hata", "Giriş başarısız")

# ---------------- ANA SAYFA ----------------
class AnaEkran(QWidget):
    def __init__(self, kullanici):
        super().__init__()
        self.kullanici = kullanici
        self.setWindowTitle("Yapılacaklar Listesi")
        self.setGeometry(300, 300, 400, 350)

        self.baslik = QLabel(f"Hoş geldin: {kullanici}")

        self.gorev_giris = QLineEdit()
        self.gorev_giris.setPlaceholderText("Yeni görev gir...")

        self.ekle_buton = QPushButton("Görev Ekle")
        self.ekle_buton.clicked.connect(self.gorev_ekle)

        self.sil_buton = QPushButton("Seçili Görevi Sil")
        self.sil_buton.clicked.connect(self.gorev_sil)

        self.liste = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.baslik)
        layout.addWidget(self.gorev_giris)
        layout.addWidget(self.ekle_buton)
        layout.addWidget(self.liste)
        layout.addWidget(self.sil_buton)
        self.setLayout(layout)

        self.gorevleri_yukle()

    def gorevleri_yukle(self):
        self.liste.clear()
        imlec.execute(
            "SELECT gorev FROM yapilacaklar WHERE kullanici_adi=?",
            (self.kullanici,)
        )
        for g in imlec.fetchall():
            self.liste.addItem(g[0])

    def gorev_ekle(self):
        gorev = self.gorev_giris.text().strip()
        if gorev:
            imlec.execute(
                "INSERT INTO yapilacaklar (kullanici_adi, gorev) VALUES (?, ?)",
                (self.kullanici, gorev)
            )
            baglanti.commit()
            self.gorev_giris.clear()
            self.gorevleri_yukle()

    def gorev_sil(self):
        secili = self.liste.currentItem()
        if secili:
            imlec.execute(
                "DELETE FROM yapilacaklar WHERE kullanici_adi=? AND gorev=?",
                (self.kullanici, secili.text())
            )
            baglanti.commit()
            self.gorevleri_yukle()

# ---------------- UYGULAMA ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    giris = Giris()
    giris.show()
    sys.exit(app.exec())