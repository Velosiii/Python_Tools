import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import pymupdf as fitz
import os

class PDFAraciApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YoRHa PDF Birleştirici ve Ayırıcı")
        self.root.geometry("900x650")
        
        # --- NieR Renk Paleti ---
        self.bg_color = "#1c1c1c"       # Koyu arka plan
        self.fg_color = "#d1cdb7"       # NieR soluk bej yazı rengi
        self.btn_bg = "#2a2a2a"         # Buton arka planı
        self.btn_active_bg = "#d1cdb7"  # Butona tıklanınca (Bej)
        self.btn_active_fg = "#111111"  # Butona tıklanınca yazı rengi (Siyah)
        
        self.root.configure(bg=self.bg_color)
        
        self.pdf_listesi = []
        
        self.secili_pdf_yolu = None
        self.secili_indeksler = []
        self.gecerli_onizleme_sirasi = 0
        
        self.tema_ayarla()
        self.arayuz_olustur()
        self.dantel_ekle() # 2B Dantel motifini ekleyen fonksiyon

    def tema_ayarla(self):
        """Treeview (Liste) ve genel ttk bileşenleri için karanlık tema ayarları"""
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview", 
                        background=self.btn_bg, 
                        foreground=self.fg_color, 
                        fieldbackground=self.btn_bg, 
                        bordercolor=self.bg_color,
                        font=("Segoe UI", 9))
        
        style.configure("Treeview.Heading", 
                        background="#111111", 
                        foreground=self.fg_color, 
                        relief="flat",
                        font=("Segoe UI", 9, "bold"))
        
        style.map("Treeview", background=[('selected', '#4a473e')]) # Seçili öğe rengi

    def arayuz_olustur(self):
        # Ana çerçeve
        ana_panel = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.bg_color, bd=0, sashwidth=2)
        ana_panel.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        ### SOL PANEL ###
        sol_frame = tk.Frame(ana_panel, bg=self.bg_color)
        ana_panel.add(sol_frame, minsize=420)

        # Butonlar
        buton_frame = tk.Frame(sol_frame, bg=self.bg_color)
        buton_frame.pack(fill=tk.X, pady=(0, 10))

        self.ozel_buton(buton_frame, "PDF Ekle", self.pdf_ekle).pack(side=tk.LEFT, padx=(0, 5))
        self.ozel_buton(buton_frame, "Listeden Çıkar", self.pdf_cikar).pack(side=tk.LEFT)

        # Liste
        sutunlar = ("dosya_adi", "sayfa_araligi")
        self.tree = ttk.Treeview(sol_frame, columns=sutunlar, show="headings", selectmode="browse")
        self.tree.heading("dosya_adi", text="Birim Adı (Dosya)")
        self.tree.heading("sayfa_araligi", text="Hedef Veri (Sayfalar)")
        self.tree.column("dosya_adi", width=250)
        self.tree.column("sayfa_araligi", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_pdf_secildi)

        # İşlem Paneli
        islem_frame = tk.LabelFrame(sol_frame, text=" İşlem Komutları ", bg=self.bg_color, fg=self.fg_color, font=("Segoe UI", 10), bd=1)
        islem_frame.pack(fill=tk.X, pady=10)

        self.ozel_buton(islem_frame, "Tüm Listeyi Birleştir", self.pdf_birlestir).pack(fill=tk.X, pady=3, padx=5)
        self.ozel_buton(islem_frame, "Seçili PDF'i Ayrı Kaydet", self.pdf_ayri_kaydet).pack(fill=tk.X, pady=3, padx=5)
        self.ozel_buton(islem_frame, "Seçili PDF'i Tek Tek Böl", self.pdf_tek_tek_bol).pack(fill=tk.X, pady=3, padx=5)

        ### SAĞ PANEL (Önizleme) ###
        sag_frame = tk.Frame(ana_panel, bg=self.bg_color, bd=1, relief=tk.SOLID)
        ana_panel.add(sag_frame, minsize=400)

        tk.Label(sag_frame, text="Görsel Veri (Önizleme)", bg=self.bg_color, fg=self.fg_color, font=("Segoe UI", 10, "bold")).pack(pady=5)

        self.onizleme_label = tk.Label(sag_frame, text="Hedef seçilmedi.", bg="#111111", fg=self.fg_color)
        self.onizleme_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        nav_frame = tk.Frame(sag_frame, bg=self.bg_color)
        nav_frame.pack(pady=10)

        self.btn_onceki = self.ozel_buton(nav_frame, "< Geri", lambda: self.sayfa_degistir(-1))
        self.btn_onceki.pack(side=tk.LEFT, padx=5)
        self.btn_onceki.config(state=tk.DISABLED)

        self.lbl_sayfa_bilgi = tk.Label(nav_frame, text="- / -", bg=self.bg_color, fg=self.fg_color)
        self.lbl_sayfa_bilgi.pack(side=tk.LEFT, padx=10)

        self.btn_sonraki = self.ozel_buton(nav_frame, "İleri >", lambda: self.sayfa_degistir(1))
        self.btn_sonraki.pack(side=tk.LEFT, padx=5)
        self.btn_sonraki.config(state=tk.DISABLED)

    def ozel_buton(self, parent, metin, komut):
        """NieR temasına uygun buton üreten yardımcı fonksiyon"""
        btn = tk.Button(parent, text=metin, command=komut, 
                        bg=self.btn_bg, fg=self.fg_color, 
                        activebackground=self.btn_active_bg, activeforeground=self.btn_active_fg,
                        font=("Segoe UI", 9), relief=tk.FLAT, bd=1, cursor="hand2")
        return btn

    def dantel_ekle(self):
        """2B'nin dantel motifini pencerenin altına yerleştirir."""
        try:
            # UYARI: Bu kodun çalışması için script ile aynı klasörde "2b_dantel.png" adında 
            # transparan bir dantel görseli olmalıdır. Yoksa sessizce hata verir ve desensiz çalışır.
            dantel_yolu = os.path.join(os.path.dirname(__file__), "2b_dantel.png")
            if os.path.exists(dantel_yolu):
                self.dantel_img = Image.open(dantel_yolu)
                # Genişliği pencereye uydur, yüksekliği 40 piksel yap
                self.dantel_img = self.dantel_img.resize((900, 40), Image.Resampling.LANCZOS)
                self.dantel_tk = ImageTk.PhotoImage(self.dantel_img)
                
                # Süsleme etiketini pencerenin en altına yerleştir
                self.dantel_label = tk.Label(self.root, image=self.dantel_tk, bg=self.bg_color, bd=0)
                self.dantel_label.pack(side=tk.BOTTOM, fill=tk.X)
        except Exception as e:
            print("Dantel yüklenemedi:", e)

    # --- ESKİ MANTIK VE İŞLEM FONKSİYONLARI (Renk kodları uyarlanarak korundu) ---
    def aralik_cozumle(self, aralik_str, max_sayfa):
        if not aralik_str.strip():
            return list(range(max_sayfa))
        indeksler = []
        parcalar = aralik_str.replace(" ", "").split(",")
        for parca in parcalar:
            if "-" in parca:
                bas, bit = parca.split("-")
                bas = max(1, int(bas))
                bit = min(max_sayfa, int(bit))
                indeksler.extend(range(bas - 1, bit))
            else:
                if parca.isdigit():
                    deger = int(parca)
                    if 1 <= deger <= max_sayfa:
                        indeksler.append(deger - 1)
        return sorted(list(set(indeksler)))

    def pdf_ekle(self):
        dosya_yolu = filedialog.askopenfilename(filetypes=[("PDF Dosyaları", "*.pdf")])
        if not dosya_yolu: return

        try:
            pdf_doc = fitz.open(dosya_yolu)
            max_sayfa = pdf_doc.page_count
            pdf_doc.close()
        except Exception:
            messagebox.showerror("Sistem Hatası", "Veri dosyası okunamadı.")
            return

        aralik = simpledialog.askstring("Veri Aralığı", 
                                        f"Bu veri {max_sayfa} sayfa.\nAlınacak hedefleri girin (Örn: 1-5, 8):\nTümü için boş bırakın:")
        if aralik is None: return
            
        dosya_adi = os.path.basename(dosya_yolu)
        gosterim_aralik = aralik if aralik.strip() else "Tümü"
        indeksler = self.aralik_cozumle(aralik, max_sayfa)

        item_id = self.tree.insert("", tk.END, values=(dosya_adi, gosterim_aralik))
        self.pdf_listesi.append({"id": item_id, "yol": dosya_yolu, "indeksler": indeksler, "dosya_adi": dosya_adi})

    def pdf_cikar(self):
        secili = self.tree.selection()
        if not secili: return
        item_id = secili[0]
        self.tree.delete(item_id)
        self.pdf_listesi = [p for p in self.pdf_listesi if p["id"] != item_id]
        
        self.onizleme_label.config(image='', text="Hedef seçilmedi.", bg="#111111")
        self.lbl_sayfa_bilgi.config(text="- / -")
        self.btn_onceki.config(state=tk.DISABLED)
        self.btn_sonraki.config(state=tk.DISABLED)

    def on_pdf_secildi(self, event):
        secili = self.tree.selection()
        if not secili: return
        item_id = secili[0]
        secili_veri = next((p for p in self.pdf_listesi if p["id"] == item_id), None)
        
        if secili_veri and secili_veri["indeksler"]:
            self.secili_pdf_yolu = secili_veri["yol"]
            self.secili_indeksler = secili_veri["indeksler"]
            self.gecerli_onizleme_sirasi = 0
            self.onizlemeyi_guncelle()

    def sayfa_degistir(self, yon):
        yeni_sira = self.gecerli_onizleme_sirasi + yon
        if 0 <= yeni_sira < len(self.secili_indeksler):
            self.gecerli_onizleme_sirasi = yeni_sira
            self.onizlemeyi_guncelle()

    def onizlemeyi_guncelle(self):
        if not self.secili_pdf_yolu: return
        toplam_secili = len(self.secili_indeksler)
        gercek_sayfa_indeksi = self.secili_indeksler[self.gecerli_onizleme_sirasi]

        try:
            doc = fitz.open(self.secili_pdf_yolu)
            sayfa = doc.load_page(gercek_sayfa_indeksi)
            mat = fitz.Matrix(1.5, 1.5)
            pix = sayfa.get_pixmap(matrix=mat)
            doc.close()

            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.thumbnail((380, 480), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)

            self.onizleme_label.config(image=tk_img, text="", bg=self.bg_color)
            self.onizleme_label.image = tk_img

            self.lbl_sayfa_bilgi.config(text=f"{self.gecerli_onizleme_sirasi + 1} / {toplam_secili}\n(Orijinal: {gercek_sayfa_indeksi + 1})")
            
            self.btn_onceki.config(state=tk.NORMAL if self.gecerli_onizleme_sirasi > 0 else tk.DISABLED)
            self.btn_sonraki.config(state=tk.NORMAL if self.gecerli_onizleme_sirasi < toplam_secili - 1 else tk.DISABLED)
        except Exception as e:
            print("Önizleme hatası:", e)

    def pdf_birlestir(self):
        if not self.pdf_listesi: return
        kayit_yolu = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dosyaları", "*.pdf")], title="Birimleri Kaydet")
        if not kayit_yolu: return
        try:
            sonuc_pdf = fitz.open()
            for item in self.pdf_listesi:
                src_pdf = fitz.open(item["yol"])
                src_pdf.select(item["indeksler"])
                sonuc_pdf.insert_pdf(src_pdf)
                src_pdf.close()
            sonuc_pdf.save(kayit_yolu)
            sonuc_pdf.close()
            messagebox.showinfo("Durum", "Aktarım tamamlandı.")
        except Exception as e:
            messagebox.showerror("Kritik Hata", f"İşlem başarısız:\n{str(e)}")

    def pdf_ayri_kaydet(self):
        secili = self.tree.selection()
        if not secili: return
        item_id = secili[0]
        secili_veri = next((p for p in self.pdf_listesi if p["id"] == item_id), None)

        kayit_yolu = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"ayrilmis_{secili_veri['dosya_adi']}", filetypes=[("PDF Dosyaları", "*.pdf")])
        if not kayit_yolu: return
        try:
            src_pdf = fitz.open(secili_veri["yol"])
            src_pdf.select(secili_veri["indeksler"])
            src_pdf.save(kayit_yolu)
            src_pdf.close()
            messagebox.showinfo("Durum", "Ayırma işlemi tamamlandı.")
        except Exception as e:
            messagebox.showerror("Kritik Hata", f"İşlem başarısız:\n{str(e)}")

    def pdf_tek_tek_bol(self):
        secili = self.tree.selection()
        if not secili: return
        item_id = secili[0]
        secili_veri = next((p for p in self.pdf_listesi if p["id"] == item_id), None)
        klasor_yolu = filedialog.askdirectory(title="Veri Klasörünü Seçin")
        if not klasor_yolu: return
        try:
            doc = fitz.open(secili_veri["yol"])
            for idx in secili_veri["indeksler"]:
                yeni_pdf = fitz.open()
                yeni_pdf.insert_pdf(doc, from_page=idx, to_page=idx)
                yeni_pdf.save(os.path.join(klasor_yolu, f"sayfa_{idx + 1}.pdf"))
                yeni_pdf.close()
            doc.close()
            messagebox.showinfo("Durum", "Veriler tek tek parçalandı.")
        except Exception as e:
            messagebox.showerror("Kritik Hata", f"İşlem başarısız:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFAraciApp(root)
    root.mainloop()
