import pandas as pd
import customtkinter
import matplotlib.pyplot as plt
import io

class QuizLogic:
    def __init__(self, data_file):
        self.df_holland = pd.read_csv(data_file)
        self.questions_data = self.df_holland.to_dict('records')
        self.total_questions = len(self.questions_data)
        self.current_question_index = 0

        self.riasec_descriptions = {
            'R': 'Realistis (Doers): Individu ini praktis, kuat secara fisik, dan suka bekerja dengan tangan, alat, dan mesin. Mereka menikmati pekerjaan yang konkret dan tangible, seperti konstruksi, teknik, atau pertanian.',
            'I': 'Investigatif (Thinkers): Individu ini analitis, logis, dan suka memecahkan masalah. Mereka tertarik pada sains, penelitian, dan kegiatan intelektual. Karir yang cocok meliputi ilmuwan, peneliti, atau dokter.',
            'A': 'Artistik (Creators): Individu ini ekspresif, inovatif, dan imajinatif. Mereka menikmati bentuk seni seperti musik, drama, menulis, atau desain. Mereka sering menghindari struktur dan aturan yang kaku, lebih memilih kebebasan berekspresi.',
            'S': 'Sosial (Helpers): Individu ini peduli, kooperatif, dan suka membantu orang lain. Mereka memiliki minat dalam mengajar, konseling, atau layanan masyarakat. Mereka terampil dalam berkomunikasi dan membangun hubungan.',
            'E': 'Enterprising (Persuaders): Individu ini ambisius, energik, dan suka memimpin. Mereka menikmati mempengaruhi, meyakinkan, dan bernegosiasi. Karir yang sesuai adalah penjualan, manajemen, atau kewirausahaan.',
            'C': 'Konvensional (Organizers): Individu ini teratur, teliti, dan suka bekerja dengan data dan detail. Mereka efisien dan suka mengikuti prosedur yang jelas. Pekerjaan yang cocok adalah akuntan, sekretaris, atau pustakawan.'
        }
        
        self.answer_vars = {}
        for row in self.df_holland.to_dict('records'):
            self.answer_vars[row['id']] = customtkinter.StringVar(value="None")

    def get_current_question(self):
        """Mengembalikan data pertanyaan saat ini."""
        if self.current_question_index < self.total_questions:
            return self.questions_data[self.current_question_index]
        return None

    def record_answer(self, question_id, answer_value):
        """Merekam jawaban pengguna."""
        self.answer_vars[question_id].set(answer_value)

    def all_questions_answered(self):
        """Memeriksa apakah semua pertanyaan sudah dijawab."""
        for q_id in self.df_holland['id']:
            if self.answer_vars[q_id].get() == "None":
                return False
        return True

    def calculate_scores(self):
        """Menghitung skor RIASEC berdasarkan jawaban pengguna."""
        skor = {kategori: 0 for kategori in self.df_holland['kategori'].unique()}
        for i, row in self.df_holland.iterrows():
            question_id = row['id']
            answer = self.answer_vars[question_id].get()
            if answer == 'setuju':
                kategori = row['kategori']
                if kategori in skor:
                    skor[kategori] += 1
        return skor

    def get_final_results(self, skor_lengkap):
        """Menentukan kategori tertinggi, deskripsi, dan rekomendasi karir."""
        max_score = 0
        kategori_tertinggi = None
        for k, v in skor_lengkap.items():
            if v > max_score:
                max_score = v
                kategori_tertinggi = k
            elif v == max_score and kategori_tertinggi is None:
                kategori_tertinggi = k
        
        if kategori_tertinggi is None:
             deskripsi = "Tidak ada jawaban 'Setuju' yang dipilih."
             rekomendasi_list = ["Tidak ada rekomendasi spesifik."]
        else:
            data_tertinggi = self.df_holland[self.df_holland['kategori'] == kategori_tertinggi].iloc[0]
            deskripsi = data_tertinggi['deskripsi']
            rekomendasi_list = [item.strip() for item in data_tertinggi['rekomendasi_karir'].split(',')]
        
        return kategori_tertinggi, deskripsi, rekomendasi_list

    def create_riasec_chart(self, scores_dict):
        """Membuat grafik batang dari skor RIASEC dan mengembalikan objek BytesIO."""
        labels = list(scores_dict.keys())
        values = list(scores_dict.values())
        
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        # Ambil warna dari tema CustomTkinter yang sedang aktif (misalnya untuk dark mode)
        bar_color = customtkinter.ThemeManager.theme["CTkButton"]["fg_color"][1] 
        bars = ax.bar(labels, values, color=bar_color)
        
        ax.set_ylabel('Skor Minat')
        ax.set_title('Profil Minat Holland (RIASEC)')
        ax.set_ylim(0, max(values) + 2 if values else 10)
        
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, int(yval), va='bottom', ha='center', fontsize=10)

        fig.patch.set_alpha(0) # Transparan untuk figure background
        ax.patch.set_alpha(0)  # Transparan untuk axes background
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', transparent=True)
        buf.seek(0)
        plt.close(fig)
        return buf
    
    def reset_quiz(self):
        """Meriset status kuesioner."""
        self.current_question_index = 0
        for q_id in self.df_holland['id']:
            self.answer_vars[q_id].set("None")

