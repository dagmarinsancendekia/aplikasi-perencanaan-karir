from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
import tkinter.messagebox
from tkinter import filedialog 
import tempfile
import os

class ReportGenerator:
    def __init__(self):
        pass 

    def add_pdf_page_layout(self, canvas_obj, user_name, page_num):
        """Menambahkan header dan footer ke setiap halaman PDF."""
        canvas_obj.saveState()
        styles = getSampleStyleSheet()

        # Header
        header_text = f"Laporan Hasil Tes Karir - {user_name}"
        # Ukuran font header disesuaikan
        P_header = Paragraph(header_text, ParagraphStyle(
            'HeaderStyle',
            parent=styles['h3'],
            fontSize=13, # Sedikit lebih kecil agar tidak terlalu menonjol dari judul utama
            alignment=TA_LEFT,
            fontName='Helvetica-Bold' # Pastikan font yang jelas
        ))
        P_header.wrapOn(canvas_obj, letter[0] - 2*inch, letter[1])
        P_header.drawOn(canvas_obj, inch, letter[1] - 0.75*inch)
        
        # Garis pembatas header
        canvas_obj.setStrokeColorRGB(0.7, 0.7, 0.7) # Warna abu-abu
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(inch, letter[1] - 1.0*inch, letter[0] - inch, letter[1] - 1.0*inch)

        # Footer
        footer_text = f"Halaman {page_num}"
        # Ukuran font footer disesuaikan
        P_footer = Paragraph(footer_text, ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=10, # Ukuran standar untuk footer
            alignment=TA_CENTER
        ))
        P_footer.wrapOn(canvas_obj, letter[0] - 2*inch, letter[1])
        P_footer.drawOn(canvas_obj, (letter[0] - P_footer.width) / 2, 0.5 * inch)
        
        canvas_obj.restoreState()

    def download_results(self, user_data, kategori_tertinggi, deskripsi_utama, rekomendasi_list_utama, skor_lengkap, chart_bytes_for_pdf, riasec_descriptions):
        """Menyimpan hasil tes dan data pengguna ke file PDF, termasuk grafik dari file sementara."""
        temp_chart_filepath = None 

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf", 
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"Hasil_Tes_Karir_{user_data['nama'].replace(' ', '_')}.pdf"
            )

            if not file_path:
                tkinter.messagebox.showinfo("Info", "Pengunduhan dibatalkan.")
                return

            c = canvas.Canvas(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Mendefinisikan warna pastel
            pastel_blue = colors.Color(red=(204/255), green=(229/255), blue=(255/255)) 
            light_grey = colors.Color(red=(240/255), green=(240/255), blue=(240/255)) 
            
            # Gaya untuk PDF - Semua gaya didefinisikan di awal fungsi ini
            style_title = ParagraphStyle(
                'Title',
                parent=styles['h1'],
                fontSize=26, # Ukuran sedikit diperbesar untuk judul utama
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica-Bold' # Tambahkan font bold untuk judul
            )
            style_heading = ParagraphStyle(
                'Heading',
                parent=styles['h2'],
                fontSize=17, # Ukuran sedikit diperbesar untuk heading bagian
                alignment=TA_LEFT,
                spaceAfter=10,
                spaceBefore=15,
                fontName='Helvetica-Bold'
            )
            style_normal = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=11, # Ukuran standar teks normal
                alignment=TA_LEFT,
                spaceAfter=5
            )
            style_bold = ParagraphStyle(
                'Bold',
                parent=styles['Normal'],
                fontSize=11, # Konsisten dengan normal, hanya bold
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                spaceAfter=5
            )
            style_list = ParagraphStyle(
                'List',
                parent=styles['Normal'],
                fontSize=11, # Konsisten dengan normal
                alignment=TA_LEFT,
                leftIndent=20,
                spaceAfter=2
            )
            style_table_header = ParagraphStyle(
                'TableHeader',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                textColor=colors.white 
            )
            style_table_cell_bold = ParagraphStyle(
                'TableCellBold',
                parent=styles['Normal'],
                fontSize=10, # Tetap 10 untuk cell bold utama
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
            )
            style_table_cell_normal = ParagraphStyle( # Tidak digunakan secara langsung, tapi diselaraskan
                'TableCellNormal',
                parent=styles['Normal'],
                fontSize=9, 
                alignment=TA_LEFT,
            )
            style_score_heading = ParagraphStyle(
                'ScoreHeading',
                parent=styles['h3'],
                fontSize=15, # Ukuran sedikit diperbesar untuk sub-heading
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                spaceAfter=5
            )
            style_score_detail = ParagraphStyle( # Tidak digunakan secara langsung, tapi diselaraskan
                'ScoreDetail',
                parent=styles['Normal'],
                fontSize=9, 
                alignment=TA_LEFT,
                leftIndent=10,
                spaceAfter=2
            )
            style_riasec_desc = ParagraphStyle(
                'RIASECDir',
                parent=styles['Normal'],
                fontSize=10, # Ukuran teks deskripsi RIASEC
                alignment=TA_LEFT,
                leftIndent=20, 
                spaceAfter=10
            )

            y_pos = letter[1] - 1.5*inch 
            x_left = inch 
            page_num = 1

            self.add_pdf_page_layout(c, user_data['nama'], page_num) 

            # Konten PDF dimulai di sini
            P = Paragraph("Hasil Tes Perencanaan Karir", style_title)
            P.wrapOn(c, letter[0] - 2*inch, letter[1]) 
            P.drawOn(c, inch, y_pos - P.height)
            y_pos -= P.height + 0.2*inch 

            P = Paragraph("--- Data Pengguna ---", style_heading)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            if y_pos < P.height + inch: c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch 
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.1*inch

            user_data_lines = [
                f"<b>Nama:</b> {user_data['nama']}",
                f"<b>Alamat:</b> {user_data['alamat']}",
                f"<b>Usia:</b> {user_data['usia']} tahun",
                f"<b>Nomor HP:</b> {user_data['nomor_hp']}"
            ]
            for line in user_data_lines:
                P = Paragraph(line, style_normal)
                P.wrapOn(c, letter[0] - 2*inch, letter[1])
                if y_pos < P.height + inch: 
                    c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch
                P.drawOn(c, x_left, y_pos - P.height)
                y_pos -= P.height + 0.05*inch
            y_pos -= 0.2*inch 

            P = Paragraph("--- Hasil Tes ---", style_heading)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            if y_pos < P.height + inch: 
                c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.1*inch
            
            P = Paragraph(f"<b>Kategori minat tertinggi Anda adalah: {kategori_tertinggi}</b>", style_bold)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            if y_pos < P.height + inch: 
                c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.1*inch

            P = Paragraph("Deskripsi Tipe Minat Anda:", style_score_heading)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            if y_pos < P.height + inch: 
                c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.05*inch
            P = Paragraph(deskripsi_utama, style_normal)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            if y_pos < P.height + inch: 
                c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.2*inch

            P = Paragraph("Rekomendasi Karir untuk Anda:", style_score_heading)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            if y_pos < P.height + inch: 
                c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.05*inch
            for karir in rekomendasi_list_utama:
                P = Paragraph(f"- {karir}", style_list)
                P.wrapOn(c, letter[0] - 2*inch, letter[1])
                if y_pos < P.height + inch: 
                    c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch
                P.drawOn(c, x_left, y_pos - P.height)
                y_pos -= P.height + 0.02*inch
            y_pos -= 0.2*inch

            P = Paragraph("--- Skor Minat Anda untuk Setiap Tipe Holland (RIASEC) ---", style_heading)
            P.wrapOn(c, letter[0] - 2*inch, letter[1])
            if y_pos < P.height + inch: 
                c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch
            P.drawOn(c, x_left, y_pos - P.height)
            y_pos -= P.height + 0.1*inch

            # --- Tabel Skor RIASEC ---
            table_data = []
            # Header Tabel
            table_data.append([
                Paragraph("Tipe", style_table_header), 
                Paragraph("Nama & Deskripsi Lengkap", style_table_header), 
                Paragraph("Skor", style_table_header)
            ])

            # Sort skor_lengkap agar output tabel konsisten (misalnya, berdasarkan abjad kategori)
            sorted_skor_lengkap = sorted(skor_lengkap.items())

            for i, (kategori, nilai) in enumerate(sorted_skor_lengkap):
                # Gunakan deskripsi lengkap dari riasec_descriptions yang diteruskan
                full_desc_riasec = riasec_descriptions.get(kategori, 'Deskripsi tidak tersedia.')
                short_name = full_desc_riasec.split(':')[0].strip() 
                
                table_data.append([
                    Paragraph(f"<b>{kategori}</b>", style_table_cell_bold),
                    Paragraph(f"<b>{short_name}</b><br/><font size='9'>{full_desc_riasec}</font>", style_table_cell_bold), # Menggunakan font size 9
                    Paragraph(str(nilai), style_table_cell_bold)
                ])
            
            col_widths = [0.8*inch, 4.2*inch, 0.8*inch] 

            table = Table(table_data, colWidths=col_widths)
            
            # Membangun TableStyle secara dinamis untuk latar belakang bergantian
            table_styles = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4A90E2')), # Header biru
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BOX', (0,0), (-1,-1), 1, colors.black),
            ]
            # Tambahkan gaya latar belakang bergantian untuk setiap baris data yang ada
            for i in range(1, len(table_data)): 
                bg_color = light_grey if (i - 1) % 2 == 0 else colors.white 
                table_styles.append(('BACKGROUND', (0,i), (-1,i), bg_color))

            table.setStyle(TableStyle(table_styles))

            table_width, table_height = table.wrapOn(c, letter[0] - 2*inch, letter[1])
            
            if y_pos < table_height + inch: 
                c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch 

            table.drawOn(c, x_left, y_pos - table_height)
            y_pos -= table_height + 0.2*inch
            # --- End Tabel Skor RIASEC ---

            # --- Tambahkan Grafik ke PDF ---
            if chart_bytes_for_pdf:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    tmp_file.write(chart_bytes_for_pdf.getvalue())
                    temp_chart_filepath = tmp_file.name

                chart_height_estimate = 4 * inch 
                chart_width_estimate = 6 * inch 
                
                if y_pos < chart_height_estimate + inch: 
                    c.showPage(); page_num += 1; self.add_pdf_page_layout(c, user_data['nama'], page_num); y_pos = letter[1] - 1.5*inch

                c.drawImage(temp_chart_filepath, 
                            (letter[0] - chart_width_estimate) / 2, 
                            y_pos - chart_height_estimate - 0.2*inch, 
                            width=chart_width_estimate, 
                            height=chart_height_estimate)
                y_pos -= chart_height_estimate + 0.5*inch 
            # --- End Tambah Grafik ke PDF ---
                    
            c.save()
            tkinter.messagebox.showinfo("Berhasil", f"Hasil tes berhasil diunduh ke:\n{file_path}")

        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Terjadi kesalahan saat mengunduh hasil: {e}")
        finally:
            if temp_chart_filepath and os.path.exists(temp_chart_filepath):
                os.remove(temp_chart_filepath)

