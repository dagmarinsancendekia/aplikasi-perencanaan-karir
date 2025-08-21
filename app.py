    from flask import Flask, render_template, request
    import pandas as pd

    app = Flask(__name__)

    # Memuat data sekali saat aplikasi dimulai
    df_holland = pd.read_csv('data/tes_holland.csv')

    # Data tambahan untuk deskripsi singkat setiap kategori RIASEC
    # Ini akan kita gunakan di halaman hasil untuk memberikan konteks
    riasec_descriptions = {
        'R': 'Realistis (Doers): Praktis, suka bekerja dengan tangan, alat, dan mesin.',
        'I': 'Investigatif (Thinkers): Analitis, suka memecahkan masalah, melakukan penelitian, dan berpikir kritis.',
        'A': 'Artistik (Creators): Ekspresif, inovatif, suka seni, musik, drama, dan desain.',
        'S': 'Sosial (Helpers): Peduli, suka membantu, mengajar, dan berinteraksi dengan orang lain.',
        'E': 'Enterprising (Persuaders): Ambisius, suka memimpin, mempengaruhi, dan bernegosiasi.',
        'C': 'Konvensional (Organizers): Teratur, teliti, suka bekerja dengan data, angka, dan detail.'
    }

    @app.route('/')
    def index():
        """Menampilkan halaman utama dengan pertanyaan tes."""
        soal_tes = df_holland[['id', 'pertanyaan']].to_dict('records')
        return render_template('index.html', soal_tes=soal_tes)

    @app.route('/hasil', methods=['POST'])
    def hasil():
        """Memproses jawaban tes dan menampilkan hasilnya."""
        skor = {kategori: 0 for kategori in df_holland['kategori'].unique()}

        for soal in df_holland.to_dict('records'):
            jawaban_user = request.form.get(f'soal_{soal["id"]}')
            if jawaban_user == 'setuju':
                kategori = soal['kategori']
                if kategori in skor:
                    skor[kategori] += 1
        
        if not any(skor.values()):
            kategori_tertinggi = "Tidak Ada Jawaban"
            deskripsi = "Sepertinya Anda belum memilih jawaban apapun. Silakan pilih setidaknya satu jawaban untuk mendapatkan hasil."
            rekomendasi_list = ["Silakan coba tes lagi untuk mengetahui minat karir Anda!"]
            
            return render_template('hasil.html', 
                                   kategori_tertinggi=kategori_tertinggi, 
                                   deskripsi=deskripsi, 
                                   rekomendasi=rekomendasi_list,
                                   skor_lengkap=skor, # Kirim skor lengkap
                                   riasec_desc=riasec_descriptions) # Kirim deskripsi RIASEC
        
        kategori_tertinggi = max(skor, key=skor.get)
        data_tertinggi = df_holland[df_holland['kategori'] == kategori_tertinggi].iloc[0]
        
        deskripsi = data_tertinggi['deskripsi']
        rekomendasi_list = [item.strip() for item in data_tertinggi['rekomendasi_karir'].split(',')]
        
        return render_template('hasil.html', 
                               kategori_tertinggi=kategori_tertinggi, 
                               deskripsi=deskripsi, 
                               rekomendasi=rekomendasi_list,
                               skor_lengkap=skor, # Kirim skor lengkap
                               riasec_desc=riasec_descriptions) # Kirim deskripsi RIASEC

    if __name__ == '__main__':
        app.run(debug=True)
    