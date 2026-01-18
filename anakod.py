import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QListWidget, QMessageBox
)

KULLANICI_DOSYA = "kullanicilar.txt"
GOREV_DOSYA = "gorevler.txt"


def kullanici_var_mi(kullanici):
    try:
        with open(KULLANICI_DOSYA, "r", encoding="utf-8") as f:
            for satir in f:
                if satir.strip().split("|")[0] == kullanici:
                    return True
    except FileNotFoundError:
        pass
    return False


def giris_dogrula(kullanici, sifre):
    try:
        with open(KULLANICI_DOSYA, "r", encoding="utf-8") as f:
            for satir in f:
                k, s = satir.strip().split("|")
                if k == kullanici and s == sifre:
                    return True
    except FileNotFoundError:
        pass
    return False


# ---------------- KAYIT OL ----------------
class KayitOl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kayıt Ol")

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
        k = self.kullanici.text().strip()
        s = self.sifre.text().strip()

        if not k or not s:
            QMessageBox.warning(self, "Hata", "Boş alan bırakma")
            return

        if kullanici_var_mi(k):
            QMessageBox.warning(self, "Hata", "Kullanıcı zaten var")
            return

        with open(KULLANICI_DOSYA, "a", encoding="utf-8") as f:
            f.write(f"{k}|{s}\n")

        QMessageBox.information(self, "Başarılı", "Kayıt oluşturuldu")
        self.close()


# ---------------- GİRİŞ ----------------
class Giris(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Giriş Yap")

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
        if giris_dogrula(self.kullanici.text(), self.sifre.text()):
            self.ana = AnaEkran(self.kullanici.text())
            self.ana.show()
            self.close()
        else:
            QMessageBox.warning(self, "Hata", "Giriş başarısız")


# ---------------- ANA EKRAN ----------------
class AnaEkran(QWidget):
    def __init__(self, kullanici):
        super().__init__()
        self.kullanici = kullanici
        self.setWindowTitle("Yapılacaklar Listesi")

        self.baslik = QLabel(f"Hoş geldin: {kullanici}")

        self.gorev_giris = QLineEdit()
        self.gorev_giris.setPlaceholderText("Yeni görev")

        self.ekle = QPushButton("Görev Ekle")
        self.ekle.clicked.connect(self.gorev_ekle)

        self.sil = QPushButton("Seçili Görevi Sil")
        self.sil.clicked.connect(self.gorev_sil)

        self.liste = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.baslik)
        layout.addWidget(self.gorev_giris)
        layout.addWidget(self.ekle)
        layout.addWidget(self.liste)
        layout.addWidget(self.sil)
        self.setLayout(layout)

        self.gorevleri_yukle()

    def gorevleri_yukle(self):
        self.liste.clear()
        try:
            with open(GOREV_DOSYA, "r", encoding="utf-8") as f:
                for satir in f:
                    k, g = satir.strip().split("|")
                    if k == self.kullanici:
                        self.liste.addItem(g)
        except FileNotFoundError:
            pass

    def gorev_ekle(self):
        gorev = self.gorev_giris.text().strip()
        if gorev:
            with open(GOREV_DOSYA, "a", encoding="utf-8") as f:
                f.write(f"{self.kullanici}|{gorev}\n")
            self.gorev_giris.clear()
            self.gorevleri_yukle()

    def gorev_sil(self):
        secili = self.liste.currentItem()
        if not secili:
            return

        with open(GOREV_DOSYA, "r", encoding="utf-8") as f:
            satirlar = f.readlines()

        with open(GOREV_DOSYA, "w", encoding="utf-8") as f:
            for satir in satirlar:
                if satir.strip() != f"{self.kullanici}|{secili.text()}":
                    f.write(satir)

        self.gorevleri_yukle()


# ---------------- ÇALIŞTIR ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    g = Giris()
    g.show()
    sys.exit(app.exec())