import customtkinter
import pandas as pd
import tkinter.messagebox
import io
import base64
from PIL import Image

# Import modul yang sudah dipisahkan
from quiz_logic import QuizLogic
from report_generator import ReportGenerator
from user_data_manager import UserDataManager

# Pengaturan dasar CustomTkinter
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class CareerGuidanceApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aplikasi Perencanaan Karir")
        self.geometry("800x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Inisialisasi logika kuesioner, data pengguna, dan generator laporan
        self.quiz_logic = QuizLogic('data/tes_holland.csv')
        self.user_data_manager = UserDataManager('user_records.csv')
        self.report_generator = ReportGenerator()

        self.user_data = {
            "nama": "",
            "alamat": "",
            "usia": "",
            "nomor_hp": ""
        }
        
        self.create_start_screen()

    def clear_screen(self):
        """Menghapus semua widget dari jendela utama."""
        for widget in self.winfo_children():
            widget.destroy()

    def create_start_screen(self):
        """Membuat layar awal untuk input data pengguna dengan tampilan yang lebih menarik."""
        self.clear_screen()

        # Frame utama untuk menampung konten layar awal, berpusat
        main_start_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_start_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_start_frame.grid_columnconfigure(0, weight=1)
        main_start_frame.grid_rowconfigure(0, weight=1) # Agar inner_frame bisa berpusat vertikal

        # Inner frame sebagai 'card' untuk data input
        self.start_card_frame = customtkinter.CTkFrame(main_start_frame, corner_radius=15, fg_color=("gray85", "gray15")) # Sudut membulat, warna abu-abu pastel
        self.start_card_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.start_card_frame.grid_columnconfigure(0, weight=1)
        
        # Judul Utama
        customtkinter.CTkLabel(self.start_card_frame, 
                               text="Selamat Datang di Aplikasi Perencanaan Karir!",
                               font=customtkinter.CTkFont(size=28, weight="bold"), # Font lebih besar dan tebal
                               text_color=("gray10", "gray90")).grid(row=0, column=0, pady=(30, 10)) # Warna teks disesuaikan

        # Instruksi
        customtkinter.CTkLabel(self.start_card_frame, 
                               text="Kami akan membantu Anda menemukan minat karir. Untuk memulai, mohon isi data diri Anda di bawah ini:",
                               font=customtkinter.CTkFont(size=15),
                               wraplength=500, # Batasi panjang teks agar rapi
                               justify="center", # Teks rata tengah
                               text_color=("gray20", "gray70")).grid(row=1, column=0, pady=(0, 25))

        # Frame untuk input field agar lebih teratur
        input_fields_frame = customtkinter.CTkFrame(self.start_card_frame, fg_color="transparent")
        input_fields_frame.grid(row=2, column=0, pady=10)
        input_fields_frame.grid_columnconfigure(0, weight=1)
        input_fields_frame.grid_columnconfigure(1, weight=3) # Kolom input lebih lebar

        self.entry_widgets = {}
        labels = ["Nama Lengkap", "Alamat", "Usia", "Nomor HP"]
        keys = ["nama", "alamat", "usia", "nomor_hp"]

        for i, (label_text, key) in enumerate(zip(labels, keys)):
            # label_text
            customtkinter.CTkLabel(input_fields_frame, 
                                   text=f"{label_text}:", 
                                   font=customtkinter.CTkFont(size=14, weight="bold"), # Label input juga bold
                                   text_color=("gray20", "gray70"),
                                   anchor="w").grid(row=i, column=0, padx=15, pady=8, sticky="w")
            # Entry field
            entry = customtkinter.CTkEntry(input_fields_frame, 
                                           placeholder_text=label_text, 
                                           width=300, 
                                           height=35, # Tinggi entry field
                                           corner_radius=10, # Sudut membulat untuk entry
                                           font=customtkinter.CTkFont(size=14))
            entry.grid(row=i, column=1, padx=15, pady=8, sticky="ew")
            self.entry_widgets[key] = entry
        
        # Tombol Mulai Tes
        start_button = customtkinter.CTkButton(self.start_card_frame, 
                                               text="Mulai Tes", 
                                               command=self.start_test_flow,
                                               font=customtkinter.CTkFont(size=18, weight="bold"), # Font tombol lebih besar
                                               height=45, # Tinggi tombol
                                               corner_radius=10, # Sudut membulat
                                               fg_color="#4A90E2", # Warna biru yang konsisten
                                               hover_color="#3A7DC1") # Warna hover yang sedikit lebih gelap
        start_button.grid(row=3, column=0, pady=(30, 30)) # Posisi tombol setelah input fields

    def start_test_flow(self):
        """Memvalidasi data pengguna, menyimpan, dan memulai kuesioner."""
        for key, entry in self.entry_widgets.items():
            self.user_data[key] = entry.get().strip()

        if not all(self.user_data.values()):
            tkinter.messagebox.showwarning("Peringatan", "Mohon lengkapi semua data diri sebelum memulai tes.")
            return
        
        if not self.user_data["usia"].isdigit():
            tkinter.messagebox.showwarning("Peringatan", "Usia harus berupa angka.")
            return

        self.user_data_manager.save_user_data(self.user_data) # Menggunakan UserDataManager

        self.clear_screen()
        self.create_quiz_widgets()
        self.display_current_question()

    def create_quiz_widgets(self):
        """Membuat antarmuka untuk kuesioner (satu pertanyaan per layar)."""
        self.quiz_frame = customtkinter.CTkFrame(self)
        self.quiz_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.quiz_frame.grid_columnconfigure(0, weight=1)
        self.quiz_frame.grid_rowconfigure((0, 1, 2), weight=1)

        instruction_label = customtkinter.CTkLabel(self.quiz_frame, 
                                                   text="Jawablah pertanyaan-pertanyaan berikut dengan jujur untuk mengungkap tipe minat Anda:",
                                                   wraplength=700,
                                                   font=customtkinter.CTkFont(size=14))
        instruction_label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="ew")

        self.question_display_frame = customtkinter.CTkFrame(self.quiz_frame, fg_color="transparent")
        self.question_display_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.question_display_frame.grid_columnconfigure(0, weight=1) 
        self.question_display_frame.grid_rowconfigure((0, 1, 2), weight=1)

        self.navigation_frame = customtkinter.CTkFrame(self.quiz_frame, fg_color="transparent")
        self.navigation_frame.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="ew")
        self.navigation_frame.grid_columnconfigure((0, 1), weight=1)

        self.prev_button = customtkinter.CTkButton(self.navigation_frame, text="Sebelumnya", command=self.go_previous)
        self.prev_button.grid(row=0, column=0, padx=5, pady=10, sticky="e")

        self.next_button = customtkinter.CTkButton(self.navigation_frame, text="Selanjutnya", command=self.go_next_manual)
        self.next_button.grid(row=0, column=1, padx=5, pady=10, sticky="w")

    def display_current_question(self):
        """Menampilkan pertanyaan saat ini dan mengelola status tombol."""
        for widget in self.question_display_frame.winfo_children():
            widget.destroy()

        if self.quiz_logic.current_question_index < self.quiz_logic.total_questions:
            current_q_data = self.quiz_logic.get_current_question()
            question_id = current_q_data['id']

            question_label = customtkinter.CTkLabel(self.question_display_frame, 
                                                    text=f"{self.quiz_logic.current_question_index + 1}. {current_q_data['pertanyaan']}", 
                                                    wraplength=650, 
                                                    font=customtkinter.CTkFont(size=18, weight="bold"),
                                                    justify="center") 
            question_label.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew") 

            default_button_color = customtkinter.ThemeManager.theme["CTkButton"]["fg_color"]
            selected_button_color = customtkinter.ThemeManager.theme["CTkButton"]["hover_color"]

            setuju_btn = customtkinter.CTkButton(
                self.question_display_frame, 
                text="Ya, ini cocok dengan saya!", # Teks tombol lebih friendly
                font=customtkinter.CTkFont(size=16),
                command=lambda q_id=question_id: self.on_answer_button_click(q_id, "setuju")
            )
            setuju_btn.grid(row=1, column=0, padx=10, pady=5) 

            tidak_setuju_btn = customtkinter.CTkButton(
                self.question_display_frame, 
                text="Tidak, ini bukan saya.", # Teks tombol lebih friendly
                font=customtkinter.CTkFont(size=16),
                command=lambda q_id=question_id: self.on_answer_button_click(q_id, "tidak_setuju")
            )
            tidak_setuju_btn.grid(row=2, column=0, padx=10, pady=5) 

            self.current_answer_buttons = {
                "setuju": setuju_btn,
                "tidak_setuju": tidak_setuju_btn
            }

            current_selection = self.quiz_logic.answer_vars[question_id].get()
            if current_selection != "None":
                if current_selection == "setuju":
                    setuju_btn.configure(fg_color=selected_button_color)
                else:
                    tidak_setuju_btn.configure(fg_color=selected_button_color)

            self.prev_button.configure(state="normal" if self.quiz_logic.current_question_index > 0 else "disabled")
            
            if self.quiz_logic.current_question_index == self.quiz_logic.total_questions - 1:
                self.next_button.configure(text="Lihat Hasil Tes", command=self.show_results)
            else:
                self.next_button.configure(text="Selanjutnya", command=self.go_next_manual)
        else:
            self.show_results()

    def on_answer_button_click(self, question_id, answer_value):
        """Memproses klik tombol jawaban, menandai pilihan, dan otomatis melanjutkan."""
        default_button_color = customtkinter.ThemeManager.theme["CTkButton"]["fg_color"]
        selected_button_color = customtkinter.ThemeManager.theme["CTkButton"]["hover_color"]
        
        for btn_value, button_widget in self.current_answer_buttons.items():
            if btn_value == answer_value:
                button_widget.configure(fg_color=selected_button_color)
            else:
                button_widget.configure(fg_color=default_button_color)

        self.quiz_logic.record_answer(question_id, answer_value) 
        self.auto_advance_on_select()

    def auto_advance_on_select(self):
        """Otomatis melanjutkan ke pertanyaan berikutnya setelah jawaban dipilih."""
        if self.quiz_logic.current_question_index < self.quiz_logic.total_questions - 1:
            self.quiz_logic.current_question_index += 1
            self.display_current_question()
        elif self.quiz_logic.current_question_index == self.quiz_logic.total_questions - 1:
            self.show_results()

    def go_next_manual(self):
        """Digunakan jika pengguna secara manual mengklik tombol 'Selanjutnya'/'Lihat Hasil Tes'."""
        current_q_id = self.quiz_logic.get_current_question()['id']
        if self.quiz_logic.answer_vars[current_q_id].get() == "None":
            tkinter.messagebox.showwarning("Peringatan", "Mohon pilih jawaban untuk pertanyaan ini sebelum melanjutkan.")
            return

        if self.quiz_logic.current_question_index < self.quiz_logic.total_questions - 1:
            self.quiz_logic.current_question_index += 1
            self.display_current_question()
        else:
            self.show_results()

    def go_previous(self):
        """Kembali ke pertanyaan sebelumnya."""
        if self.quiz_logic.current_question_index > 0:
            self.quiz_logic.current_question_index -= 1
            self.display_current_question()
        else:
            self.prev_button.configure(state="disabled")

    def show_results(self):
        """Memproses jawaban dan menampilkan jendela hasil."""
        skor_lengkap = self.quiz_logic.calculate_scores() 
        
        if not self.quiz_logic.all_questions_answered(): 
            tkinter.messagebox.showwarning("Peringatan", "Mohon jawab semua pertanyaan sebelum melihat hasil.")
            self.quiz_logic.current_question_index = self.quiz_logic.total_questions - 1 
            self.display_current_question() 
            return

        kategori_tertinggi, deskripsi_utama, rekomendasi_list_utama = self.quiz_logic.get_final_results(skor_lengkap)

        chart_bytes_io = self.quiz_logic.create_riasec_chart(skor_lengkap)
        chart_bytes_for_pdf = chart_bytes_io 
        
        chart_bytes_io.seek(0) 
        chart_data_base64 = base64.b64encode(chart_bytes_io.read()).decode('utf-8') 

        self.after(10, lambda: self.open_results_window(kategori_tertinggi, deskripsi_utama, rekomendasi_list_utama, skor_lengkap, chart_data_base64, chart_bytes_for_pdf))

    def open_results_window(self, kategori_tertinggi, deskripsi, rekomendasi_list, skor_lengkap, chart_data_base64, chart_bytes_for_pdf):
        """Membuka jendela baru untuk menampilkan hasil tes, data pengguna, dan grafik."""
        self.results_window = customtkinter.CTkToplevel(self)
        self.results_window.title("Hasil Tes Karir Anda")
        self.results_window.geometry("700x850")
        self.results_window.grab_set()
        self.results_window.resizable(False, False)

        self.results_window.grid_columnconfigure(0, weight=1)
        self.results_window.grid_rowconfigure((0, 1), weight=1)

        results_scroll_frame = customtkinter.CTkScrollableFrame(self.results_window)
        results_scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        results_scroll_frame.grid_columnconfigure(0, weight=1)

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
            score_item_frame.grid(row=6+len(rekomendasi_list)+2+(i*2), column=0, padx=10, pady=5, sticky="ew") 
            score_item_frame.grid_columnconfigure(0, weight=1)

            score_text = f"[{kategori}] {self.quiz_logic.riasec_descriptions[kategori].split(':')[0]} : {nilai} Poin" 
            customtkinter.CTkLabel(score_item_frame, 
                                 text=score_text,
                                 font=customtkinter.CTkFont(size=14, weight="bold"),
                                 wraplength=550, justify="left").grid(row=0, column=0, padx=10, pady=2, sticky="w")
            
            full_desc_text = self.quiz_logic.riasec_descriptions[kategori] 
            customtkinter.CTkLabel(score_item_frame,
                                 text=full_desc_text,
                                 font=customtkinter.CTkFont(size=12),
                                 wraplength=550, justify="left").grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")
        
        if chart_data_base64:
            img_data = base64.b64decode(chart_data_base64)
            chart_image = customtkinter.CTkImage(light_image=Image.open(io.BytesIO(img_data)), 
                                                 dark_image=Image.open(io.BytesIO(img_data)), 
                                                 size=(550, 350))

            chart_label = customtkinter.CTkLabel(results_scroll_frame, text="", image=chart_image)
            chart_label.grid(row=6+len(rekomendasi_list)+2+(len(skor_lengkap)*2), column=0, pady=20) 

        button_frame = customtkinter.CTkFrame(self.results_window, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        download_button = customtkinter.CTkButton(button_frame, 
                                                 text="Unduh Hasil (PDF)", 
                                                 command=lambda: self.report_generator.download_results(
                                                     self.user_data, kategori_tertinggi, deskripsi, 
                                                     rekomendasi_list, skor_lengkap, chart_bytes_for_pdf, 
                                                     self.quiz_logic.riasec_descriptions 
                                                 ))
        download_button.grid(row=0, column=0, padx=5, pady=10, sticky="e")

        restart_button = customtkinter.CTkButton(button_frame, text="Ulangi Tes", command=self.reset_and_start_over)
        restart_button.grid(row=0, column=1, padx=5, pady=10, sticky="w")

    def reset_and_start_over(self):
        """Meriset aplikasi dan kembali ke layar awal."""
        self.quiz_logic.reset_quiz() 
        self.user_data = {
            "nama": "",
            "alamat": "",
            "usia": "",
            "nomor_hp": ""
        }
        if hasattr(self, 'results_window') and self.results_window.winfo_exists():
            self.results_window.destroy()
        
        self.create_start_screen()


if __name__ == '__main__':
    app = CareerGuidanceApp()
    app.mainloop()
