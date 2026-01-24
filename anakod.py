import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QListWidget, QMessageBox
)
from PyQt6.QtCore import Qt

DB_DOSYA = "uygulama.db"
KULLANICI_DOSYA = "kullanicilar.txt"
GOREV_DOSYA = "gorevler.txt"


def veritabani_baslat():
    """Veritabanını başlatır ve tabloları oluşturur"""
    conn = sqlite3.connect(DB_DOSYA)
    conn.execute('PRAGMA encoding = "UTF-8"')
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE NOT NULL,
            sifre TEXT NOT NULL,
            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Görevler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gorevler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER NOT NULL,
            gorev_adi TEXT NOT NULL,
            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()


def kullanici_var_mi(kullanici):
    """Kullanıcının veritabanında var olup olmadığını kontrol eder"""
    try:
        conn = sqlite3.connect(DB_DOSYA)
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM kullanicilar WHERE kullanici_adi = ?', (kullanici,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except sqlite3.Error:
        pass
    return False


def giris_dogrula(kullanici, sifre):
    """Kullanıcı girişini doğrular"""
    try:
        conn = sqlite3.connect(DB_DOSYA)
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?', 
                      (kullanici, sifre))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except sqlite3.Error:
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

        try:
            conn = sqlite3.connect(DB_DOSYA)
            conn.text_factory = str
            cursor = conn.cursor()
            cursor.execute('INSERT INTO kullanicilar (kullanici_adi, sifre) VALUES (?, ?)',
                          (k, s))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Başarılı", "Kayıt oluşturuldu")
            self.close()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Veritabanı hatası: {e}")


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


# ---------------- ANA EKRAN ------------------
class AnaEkran(QWidget):
    def __init__(self, kullanici):
        super().__init__()
        self.kullanici = kullanici
        self.kullanici_id = self.kullanici_id_obt()
        self.gorev_idsler = {}  # Görev adı -> ID eşlemesi
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

    def kullanici_id_obt(self):
        """Kullanıcının ID'sini veritabanından alır"""
        try:
            conn = sqlite3.connect(DB_DOSYA)
            conn.text_factory = str
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM kullanicilar WHERE kullanici_adi = ?', (self.kullanici,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except sqlite3.Error:
            return None

    def gorevleri_yukle(self):
        """Kullanıcının görevlerini veritabanından yükler"""
        self.liste.clear()
        self.gorev_idsler = {}
        try:
            conn = sqlite3.connect(DB_DOSYA)
            conn.text_factory = str
            cursor = conn.cursor()
            cursor.execute('SELECT id, gorev_adi FROM gorevler WHERE kullanici_id = ? ORDER BY id DESC', 
                          (self.kullanici_id,))
            gorevler = cursor.fetchall()
            conn.close()
            
            for gorev_id, gorev_adi in gorevler:
                self.liste.addItem(gorev_adi)
                self.gorev_idsler[gorev_adi] = gorev_id
        except sqlite3.Error:
            pass

    def gorev_ekle(self):
        """Yeni görev ekler"""
        gorev = self.gorev_giris.text().strip()
        if gorev:
            try:
                conn = sqlite3.connect(DB_DOSYA)
                conn.text_factory = str
                cursor = conn.cursor()
                cursor.execute('INSERT INTO gorevler (kullanici_id, gorev_adi) VALUES (?, ?)',
                              (self.kullanici_id, gorev))
                conn.commit()
                conn.close()
                self.gorev_giris.clear()
                self.gorevleri_yukle()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Hata", f"Görev eklenemedi: {e}")

    def gorev_sil(self):
        """Seçili görevi siler"""
        secili = self.liste.currentItem()
        if not secili:
            return

        gorev_adi = secili.text()
        gorev_id = self.gorev_idsler.get(gorev_adi)
        
        if not gorev_id:
            QMessageBox.warning(self, "Hata", "Görev ID'si bulunamadı")
            return

        try:
            conn = sqlite3.connect(DB_DOSYA)
            conn.text_factory = str
            cursor = conn.cursor()
            cursor.execute('DELETE FROM gorevler WHERE id = ? AND kullanici_id = ?',
                          (gorev_id, self.kullanici_id))
            conn.commit()
            conn.close()
            self.gorevleri_yukle()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Görev silinemedi: {e}")


# ---------------- ÇALIŞTIR ----------------
if __name__ == "__main__":
    veritabani_baslat()
    app = QApplication(sys.argv)
    g = Giris()
    g.show()
    sys.exit(app.exec())