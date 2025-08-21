import customtkinter
import pandas as pd
import tkinter.messagebox
from tkinter import filedialog # Untuk fitur simpan file
import os # Untuk memeriksa keberadaan file
import csv # Import modul csv

# Import untuk PDF generation
from reportlab.lib.pagesizes import letter # Ukuran halaman (misal: A4, letter)
from reportlab.pdfgen import canvas # Untuk membuat dokumen PDF
from reportlab.lib.units import inch # Satuan ukuran (misal: inci)
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Pengaturan dasar CustomTkinter
customtkinter.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

class CareerGuidanceApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aplikasi Perencanaan Karir")
        self.geometry("800x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Hanya satu baris utama yang akan berisi frame

        # Memuat data sekali saat aplikasi dimulai
        self.df_holland = pd.read_csv('data/tes_holland.csv')
        self.questions_data = self.df_holland.to_dict('records')
        self.total_questions = len(self.questions_data)
        self.current_question_index = 0

        # Data tambahan untuk deskripsi singkat setiap kategori RIASEC
        self.riasec_descriptions = {
            'R': 'Realistis (Doers): Praktis, suka bekerja dengan tangan, alat, dan mesin.',
            'I': 'Investigatif (Thinkers): Analitis, suka memecahkan masalah, melakukan penelitian, dan berpikir kritis.',
            'A': 'Artistik (Creators): Ekspresif, inovatif, suka seni, musik, drama, dan desain.',
            'S': 'Sosial (Helpers): Peduli, suka membantu, mengajar, dan berinteraksi dengan orang lain.',
            'E': 'Enterprising (Persuaders): Ambisius, suka memimpin, mempengaruhi, dan bernegosiasi.',
            'C': 'Konvensional (Organizers): Teratur, teliti, suka bekerja dengan data, angka, dan detail.'
        }
        
        self.answer_vars = {}
        for row in self.df_holland.to_dict('records'):
            self.answer_vars[row['id']] = customtkinter.StringVar(value="None")
        
        self.user_data = {
            "nama": "",
            "alamat": "",
            "usia": "",
            "nomor_hp": ""
        }
        self.user_data_csv_file = 'user_records.csv' # Nama file CSV untuk menyimpan data pengguna

        self.create_start_screen() # Tampilkan layar awal saat aplikasi dimulai

    def clear_screen(self):
        """Menghapus semua widget dari jendela utama."""
        for widget in self.winfo_children():
            widget.destroy()

    def create_start_screen(self):
        """Membuat layar awal untuk input data pengguna."""
        self.clear_screen() # Pastikan layar bersih

        self.start_frame = customtkinter.CTkFrame(self)
        self.start_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.start_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(self.start_frame, 
                               text="Selamat Datang di Aplikasi Perencanaan Karir!",
                               font=customtkinter.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(20, 10))
        
        customtkinter.CTkLabel(self.start_frame, 
                               text="Silakan masukkan data diri Anda sebelum memulai tes:",
                               font=customtkinter.CTkFont(size=14)).grid(row=1, column=0, pady=(0, 20))

        # Input fields
        self.entry_widgets = {}
        labels = ["Nama Lengkap", "Alamat", "Usia", "Nomor HP"]
        keys = ["nama", "alamat", "usia", "nomor_hp"]

        for i, (label_text, key) in enumerate(zip(labels, keys)):
            frame_input = customtkinter.CTkFrame(self.start_frame, fg_color="transparent")
            frame_input.grid(row=2+i, column=0, pady=5, sticky="ew")
            frame_input.grid_columnconfigure((0,1), weight=1)

            customtkinter.CTkLabel(frame_input, text=f"{label_text}:", width=120, anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            entry = customtkinter.CTkEntry(frame_input, placeholder_text=label_text, width=300)
            entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            self.entry_widgets[key] = entry
        
        start_button = customtkinter.CTkButton(self.start_frame, text="Mulai Tes", command=self.start_test_flow)
        start_button.grid(row=len(labels)+2, column=0, pady=30)

    def save_user_data_to_csv(self):
        """Menyimpan data pengguna ke file CSV."""
        file_exists = os.path.isfile(self.user_data_csv_file)
        
        try:
            with open(self.user_data_csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f) # Menggunakan csv.writer
                if not file_exists:
                    writer.writerow(list(self.user_data.keys())) # Tulis header jika file baru
                writer.writerow(list(self.user_data.values()))
            # tkinter.messagebox.showinfo("Informasi", "Data pengguna berhasil disimpan.")
        except Exception as e:
            tkinter.messagebox.showerror("Error Simpan Data", f"Gagal menyimpan data pengguna: {e}")


    def start_test_flow(self):
        """Memvalidasi data pengguna, menyimpan, dan memulai kuesioner."""
        # Ambil data dari entry fields
        for key, entry in self.entry_widgets.items():
            self.user_data[key] = entry.get().strip()

        # Validasi sederhana
        if not all(self.user_data.values()):
            tkinter.messagebox.showwarning("Peringatan", "Mohon lengkapi semua data diri sebelum memulai tes.")
            return
        
        # Validasi usia harus angka
        if not self.user_data["usia"].isdigit():
            tkinter.messagebox.showwarning("Peringatan", "Usia harus berupa angka.")
            return

        # Simpan data pengguna ke CSV
        self.save_user_data_to_csv()

        self.clear_screen() # Hapus layar awal
        self.create_quiz_widgets() # Buat UI kuesioner
        self.display_current_question() # Tampilkan pertanyaan pertama

    def create_quiz_widgets(self):
        """Membuat antarmuka untuk kuesioner (satu pertanyaan per layar)."""
        self.quiz_frame = customtkinter.CTkFrame(self)
        self.quiz_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.quiz_frame.grid_columnconfigure(0, weight=1)
        self.quiz_frame.grid_rowconfigure((0, 1, 2), weight=1) # Baris untuk instruksi, pertanyaan, dan navigasi

        # Instruksi
        instruction_label = customtkinter.CTkLabel(self.quiz_frame, 
                                                   text="Jawablah pertanyaan-pertanyaan berikut dengan jujur untuk mengungkap tipe minat Anda:",
                                                   wraplength=700,
                                                   font=customtkinter.CTkFont(size=14))
        instruction_label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="ew")

        # Frame untuk menampilkan satu pertanyaan saat ini
        self.question_display_frame = customtkinter.CTkFrame(self.quiz_frame, fg_color="transparent")
        self.question_display_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.question_display_frame.grid_columnconfigure(0, weight=1)
        self.question_display_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # Frame untuk tombol navigasi (Sebelumnya/Selanjutnya/Lihat Hasil)
        self.navigation_frame = customtkinter.CTkFrame(self.quiz_frame, fg_color="transparent")
        self.navigation_frame.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="ew")
        self.navigation_frame.grid_columnconfigure((0, 1), weight=1)

        self.prev_button = customtkinter.CTkButton(self.navigation_frame, text="Sebelumnya", command=self.go_previous)
        self.prev_button.grid(row=0, column=0, padx=5, pady=10, sticky="e")

        # Tombol "Selanjutnya" akan diatur di display_current_question
        self.next_button = customtkinter.CTkButton(self.navigation_frame, text="Selanjutnya", command=self.go_next_manual)
        self.next_button.grid(row=0, column=1, padx=5, pady=10, sticky="w")


    def display_current_question(self):
        """Menampilkan pertanyaan saat ini dan mengelola status tombol."""
        # Hapus widget yang ada di frame pertanyaan
        for widget in self.question_display_frame.winfo_children():
            widget.destroy()

        if self.current_question_index < self.total_questions:
            current_q_data = self.questions_data[self.current_question_index]
            question_id = current_q_data['id']

            question_label = customtkinter.CTkLabel(self.question_display_frame, 
                                                    text=f"{self.current_question_index + 1}. {current_q_data['pertanyaan']}", 
                                                    wraplength=650, 
                                                    font=customtkinter.CTkFont(size=18, weight="bold"))
            question_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="w")

            # Membuat tombol "Setuju" dan "Tidak Setuju"
            # Style default
            default_button_color = customtkinter.ThemeManager.theme["CTkButton"]["fg_color"]
            selected_button_color = customtkinter.ThemeManager.theme["CTkButton"]["hover_color"] # Warna saat hover untuk indikasi terpilih

            setuju_btn = customtkinter.CTkButton(
                self.question_display_frame, 
                text="Setuju",
                font=customtkinter.CTkFont(size=16),
                command=lambda: self.on_answer_button_click(question_id, "setuju")
            )
            setuju_btn.grid(row=1, column=0, padx=10, pady=5, sticky="w", ipadx=20, ipady=10)

            tidak_setuju_btn = customtkinter.CTkButton(
                self.question_display_frame, 
                text="Tidak Setuju",
                font=customtkinter.CTkFont(size=16),
                command=lambda: self.on_answer_button_click(question_id, "tidak_setuju")
            )
            tidak_setuju_btn.grid(row=2, column=0, padx=10, pady=5, sticky="w", ipadx=20, ipady=10)

            # Menyimpan referensi tombol untuk perubahan warna
            self.current_answer_buttons = {
                "setuju": setuju_btn,
                "tidak_setuju": tidak_setuju_btn
            }

            # Menandai pilihan yang sudah ada (jika kembali ke pertanyaan sebelumnya)
            current_selection = self.answer_vars[question_id].get()
            if current_selection != "None":
                if current_selection == "setuju":
                    setuju_btn.configure(fg_color=selected_button_color)
                else:
                    tidak_setuju_btn.configure(fg_color=selected_button_color)


            # Atur status tombol navigasi
            self.prev_button.configure(state="normal" if self.current_question_index > 0 else "disabled")
            
            # Tombol "Selanjutnya" akan menjadi "Lihat Hasil Tes" di pertanyaan terakhir
            if self.current_question_index == self.total_questions - 1:
                self.next_button.configure(text="Lihat Hasil Tes", command=self.show_results)
            else:
                self.next_button.configure(text="Selanjutnya", command=self.go_next_manual)
        else:
            # Ini adalah fallback jika current_question_index melebihi batas
            self.show_results()

    def on_answer_button_click(self, question_id, answer_value):
        """Memproses klik tombol jawaban, menandai pilihan, dan otomatis melanjutkan."""
        # Reset warna semua tombol jawaban untuk pertanyaan ini
        default_button_color = customtkinter.ThemeManager.theme["CTkButton"]["fg_color"]
        selected_button_color = customtkinter.ThemeManager.theme["CTkButton"]["hover_color"]
        
        for btn_value, button_widget in self.current_answer_buttons.items():
            if btn_value == answer_value:
                button_widget.configure(fg_color=selected_button_color) # Tandai yang terpilih
            else:
                button_widget.configure(fg_color=default_button_color) # Reset yang lain

        self.answer_vars[question_id].set(answer_value) # Simpan jawaban
        self.auto_advance_on_select() # Otomatis lanjut


    def auto_advance_on_select(self):
        """Otomatis melanjutkan ke pertanyaan berikutnya setelah radio button dipilih."""
        # Logic ini sekarang lebih sederhana karena dipanggil setelah jawaban dipastikan dipilih
        if self.current_question_index < self.total_questions - 1:
            self.current_question_index += 1
            self.display_current_question()
        elif self.current_question_index == self.total_questions - 1:
            # Jika ini pertanyaan terakhir dan dijawab, otomatis tampilkan hasil
            self.show_results()

    def go_next_manual(self):
        """Digunakan jika pengguna secara manual mengklik tombol 'Selanjutnya'/'Lihat Hasil Tes'."""
        current_q_id = self.questions_data[self.current_question_index]['id']
        if self.answer_vars[current_q_id].get() == "None":
            tkinter.messagebox.showwarning("Peringatan", "Mohon pilih jawaban untuk pertanyaan ini sebelum melanjutkan.")
            return

        if self.current_question_index < self.total_questions - 1:
            self.current_question_index += 1
            self.display_current_question()
        else:
            self.show_results() # Semua pertanyaan sudah dijawab, tampilkan hasil

    def go_previous(self):
        """Kembali ke pertanyaan sebelumnya."""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.display_current_question()
        else:
            self.prev_button.configure(state="disabled") # Nonaktifkan jika sudah di pertanyaan pertama

    def show_results(self):
        """Memproses jawaban dan menampilkan jendela hasil."""
        # Inisialisasi skor
        skor = {kategori: 0 for kategori in self.df_holland['kategori'].unique()}
        
        # Cek apakah semua pertanyaan sudah dijawab (cek lagi untuk jaga-jaga)
        all_answered = True
        for q_id in self.df_holland['id']:
            if self.answer_vars[q_id].get() == "None":
                all_answered = False
                break
        
        if not all_answered:
            tkinter.messagebox.showwarning("Peringatan", "Mohon jawab semua pertanyaan sebelum melihat hasil.")
            # Kembali ke pertanyaan terakhir jika ada yang belum dijawab
            self.current_question_index = self.total_questions - 1 
            self.display_current_question() 
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
        if not any(skor.values()):
            kategori_tertinggi = "Tidak Ada Jawaban"
            deskripsi = "Sepertinya ada masalah dalam pemrosesan jawaban Anda."
            rekomendasi_list = ["Silakan coba tes lagi."]
        else:
            # Cari kategori dengan skor tertinggi
            max_score = 0
            kategori_tertinggi = None
            for k, v in skor.items():
                if v > max_score:
                    max_score = v
                    kategori_tertinggi = k
                # Handle cases where multiple categories have the same max score (e.g., pick the first one encountered)
                # For more sophisticated handling, you might return all max categories.
                elif v == max_score and kategori_tertinggi: 
                    pass 

            if kategori_tertinggi is None: # Fallback jika semua skor 0
                 kategori_tertinggi = "Tidak Ada Jawaban"
                 deskripsi = "Tidak ada jawaban 'Setuju' yang dipilih."
                 rekomendasi_list = ["Tidak ada rekomendasi spesifik."]
            else:
                data_tertinggi = self.df_holland[self.df_holland['kategori'] == kategori_tertinggi].iloc[0]
                deskripsi = data_tertinggi['deskripsi']
                rekomendasi_list = [item.strip() for item in data_tertinggi['rekomendasi_karir'].split(',')]

        self.open_results_window(kategori_tertinggi, deskripsi, rekomendasi_list, skor)

    def open_results_window(self, kategori_tertinggi, deskripsi, rekomendasi_list, skor_lengkap):
        """Membuka jendela baru untuk menampilkan hasil tes dan data pengguna."""
        self.results_window = customtkinter.CTkToplevel(self) # Simpan referensi ke jendela
        self.results_window.title("Hasil Tes Karir Anda")
        self.results_window.geometry("700x750")
        self.results_window.grab_set()
        self.results_window.resizable(False, False)

        self.results_window.grid_columnconfigure(0, weight=1)
        self.results_window.grid_rowconfigure((0, 1), weight=1)

        results_scroll_frame = customtkinter.CTkScrollableFrame(self.results_window)
        results_scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        results_scroll_frame.grid_columnconfigure(0, weight=1)

        # Bagian Data Pengguna
        customtkinter.CTkLabel(results_scroll_frame, 
                               text="Data Pengguna:",
                               font=customtkinter.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(10, 5), sticky="w")
        
        user_data_text = (f"Nama: {self.user_data['nama']}\n"
                          f"Alamat: {self.user_data['alamat']}\n"
                          f"Usia: {self.user_data['usia']} tahun\n"
                          f"Nomor HP: {self.user_data['nomor_hp']}")
        customtkinter.CTkLabel(results_scroll_frame, 
                               text=user_data_text,
                               font=customtkinter.CTkFont(size=14),
                               justify="left", wraplength=600).grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Hasil Tes
        customtkinter.CTkLabel(results_scroll_frame, 
                               text=f"Kategori minat tertinggi Anda adalah: {kategori_tertinggi}",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=2, column=0, pady=(20, 5), sticky="ew")

        customtkinter.CTkLabel(results_scroll_frame, 
                               text="Deskripsi Tipe Minat Anda:",
                               font=customtkinter.CTkFont(size=16, weight="bold")).grid(row=3, column=0, pady=(15, 5), sticky="ew")
        customtkinter.CTkLabel(results_scroll_frame, 
                               text=deskripsi,
                               font=customtkinter.CTkFont(size=14),
                               wraplength=600, justify="left").grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        customtkinter.CTkLabel(results_scroll_frame, 
                               text="Rekomendasi Karir untuk Anda:",
                               font=customtkinter.CTkFont(size=16, weight="bold")).grid(row=5, column=0, pady=(15, 5), sticky="ew")
        
        for i, karir in enumerate(rekomendasi_list):
            customtkinter.CTkLabel(results_scroll_frame, 
                                 text=f"- {karir}",
                                 font=customtkinter.CTkFont(size=14),
                                 wraplength=600, justify="left").grid(row=6+i, column=0, padx=10, pady=2, sticky="ew")

        customtkinter.CTkLabel(results_scroll_frame, 
                               text="Skor Minat Anda untuk Setiap Tipe Holland (RIASEC):",
                               font=customtkinter.CTkFont(size=16, weight="bold")).grid(row=6+len(rekomendasi_list)+1, column=0, pady=(20, 5), sticky="ew")

        for i, (kategori, nilai) in enumerate(skor_lengkap.items()):
            score_item_frame = customtkinter.CTkFrame(results_scroll_frame, fg_color="transparent")
            score_item_frame.grid(row=6+len(rekomendasi_list)+2+i, column=0, padx=10, pady=5, sticky="ew")
            score_item_frame.grid_columnconfigure(0, weight=1)

            score_text = f"[{kategori}] {self.riasec_descriptions[kategori].split(':')[0]} : {nilai} Poin"
            customtkinter.CTkLabel(score_item_frame, 
                                 text=score_text,
                                 font=customtkinter.CTkFont(size=14, weight="bold"),
                                 wraplength=550, justify="left").grid(row=0, column=0, padx=10, pady=2, sticky="w")
            
            desc_text = self.riasec_descriptions[kategori].split(':', 1)[1].strip()
            customtkinter.CTkLabel(score_item_frame,
                                 text=desc_text,
                                 font=customtkinter.CTkFont(size=12),
                                 wraplength=550, justify="left").grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        # Tombol Download dan Ulangi Tes
        button_frame = customtkinter.CTkFrame(self.results_window, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        download_button = customtkinter.CTkButton(button_frame, 
                                                 text="Unduh Hasil (PDF)", 
                                                 command=lambda: self.download_results(kategori_tertinggi, deskripsi, rekomendasi_list, skor_lengkap))
        download_button.grid(row=0, column=0, padx=5, pady=10, sticky="e")

        restart_button = customtkinter.CTkButton(button_frame, text="Ulangi Tes", command=self.reset_and_start_over)
        restart_button.grid(row=0, column=1, padx=5, pady=10, sticky="w")

    def download_results(self, kategori_tertinggi, deskripsi, rekomendasi_list, skor_lengkap):
        """Menyimpan hasil tes dan data pengguna ke file PDF."""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf", 
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"Hasil_Tes_Karir_{self.user_data['nama'].replace(' ', '_')}.pdf"
            )

            if not file_path:
                tkinter.messagebox.showinfo("Info", "Pengunduhan dibatalkan.")
                return

            c = canvas.Canvas(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            style_title = ParagraphStyle(
                'Title',
                parent=styles['h1'],
                fontSize=24,
                alignment=TA_CENTER,
                spaceAfter=20
            )
            style_heading = ParagraphStyle(
                'Heading',
                parent=styles['h2'],
                fontSize=16,
                alignment=TA_LEFT,
                spaceAfter=10,
                spaceBefore=15
            )
            style_normal = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_LEFT,
                spaceAfter=5
            )
            style_bold = ParagraphStyle(
                'Bold',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                spaceAfter=5
            )
            style_list = ParagraphStyle(
                'List',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_LEFT,
                leftIndent=20,
                spaceAfter=2
            )
            style_score_heading = ParagraphStyle(
                'ScoreHeading',
                parent=styles['h3'],
                fontSize=14,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                spaceAfter=5
            )
            style_score_detail = ParagraphStyle(
                'ScoreDetail',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_LEFT,
                leftIndent=10,
                spaceAfter=2
            )

            y_pos = 10.5 * inch 
            x_left = inch 

            P = Paragraph("Hasil Tes Perencanaan Karir", style_title)
            P.wrapOn(c, letter[0] - 2*inch, letter[1]) 
            P.drawOn(c, inch, y_pos - P.height)
            y_pos -= P.height + 0.2*inch 

            P = Paragraph("--- Data Pengguna ---", style_heading)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.1*inch

            user_data_lines = [
                f"<b>Nama:</b> {self.user_data['nama']}",
                f"<b>Alamat:</b> {self.user_data['alamat']}",
                f"<b>Usia:</b> {self.user_data['usia']} tahun",
                f"<b>Nomor HP:</b> {self.user_data['nomor_hp']}"
            ]
            for line in user_data_lines:
                P = Paragraph(line, style_normal)
                P.wrapOn(c, letter[0] - 2*inch, letter[1])
                P.drawOn(c, x_left, y_pos - P.height)
                y_pos -= P.height + 0.05*inch
            y_pos -= 0.2*inch 

            P = Paragraph("--- Hasil Tes ---", style_heading)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.1*inch
            
            P = Paragraph(f"<b>Kategori minat tertinggi Anda adalah: {kategori_tertinggi}</b>", style_bold)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.1*inch

            P = Paragraph("Deskripsi Tipe Minat Anda:", style_score_heading)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.05*inch
            P = Paragraph(deskripsi, style_normal)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.2*inch

            P = Paragraph("Rekomendasi Karir untuk Anda:", style_score_heading)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.05*inch
            for karir in rekomendasi_list:
                P = Paragraph(f"- {karir}", style_list)
                P.wrapOn(c, letter[0] - 2*inch, letter[1])
                P.drawOn(c, x_left, y_pos - P.height)
                y_pos -= P.height + 0.02*inch
            y_pos -= 0.2*inch

            P = Paragraph("--- Skor Minat Anda untuk Setiap Tipe Holland (RIASEC) ---", style_heading)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.1*inch

            for kategori, nilai in skor_lengkap.items():
                score_line = f"<b>[{kategori}] {self.riasec_descriptions[kategori].split(':')[0]} :</b> {nilai} Poin"
                P = Paragraph(score_line, style_score_heading)
                P.wrapOn(c, letter[0] - 2*inch, letter[1])
                P.drawOn(c, x_left, y_pos - P.height)
                y_pos -= P.height + 0.02*inch

                desc_detail = self.riasec_descriptions[kategori].split(':', 1)[1].strip()
                P = Paragraph(desc_detail, style_score_detail)
                P.wrapOn(c, letter[0] - 2*inch, letter[1])
                P.drawOn(c, x_left, y_pos - P.height)
                y_pos -= P.height + 0.1*inch 
                
                if y_pos < inch: 
                    c.showPage()
                    y_pos = 10.5 * inch 
                    
            c.save()
            tkinter.messagebox.showinfo("Berhasil", f"Hasil tes berhasil diunduh ke:\n{file_path}")

        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Terjadi kesalahan saat mengunduh hasil: {e}")

    def reset_and_start_over(self):
        """Meriset aplikasi dan kembali ke layar awal."""
        # Reset state
        self.current_question_index = 0
        for q_id in self.df_holland['id']:
            self.answer_vars[q_id].set("None")
        self.user_data = {
            "nama": "",
            "alamat": "",
            "usia": "",
            "nomor_hp": ""
        }
        # Tutup jendela hasil jika masih terbuka
        if hasattr(self, 'results_window') and self.results_window.winfo_exists():
            self.results_window.destroy()
        
        self.create_start_screen()


if __name__ == '__main__':
    app = CareerGuidanceApp()
    app.mainloop()

