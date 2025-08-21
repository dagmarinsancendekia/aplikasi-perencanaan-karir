import customtkinter
import pandas as pd
import tkinter.messagebox # Untuk menampilkan pesan pop-up

# Pengaturan dasar CustomTkinter
customtkinter.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

class CareerGuidanceApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aplikasi Perencanaan Karir")
        self.geometry("800x700") # Ukuran jendela utama
        self.grid_columnconfigure(0, weight=1) # Agar konten di tengah
        self.grid_rowconfigure(0, weight=1)

        # Memuat data sekali saat aplikasi dimulai
        self.df_holland = pd.read_csv('data/tes_holland.csv')

        # Data tambahan untuk deskripsi singkat setiap kategori RIASEC
        self.riasec_descriptions = {
            'R': 'Realistis (Doers): Praktis, suka bekerja dengan tangan, alat, dan mesin.',
            'I': 'Investigatif (Thinkers): Analitis, suka memecahkan masalah, melakukan penelitian, dan berpikir kritis.',
            'A': 'Artistik (Creators): Ekspresif, inovatif, suka seni, musik, drama, dan desain.',
            'S': 'Sosial (Helpers): Peduli, suka membantu, mengajar, dan berinteraksi dengan orang lain.',
            'E': 'Enterprising (Persuaders): Ambisius, suka memimpin, mempengaruhi, dan bernegosiasi.',
            'C': 'Konvensional (Organizers): Teratur, teliti, suka bekerja dengan data, angka, dan detail.'
        }
        
        self.answer_vars = {} # Untuk menyimpan pilihan jawaban radio button

        self.create_widgets()

    def create_widgets(self):
        # Frame utama yang bisa di-scroll untuk menampung pertanyaan
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="Temukan Minat Karir Anda!")
        self.scrollable_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Instruksi
        instruction_label = customtkinter.CTkLabel(self.scrollable_frame, 
                                                   text="Jawablah pertanyaan-pertanyaan berikut dengan jujur untuk mengungkap tipe minat Anda berdasarkan Teori Holland (RIASEC) dan dapatkan rekomendasi karir yang sesuai.",
                                                   wraplength=700, # Batas lebar teks
                                                   font=customtkinter.CTkFont(size=14))
        instruction_label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="ew")

        # Menambahkan pertanyaan
        for i, row in self.df_holland.iterrows():
            question_frame = customtkinter.CTkFrame(self.scrollable_frame)
            question_frame.grid(row=i+1, column=0, padx=10, pady=5, sticky="ew")
            question_frame.grid_columnconfigure(0, weight=1) # Agar pertanyaan rata kiri

            question_label = customtkinter.CTkLabel(question_frame, 
                                                    text=f"{i+1}. {row['pertanyaan']}", 
                                                    wraplength=650, # Batas lebar teks pertanyaan
                                                    font=customtkinter.CTkFont(size=16, weight="bold"))
            question_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

            self.answer_vars[row['id']] = customtkinter.StringVar(value="None") # Default value

            radio_setuju = customtkinter.CTkRadioButton(question_frame, text="Setuju", 
                                                         variable=self.answer_vars[row['id']], value="setuju",
                                                         font=customtkinter.CTkFont(size=14))
            radio_setuju.grid(row=1, column=0, padx=10, pady=5, sticky="w")

            radio_tidak_setuju = customtkinter.CTkRadioButton(question_frame, text="Tidak Setuju", 
                                                               variable=self.answer_vars[row['id']], value="tidak_setuju",
                                                               font=customtkinter.CTkFont(size=14))
            radio_tidak_setuju.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Tombol submit
        submit_button = customtkinter.CTkButton(self, text="Lihat Hasil Tes", command=self.show_results)
        submit_button.grid(row=1, column=0, padx=20, pady=20) # Di luar scrollable frame

    def show_results(self):
        # Inisialisasi skor
        skor = {kategori: 0 for kategori in self.df_holland['kategori'].unique()}
        
        # Cek apakah semua pertanyaan sudah dijawab
        all_answered = True
        for q_id in self.df_holland['id']:
            if self.answer_vars[q_id].get() == "None":
                all_answered = False
                break
        
        if not all_answered:
            tkinter.messagebox.showwarning("Peringatan", "Mohon jawab semua pertanyaan sebelum melihat hasil.")
            return

        # Mengolah jawaban
        for i, row in self.df_holland.iterrows():
            question_id = row['id']
            answer = self.answer_vars[question_id].get()
            if answer == 'setuju':
                kategori = row['kategori']
                if kategori in skor:
                    skor[kategori] += 1
        
        # Menentukan kategori dengan skor tertinggi
        if not any(skor.values()): # Fallback jika entah mengapa skor masih kosong
            kategori_tertinggi = "Tidak Ada Jawaban"
            deskripsi = "Sepertinya ada masalah dalam pemrosesan jawaban Anda."
            rekomendasi_list = ["Silakan coba tes lagi."]
        else:
            kategori_tertinggi = max(skor, key=skor.get)
            data_tertinggi = self.df_holland[self.df_holland['kategori'] == kategori_tertinggi].iloc[0]
            
            deskripsi = data_tertinggi['deskripsi']
            rekomendasi_list = [item.strip() for item in data_tertinggi['rekomendasi_karir'].split(',')]

        self.open_results_window(kategori_tertinggi, deskripsi, rekomendasi_list, skor)

    def open_results_window(self, kategori_tertinggi, deskripsi, rekomendasi_list, skor_lengkap):
        # Membuat jendela baru untuk hasil
        results_window = customtkinter.CTkToplevel(self)
        results_window.title("Hasil Tes Karir Anda")
        results_window.geometry("700x600")
        results_window.grab_set() # Membuat jendela ini fokus sampai ditutup
        results_window.resizable(False, False) # Nonaktifkan resize

        results_window.grid_columnconfigure(0, weight=1)
        results_window.grid_rowconfigure(0, weight=1)

        # Scrollable frame untuk hasil
        results_scroll_frame = customtkinter.CTkScrollableFrame(results_window)
        results_scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        results_scroll_frame.grid_columnconfigure(0, weight=1)

        # Kategori tertinggi
        label_tertinggi = customtkinter.CTkLabel(results_scroll_frame, 
                                                 text=f"Kategori minat tertinggi Anda adalah: {kategori_tertinggi}",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"),
                                                 wraplength=600)
        label_tertinggi.grid(row=0, column=0, pady=(10, 5), sticky="ew")

        # Deskripsi tipe minat
        label_desc_title = customtkinter.CTkLabel(results_scroll_frame, 
                                                 text="Deskripsi Tipe Minat Anda:",
                                                 font=customtkinter.CTkFont(size=16, weight="bold"),
                                                 wraplength=600)
        label_desc_title.grid(row=1, column=0, pady=(15, 5), sticky="ew")
        label_desc = customtkinter.CTkLabel(results_scroll_frame, 
                                           text=deskripsi,
                                           font=customtkinter.CTkFont(size=14),
                                           wraplength=600, justify="left")
        label_desc.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Rekomendasi Karir
        label_rekom_title = customtkinter.CTkLabel(results_scroll_frame, 
                                                  text="Rekomendasi Karir untuk Anda:",
                                                  font=customtkinter.CTkFont(size=16, weight="bold"),
                                                  wraplength=600)
        label_rekom_title.grid(row=3, column=0, pady=(15, 5), sticky="ew")
        
        for i, karir in enumerate(rekomendasi_list):
            karir_label = customtkinter.CTkLabel(results_scroll_frame, 
                                                 text=f"- {karir}",
                                                 font=customtkinter.CTkFont(size=14),
                                                 wraplength=600, justify="left")
            karir_label.grid(row=4+i, column=0, padx=10, pady=2, sticky="ew")

        # Ringkasan Skor Lengkap
        label_skor_title = customtkinter.CTkLabel(results_scroll_frame, 
                                                 text="Skor Minat Anda untuk Setiap Tipe Holland (RIASEC):",
                                                 font=customtkinter.CTkFont(size=16, weight="bold"),
                                                 wraplength=600)
        label_skor_title.grid(row=4+len(rekomendasi_list)+1, column=0, pady=(20, 5), sticky="ew")

        for i, (kategori, nilai) in enumerate(skor_lengkap.items()):
            score_item_frame = customtkinter.CTkFrame(results_scroll_frame)
            score_item_frame.grid(row=4+len(rekomendasi_list)+2+i, column=0, padx=10, pady=5, sticky="ew")
            score_item_frame.grid_columnconfigure(0, weight=1)

            score_text = f"[{kategori}] {self.riasec_descriptions[kategori].split(':')[0]} : {nilai} Poin"
            score_label = customtkinter.CTkLabel(score_item_frame, 
                                                 text=score_text,
                                                 font=customtkinter.CTkFont(size=14, weight="bold"),
                                                 wraplength=550, justify="left")
            score_label.grid(row=0, column=0, padx=10, pady=2, sticky="w")
            
            desc_text = self.riasec_descriptions[kategori].split(':', 1)[1].strip()
            desc_label = customtkinter.CTkLabel(score_item_frame,
                                                text=desc_text,
                                                font=customtkinter.CTkFont(size=12),
                                                wraplength=550, justify="left")
            desc_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")


        # Tombol Ulangi Tes
        restart_button = customtkinter.CTkButton(results_window, text="Ulangi Tes", command=results_window.destroy)
        restart_button.grid(row=1, column=0, padx=20, pady=20)


if __name__ == '__main__':
    app = CareerGuidanceApp()
    app.mainloop()

