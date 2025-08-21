from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # Memuat data dari CSV
    df = pd.read_csv('data/tes_holland.csv')
    soal_tes = df.to_dict('records')
    return render_template('index.html', soal_tes=soal_tes)

# Jalankan aplikasi jika file ini dieksekusi langsung
if __name__ == '__main__':
    app.run(debug=True)