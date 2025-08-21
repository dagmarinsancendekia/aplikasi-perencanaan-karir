import csv
import os
import tkinter.messagebox

class UserDataManager:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def save_user_data(self, user_data):
        """Menyimpan data pengguna ke file CSV."""
        file_exists = os.path.isfile(self.csv_file_path)
        
        try:
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(list(user_data.keys()))
                writer.writerow(list(user_data.values()))
        except Exception as e:
            tkinter.messagebox.showerror("Error Simpan Data", f"Gagal menyimpan data pengguna: {e}")
