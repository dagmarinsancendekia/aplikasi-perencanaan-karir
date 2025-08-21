from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # Memuat data dari CSV
    df = pd.read_csv('data/tes_holland.csv')
    soal_tes = df.to_dict('records')
    return render_template('index.html', soal_tes=soal_tes)
@app.route('/hasil', methods=['POST'])
def hasil():
    # Memuat data soal untuk referensi
    df = pd.read_csv('data/tes_holland.csv')

    # Inisialisasi skor untuk setiap kategori RIASEC
    skor = {
        'R': 0, 'I': 0, 'A': 0, 
        'S': 0, 'E': 0, 'C': 0
    }

    # Memproses jawaban dari formulir
    for soal in df.to_dict('records'):
        jawaban_user = request.form.get(f'soal_{soal["id"]}')
        if jawaban_user == 'setuju':
            kategori = soal['kategori']
            if kategori in skor:
                skor[kategori] += 1

    # Menentukan kategori dengan skor tertinggi
    kategori_tertinggi = max(skor, key=skor.get)

    # Contoh rekomendasi berdasarkan kategori
    rekomendasi = "Belum ada rekomendasi yang tersedia."
    if kategori_tertinggi == 'R':
        rekomendasi = "Anda cenderung memiliki minat di bidang Realistis. Karir yang cocok: Insinyur, Teknisi, Mekanik."
    elif kategori_tertinggi == 'I':
        rekomendasi = "Anda cenderung memiliki minat di bidang Investigatif. Karir yang cocok: Ilmuwan, Analis Data, Dokter."
    # Tambahkan kondisi untuk kategori lainnya (A, S, E, C)

    return render_template('hasil.html', kategori_tertinggi=kategori_tertinggi, rekomendasi=rekomendasi)

# Jalankan aplikasi jika file ini dieksekusi langsung
if __name__ == '__main__':
    app.run(debug=True)