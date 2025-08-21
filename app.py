from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Memuat data sekali saat aplikasi dimulai
df_holland = pd.read_csv('data/tes_holland.csv')

@app.route('/')
def index():
    soal_tes = df_holland[['id', 'pertanyaan']].to_dict('records')
    return render_template('index.html', soal_tes=soal_tes)

@app.route('/hasil', methods=['POST'])
def hasil():
    # Inisialisasi skor
    skor = {kategori: 0 for kategori in df_holland['kategori'].unique()}

    # Mengolah jawaban
    for soal in df_holland.to_dict('records'):
        jawaban_user = request.form.get(f'soal_{soal["id"]}')
        if jawaban_user == 'setuju':
            kategori = soal['kategori']
            if kategori in skor:
                skor[kategori] += 1

    # Menentukan kategori tertinggi dan mengambil datanya
    if not skor:
        kategori_tertinggi = None
        deskripsi = "Tidak ada jawaban yang dipilih."
        rekomendasi = "Silakan coba tes lagi."
    else:
        kategori_tertinggi = max(skor, key=skor.get)

        # Ambil data dari CSV berdasarkan kategori tertinggi
        data_tertinggi = df_holland[df_holland['kategori'] == kategori_tertinggi].iloc[0]
        deskripsi = data_tertinggi['deskripsi']
        rekomendasi = data_tertinggi['rekomendasi_karir']

    return render_template('hasil.html', kategori_tertinggi=kategori_tertinggi, deskripsi=deskripsi, rekomendasi=rekomendasi)

if __name__ == '__main__':
    app.run(debug=True)