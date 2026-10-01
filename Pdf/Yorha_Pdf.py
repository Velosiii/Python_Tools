import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import pymupdf as fitz
import os
import ctypes

class PDFAraciApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YoRHa Sistem Veri Yöneticisi")
        
        # --- DPI ÖLÇEKLEME FAKTÖRÜ HESAPLAMA ---
        try:
            self.sf = self.root.winfo_fpixels('1i') / 96.0
        except:
            self.sf = 1.0
            
        # --- BOYUT GÜNCELLEMESİ (Her şeyin tam görünmesi için büyütüldü) ---
        pencere_g = int(950 * self.sf)
        pencere_y = int(780 * self.sf) # 650'den 780'e çıkarıldı ki dantel sığsın
        self.root.geometry(f"{pencere_g}x{pencere_y}")
        
        # --- NieR Orijinal UI Renk Paleti ---
        self.bg_color = "#d3cebb"       
        self.fg_color = "#3d3a31"       
        self.btn_bg = "#b3ae9d"         
        self.btn_active_bg = "#3d3a31"  
        self.btn_active_fg = "#d3cebb"  
        
        self.root.configure(bg=self.bg_color)
        
        self.pdf_listesi = []
        self.secili_pdf_yolu = None
        self.secili_indeksler = []
        self.gecerli_onizleme_sirasi = 0
        self.varsayilan_img_tk = None
        
        self.pencere_baslik_ayarla() 
        self.varsayilan_gorsel_yukle()
        self.tema_ayarla()
        self.arayuz_olustur()
        self.dantel_ekle()

    def varsayilan_gorsel_yukle(self):
        try:
            gorsel_yolu = os.path.join(os.path.dirname(__file__), "no_data.jpg")
            if os.path.exists(gorsel_yolu):
                img = Image.open(gorsel_yolu)
                img.thumbnail((int(380 * self.sf), int(480 * self.sf)), Image.Resampling.LANCZOS)
                self.varsayilan_img_tk = ImageTk.PhotoImage(img)
        except Exception as e:
            pass

    def pencere_baslik_ayarla(self):
        try:
            logo_yolu = os.path.join(os.path.dirname(__file__), "yorha.png")
            if os.path.exists(logo_yolu):
                icon_img = ImageTk.PhotoImage(Image.open(logo_yolu))
                self.root.iconphoto(False, icon_img)
        except:
            pass

        try:
            # --- ZORLANMA ÇÖZÜMÜ BURADA ---
            # update() yerine update_idletasks() kullandık. Donmayı engeller.
            self.root.update_idletasks() 
            hex_color = self.bg_color
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            color = ctypes.c_int(r | (g << 8) | (b << 16))
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            DWMWA_CAPTION_COLOR = 35 
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(color), ctypes.sizeof(color))
        except:
            pass

    def tema_ayarla(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview", 
                        background=self.btn_bg, 
                        foreground=self.fg_color, 
                        fieldbackground=self.bg_color, 
                        bordercolor=self.bg_color,
                        font=("Helvetica", 10),
                        rowheight=int(25 * self.sf))
        
        style.configure("Treeview.Heading", 
                        background=self.bg_color, 
                        foreground=self.fg_color, 
                        relief="flat",
                        font=("Helvetica", 10, "bold"))
        
        style.map("Treeview", 
                  background=[('selected', self.fg_color)],
                  foreground=[('selected', self.bg_color)])

    def arayuz_olustur(self):
        ana_panel = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.bg_color, bd=0, sashwidth=int(2 * self.sf))
        ana_panel.pack(fill=tk.BOTH, expand=True, padx=int(15 * self.sf), pady=int(15 * self.sf))

        ### SOL PANEL ###
        sol_frame = tk.Frame(ana_panel, bg=self.bg_color)
        ana_panel.add(sol_frame, minsize=int(420 * self.sf))

        baslik = tk.Label(sol_frame, text="SYSTEM DATA", font=("Helvetica", 18), bg=self.bg_color, fg=self.fg_color, anchor="w")
        baslik.pack(fill=tk.X, pady=(0, int(10 * self.sf)))

        buton_frame = tk.Frame(sol_frame, bg=self.bg_color)
        buton_frame.pack(fill=tk.X, pady=(0, int(10 * self.sf)))

        self.ozel_buton(buton_frame, "PDF Ekle", self.pdf_ekle).pack(side=tk.LEFT, padx=(0, int(5 * self.sf)))
        self.ozel_buton(buton_frame, "Listeden Çıkar", self.pdf_cikar).pack(side=tk.LEFT)

        sutunlar = ("dosya_adi", "sayfa_araligi")
        self.tree = ttk.Treeview(sol_frame, columns=sutunlar, show="headings", selectmode="browse")
        self.tree.heading("dosya_adi", text="Birim Adı (Dosya)")
        self.tree.heading("sayfa_araligi", text="Hedef Veri (Sayfalar)")
        
        self.tree.column("dosya_adi", width=int(250 * self.sf))
        self.tree.column("sayfa_araligi", width=int(150 * self.sf))
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_pdf_secildi)

        islem_frame = tk.LabelFrame(sol_frame, text=" İşlem Komutları ", bg=self.bg_color, fg=self.fg_color, font=("Helvetica", 10), bd=1)
        islem_frame.pack(fill=tk.X, pady=int(10 * self.sf))

        self.ozel_buton(islem_frame, "Tüm Listeyi Birleştir", self.pdf_birlestir).pack(fill=tk.X, pady=int(3 * self.sf), padx=int(5 * self.sf))
        self.ozel_buton(islem_frame, "Seçili PDF'i Ayrı Kaydet", self.pdf_ayri_kaydet).pack(fill=tk.X, pady=int(3 * self.sf), padx=int(5 * self.sf))
        self.ozel_buton(islem_frame, "Seçili PDF'i Tek Tek Böl", self.pdf_tek_tek_bol).pack(fill=tk.X, pady=int(3 * self.sf), padx=int(5 * self.sf))

        ### SAĞ PANEL ###
        sag_frame = tk.Frame(ana_panel, bg=self.bg_color, bd=1, relief=tk.SOLID)
        ana_panel.add(sag_frame, minsize=int(400 * self.sf))

        tk.Label(sag_frame, text="Görsel Veri (Önizleme)", bg=self.bg_color, fg=self.fg_color, font=("Helvetica", 10, "bold")).pack(pady=int(5 * self.sf))

        self.onizleme_label = tk.Label(sag_frame, bg=self.btn_bg, fg=self.fg_color)
        self.onizleme_label.pack(fill=tk.BOTH, expand=True, padx=int(10 * self.sf), pady=int(5 * self.sf))

        nav_frame = tk.Frame(sag_frame, bg=self.bg_color)
        nav_frame.pack(pady=int(10 * self.sf))

        self.btn_onceki = self.ozel_buton(nav_frame, "I<", lambda: self.sayfa_degistir(-1))
        self.btn_onceki.pack(side=tk.LEFT, padx=int(5 * self.sf))
        
        self.lbl_sayfa_bilgi = tk.Label(nav_frame, bg=self.bg_color, fg=self.fg_color, font=("Helvetica", 10))
        self.lbl_sayfa_bilgi.pack(side=tk.LEFT, padx=int(10 * self.sf))

        self.btn_sonraki = self.ozel_buton(nav_frame, ">I", lambda: self.sayfa_degistir(1))
        self.btn_sonraki.pack(side=tk.LEFT, padx=int(5 * self.sf))

        mesaj_kutusu = tk.Frame(sag_frame, bg=self.btn_bg, bd=2, relief=tk.FLAT)
        mesaj_kutusu.pack(fill=tk.X, padx=int(10 * self.sf), pady=(0, int(10 * self.sf)))
        
        sol_cizgi = tk.Frame(mesaj_kutusu, bg=self.fg_color, width=int(5 * self.sf))
        sol_cizgi.pack(side=tk.LEFT, fill=tk.Y)
        
        self.lbl_alt_mesaj = tk.Label(mesaj_kutusu, text="Sistem verilerini seçin ve işlemleri uygulayın.", bg=self.btn_bg, fg=self.fg_color, font=("Helvetica", 10), anchor="w")
        self.lbl_alt_mesaj.pack(side=tk.LEFT, fill=tk.X, padx=int(5 * self.sf), pady=int(5 * self.sf))

        self.onizleme_sifirla()

    def ozel_buton(self, parent, metin, komut):
        btn = tk.Button(parent, text=metin, command=komut, 
                        bg=self.btn_bg, fg=self.fg_color, 
                        activebackground=self.btn_active_bg, activeforeground=self.btn_active_fg,
                        font=("Helvetica", 9), relief=tk.FLAT, bd=0, 
                        padx=int(10 * self.sf), pady=int(2 * self.sf), cursor="hand2")
        return btn

    def dantel_ekle(self):
        try:
            dantel_yolu = os.path.join(os.path.dirname(__file__), "2b_dantel_seffaf_siyah.png")
            if os.path.exists(dantel_yolu):
                orijinal_img = Image.open(dantel_yolu).convert("RGBA")
                
                # Hedef yükseklik 100 yapıldı.
                hedef_yukseklik = int(75 * self.sf) 
                oran = hedef_yukseklik / orijinal_img.height
                hedef_genislik = int(orijinal_img.width * oran)
                kucuk_img = orijinal_img.resize((hedef_genislik, hedef_yukseklik), Image.Resampling.LANCZOS)
                
                max_genislik = 3000 
                tekrar_sayisi = (max_genislik // hedef_genislik) + 1
                
                tiled_img = Image.new("RGBA", (tekrar_sayisi * hedef_genislik, hedef_yukseklik), (0, 0, 0, 0))
                
                for i in range(tekrar_sayisi):
                    tiled_img.paste(kucuk_img, (i * hedef_genislik, 0))
                
                self.dantel_tk = ImageTk.PhotoImage(tiled_img)
                # anchor="n" sayesinde resim kırpılmadan üstten hizalanacak
                self.dantel_label = tk.Label(self.root, image=self.dantel_tk, bg=self.bg_color, bd=0, anchor="n")
                self.dantel_label.pack(side=tk.BOTTOM, fill=tk.X)
        except Exception as e:
            pass

    def onizleme_sifirla(self):
        if self.varsayilan_img_tk:
            self.onizleme_label.config(image=self.varsayilan_img_tk, text="", bg=self.bg_color)
        else:
            self.onizleme_label.config(image='', text="Hedef seçilmedi.", bg=self.btn_bg)
            
        self.lbl_sayfa_bilgi.config(text="NO DATA")
        self.btn_onceki.config(state=tk.DISABLED)
        self.btn_sonraki.config(state=tk.DISABLED)

    # --- İŞLEM FONKSİYONLARI ---
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
        except:
            messagebox.showerror("Sistem Hatası", "Veri dosyası okunamadı.")
            return

        aralik = simpledialog.askstring("Veri Aralığı", f"Bu veri {max_sayfa} sayfa.\nAlınacak hedefleri girin (Örn: 1-5, 8):\nTümü için boş bırakın:")
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
        self.onizleme_sifirla()

    def on_pdf_secildi(self, event):
        secili = self.tree.selection()
        if not secili: 
            self.onizleme_sifirla()
            return
            
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
            img.thumbnail((int(380 * self.sf), int(480 * self.sf)), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)

            self.onizleme_label.config(image=tk_img, text="", bg=self.bg_color)
            self.onizleme_label.image = tk_img

            self.lbl_sayfa_bilgi.config(text=f"{self.gecerli_onizleme_sirasi + 1} / {toplam_secili}\n(Orijinal: {gercek_sayfa_indeksi + 1})")
            
            self.btn_onceki.config(state=tk.NORMAL if self.gecerli_onizleme_sirasi > 0 else tk.DISABLED)
            self.btn_sonraki.config(state=tk.NORMAL if self.gecerli_onizleme_sirasi < toplam_secili - 1 else tk.DISABLED)
        except Exception as e:
            pass

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
