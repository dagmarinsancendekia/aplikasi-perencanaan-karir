from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Memuat data sekali saat aplikasi dimulai
# Pastikan jalur ke file CSV sudah benar
df_holland = pd.read_csv('data/tes_holland.csv')

@app.route('/')
def index():
    """Menampilkan halaman utama dengan pertanyaan tes."""
    # Mengambil hanya id dan pertanyaan dari dataframe
    soal_tes = df_holland[['id', 'pertanyaan']].to_dict('records')
    return render_template('index.html', soal_tes=soal_tes)

@app.route('/hasil', methods=['POST'])
def hasil():
    """Memproses jawaban tes dan menampilkan hasilnya."""
    # Inisialisasi skor untuk setiap kategori RIASEC yang unik dari data
    skor = {kategori: 0 for kategori in df_holland['kategori'].unique()}

    # Mengolah jawaban dari formulir
    for soal in df_holland.to_dict('records'):
        # Mendapatkan jawaban 'setuju' atau 'tidak_setuju' untuk setiap pertanyaan
        jawaban_user = request.form.get(f'soal_{soal["id"]}')
        if jawaban_user == 'setuju':
            kategori = soal['kategori']
            # Menambahkan skor jika kategori ada
            if kategori in skor:
                skor[kategori] += 1
    
    # Pengecekan jika tidak ada jawaban yang dipilih
    # Hal ini bisa terjadi jika pengguna langsung menekan tombol 'Lihat Hasil' tanpa memilih
    if not any(skor.values()):
        kategori_tertinggi = "Tidak Ada Jawaban"
        deskripsi = "Sepertinya Anda belum memilih jawaban apapun. Silakan pilih setidaknya satu jawaban untuk mendapatkan hasil."
        rekomendasi_list = ["Silakan coba tes lagi untuk mengetahui minat karir Anda!"]
        
        return render_template('hasil.html', 
                               kategori_tertinggi=kategori_tertinggi, 
                               deskripsi=deskripsi, 
                               rekomendasi=rekomendasi_list) # Kirim sebagai list

    # Menentukan kategori dengan skor tertinggi
    kategori_tertinggi = max(skor, key=skor.get)
    
    # Mengambil baris data yang sesuai dengan kategori tertinggi
    # Menggunakan iloc[0] untuk mengambil baris pertama yang cocok
    data_tertinggi = df_holland[df_holland['kategori'] == kategori_tertinggi].iloc[0]
    
    deskripsi = data_tertinggi['deskripsi']
    # Memisahkan string rekomendasi menjadi list individual untuk ditampilkan di HTML
    rekomendasi_list = [item.strip() for item in data_tertinggi['rekomendasi_karir'].split(',')]
    
    return render_template('hasil.html', 
                           kategori_tertinggi=kategori_tertinggi, 
                           deskripsi=deskripsi, 
                           rekomendasi=rekomendasi_list) # Kirim sebagai list

# Jalankan aplikasi jika file ini dieksekusi langsung
if __name__ == '__main__':
    # debug=True akan memberikan informasi error yang lebih detail dan otomatis refresh
    app.run(debug=True)
