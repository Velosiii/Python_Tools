import os
import time
import shutil
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

def yerel_html_olustur(hedef_yolu, hedef_kullanici, profil_bilgisi):
    if not os.path.exists(hedef_yolu): return
    dosyalar = sorted(os.listdir(hedef_yolu))
    
    post_dict = {}
    hikaye_dict = {}
    kapaklar = {}
    
    for d in dosyalar:
        if d.startswith('cover_'):
            h_id = d.split('_')[1].split('.')[0]
            kapaklar[h_id] = d
        elif d.startswith('hikaye_'):
            h_id = d.split('_')[1]
            if h_id not in hikaye_dict: hikaye_dict[h_id] = []
            hikaye_dict[h_id].append(d)
        elif d.startswith('post_'):
            p_id = d.split('_')[1]
            if p_id not in post_dict: post_dict[p_id] = []
            post_dict[p_id].append(d)

    for k in hikaye_dict: hikaye_dict[k].sort()
    for k in post_dict: post_dict[k].sort()

    hikaye_isimleri = profil_bilgisi.get('hikaye_isimleri', {})

    # ÖNE ÇIKANLAR YUVARLAKLARI VE İSİMLERİ İÇİN YENİ HTML TASARIMI
    hikaye_html = ""
    if hikaye_dict:
        hikaye_html = '<div class="highlights">\n'
        for h_id in sorted(hikaye_dict.keys()):
            kapak_img = kapaklar.get(h_id, 'pp.jpg')
            isim = hikaye_isimleri.get(h_id, '')
            
            hikaye_html += f'''
            <div class="highlight-wrapper" onclick="openModal(\'highlight\', \'{h_id}\')">
                <div class="highlight-item"><img src="{kapak_img}"></div>
                <div class="highlight-title" title="{isim}">{isim}</div>
            </div>\n'''
        hikaye_html += '</div>\n'
            
    grid_html = ""
    for p_id in sorted(post_dict.keys(), reverse=True):
        medyalar = post_dict[p_id]
        kapak = medyalar[0]
        
        multi_icon = ""
        video_icon = ""
        if len(medyalar) > 1:
            multi_icon = '<div class="icon"><svg viewBox="0 0 48 48"><path d="M34.8 29.7V11c0-2.9-2.3-5.2-5.2-5.2H11c-2.9 0-5.2 2.3-5.2 5.2v18.7c0 2.9 2.3 5.2 5.2 5.2h18.7c2.8-.1 5.1-2.4 5.1-5.2zM39.2 15v16.1c0 4.5-3.7 8.2-8.2 8.2H14.9c-.6 0-1.1.5-1.1 1.1 0 .6.5 1.1 1.1 1.1h16.1c5.1 0 9.3-4.2 9.3-9.3V15c0-.6-.5-1.1-1.1-1.1-.6 0-1.1.5-1.1 1.1z" fill="currentColor"></path></svg></div>'
        elif kapak.endswith('.mp4'):
            video_icon = '<div class="icon"><svg viewBox="0 0 48 48"><path d="M34.6 22.7L17.5 11.2c-1.3-.9-3-.2-3 1.4v22.8c0 1.6 1.7 2.4 3 1.4l17.1-11.5c1.1-.8 1.1-2.4 0-3.2z" fill="currentColor"></path></svg></div>'
            
        medya_etiketi = f'<video src="{kapak}" muted loop></video>' if kapak.endswith('.mp4') else f'<img src="{kapak}" loading="lazy">'
        grid_html += f'<div class="post" onclick="openModal(\'post\', \'{p_id}\')">\n{multi_icon}{video_icon}\n{medya_etiketi}\n</div>\n'

    takipci = profil_bilgisi.get('takipci', '0')
    takip = profil_bilgisi.get('takip', '0')
    gonderi = profil_bilgisi.get('gonderi', '0')
    biyografi = profil_bilgisi.get('biyografi', '')

    js_post_data = json.dumps(post_dict)
    js_highlight_data = json.dumps(hikaye_dict)

    bos_mesaj = ""
    if not post_dict:
        bos_mesaj = '<div style="text-align:center; padding: 50px; color: #888; grid-column: 1 / -1;">Bu hesapta hiç gönderi yok.</div>'

    html_icerik = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>@{hedef_kullanici} - Tam Arşiv</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; background: #1a1a1a; margin: 0; padding: 30px; color: #efefef; overflow-y: scroll; }}
            .container {{ max-width: 935px; margin: 0 auto; }}
            .header {{ display: flex; align-items: flex-start; margin-bottom: 30px; padding-bottom: 30px; border-bottom: 1px solid #333; }}
            .pp {{ width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin-right: 80px; border: 2px solid #333; padding: 3px; flex-shrink: 0; }}
            .info {{ flex: 1; }}
            .info h1 {{ font-size: 28px; font-weight: 300; margin: 0 0 20px 0; }}
            .stats {{ display: flex; gap: 40px; margin-bottom: 20px; font-size: 16px; }}
            .stats span {{ font-weight: 600; color: #fff; }}
            .bio {{ font-size: 16px; line-height: 1.5; color: #ddd; white-space: pre-wrap; }}
            
            /* ÖNE ÇIKANLAR YENİ TASARIMI */
            .highlights {{ display: flex; gap: 20px; margin-bottom: 40px; padding-bottom: 10px; overflow-x: auto; scrollbar-width: none; }}
            .highlights::-webkit-scrollbar {{ display: none; }}
            .highlight-wrapper {{ display: flex; flex-direction: column; align-items: center; gap: 8px; width: 80px; cursor: pointer; flex-shrink: 0; }}
            .highlight-item {{ width: 80px; height: 80px; border-radius: 50%; border: 2px solid #666; padding: 3px; background: #222; }}
            .highlight-item img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }}
            .highlight-title {{ font-size: 12px; color: #efefef; text-align: center; width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 400; }}
            
            .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
            .post {{ position: relative; aspect-ratio: 1/1; background: #000; overflow: hidden; cursor: pointer; }}
            .post img, .post video {{ width: 100%; height: 100%; object-fit: cover; transition: 0.2s; }}
            .post:hover img, .post:hover video {{ filter: brightness(0.7); }}
            .icon {{ position: absolute; top: 10px; right: 10px; width: 24px; height: 24px; color: white; z-index: 10; pointer-events: none; }}
            
            .modal {{ display: none; position: fixed; z-index: 999; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); justify-content: center; align-items: center; }}
            .modal-content {{ position: relative; max-width: 90%; max-height: 90%; display: flex; justify-content: center; align-items: center; }}
            .modal-content img, .modal-content video {{ max-width: 100vw; max-height: 90vh; object-fit: contain; border-radius: 4px; }}
            .close {{ position: absolute; top: 20px; right: 30px; color: white; font-size: 40px; font-weight: bold; cursor: pointer; z-index: 1000; }}
            .nav-btn {{ position: absolute; top: 50%; transform: translateY(-50%); background: rgba(255,255,255,0.2); color: white; border: none; padding: 15px; cursor: pointer; border-radius: 50%; font-size: 20px; z-index: 1000; transition: 0.2s; }}
            .nav-btn:hover {{ background: rgba(255,255,255,0.5); }}
            .prev {{ left: -60px; }}
            .next {{ right: -60px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="pp.jpg" class="pp" onerror="this.style.display='none'">
                <div class="info">
                    <h1>@{hedef_kullanici}</h1>
                    <div class="stats">
                        <div><span>{gonderi}</span> gönderi</div>
                        <div><span>{takipci}</span> takipçi</div>
                        <div><span>{takip}</span> takip</div>
                    </div>
                    <div class="bio">{biyografi}</div>
                </div>
            </div>
            {hikaye_html}
            <div class="grid">
                {bos_mesaj}
                {grid_html}
            </div>
        </div>

        <div id="myModal" class="modal">
            <span class="close" onclick="closeModal()">&times;</span>
            <div class="modal-content">
                <button class="nav-btn prev" onclick="changeMedia(-1)" id="prevBtn">&#10094;</button>
                <div id="media-container"></div>
                <button class="nav-btn next" onclick="changeMedia(1)" id="nextBtn">&#10095;</button>
            </div>
        </div>

        <script>
            const posts = {js_post_data};
            const highlights = {js_highlight_data};
            let currentMode = ""; 
            let currentId = "";
            let currentIndex = 0;
            let currentArray = [];

            const modal = document.getElementById("myModal");
            const mediaContainer = document.getElementById("media-container");
            const prevBtn = document.getElementById("prevBtn");
            const nextBtn = document.getElementById("nextBtn");

            function openModal(mode, id) {{
                currentMode = mode;
                currentId = id;
                currentIndex = 0;
                
                if (mode === 'post') {{
                    currentArray = posts[id];
                }} else {{
                    currentArray = highlights[id]; 
                }}
                
                if(!currentArray || currentArray.length === 0) return;
                
                updateModal();
                modal.style.display = "flex";
                document.body.style.overflow = "hidden"; 
            }}

            function closeModal() {{
                modal.style.display = "none";
                mediaContainer.innerHTML = ""; 
                document.body.style.overflow = "auto";
            }}

            function updateModal() {{
                const src = currentArray[currentIndex];
                if (src.endsWith('.mp4')) {{
                    mediaContainer.innerHTML = `<video src="${{src}}" controls autoplay style="max-height:90vh;"></video>`;
                }} else {{
                    mediaContainer.innerHTML = `<img src="${{src}}">`;
                }}

                prevBtn.style.display = currentIndex === 0 ? "none" : "block";
                nextBtn.style.display = currentIndex === currentArray.length - 1 ? "none" : "block";
            }}

            function changeMedia(direction) {{
                currentIndex += direction;
                if (currentIndex >= 0 && currentIndex < currentArray.length) {{
                    updateModal();
                }}
            }}

            document.addEventListener('keydown', function(event) {{
                if (modal.style.display === "flex") {{
                    if (event.key === "ArrowRight" && currentIndex < currentArray.length - 1) changeMedia(1);
                    if (event.key === "ArrowLeft" && currentIndex > 0) changeMedia(-1);
                    if (event.key === "Escape") closeModal();
                }}
            }});
        </script>
    </body>
    </html>
    """
    with open(os.path.join(hedef_yolu, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_icerik)


def firefox_profilini_bul():
    appdata = os.getenv('APPDATA')
    if not appdata: return None
    profiles_dir = os.path.join(appdata, "Mozilla", "Firefox", "Profiles")
    if not os.path.exists(profiles_dir): return None
    for klasor in os.listdir(profiles_dir):
        if klasor.endswith('.default-release'): return os.path.join(profiles_dir, klasor)
    return None


def instagram_clicker(hedef):
    ana_klasor = "Instagram_Yedekleri"
    os.makedirs(ana_klasor, exist_ok=True)
    hedef_yolu = os.path.join(ana_klasor, hedef)
    
    profil_yolu = firefox_profilini_bul()
    if not profil_yolu: return

    print("\n[+] Firefox başlatılıyor...")
    options = Options()
    options.add_argument("-profile")
    options.add_argument(profil_yolu)
    
    try:
        driver = webdriver.Firefox(options=options)
    except:
        print("\n[-] HATA: Lütfen Firefox'u tamamen kapatın!")
        return

    driver.get(f"https://www.instagram.com/{hedef}/")
    time.sleep(6) 
    
    print("[+] Sayfa metni okunuyor (Ctrl+A Devrede)...")
    body_text = driver.find_element(By.TAG_NAME, 'body').text
    satirlar = [s.strip() for s in body_text.split('\n') if s.strip()]
    
    takipci, takip, gonderi = None, None, None
    biyografi_satirlari = []
    icerik_basladi = False
    
    durdurma_kelimeleri = ["gönderiler", "reels", "etiketlenenler", "meta", "hakkında", "gizlilik", "koşullar", "önerilen hesaplar", "senin için önerilenler", "keşfet"]
    buton_isimleri = ["profili düzenle", "profili paylaş", "mesaj", "takip et", "takiptesin", "reklam araçları", "e-posta", "ara"]
    
    for satir in satirlar:
        kucuk = satir.lower()
        if kucuk in durdurma_kelimeleri or "tarafından takip" in kucuk or "kişi takip ediyor" in kucuk or "ortak takip" in kucuk:
            if icerik_basladi: break
            
        if kucuk == hedef.lower() or kucuk == f"@{hedef.lower()}":
            icerik_basladi = True
            continue
            
        if icerik_basladi:
            if gonderi is None and ("gönderi" in kucuk or ("post" in kucuk and len(kucuk.split()) <= 2)):
                sayi = ''.join(filter(str.isdigit, satir))
                if sayi: gonderi = sayi
                continue
            if takipci is None and ("takipçi" in kucuk or "follower" in kucuk):
                sayi = ''.join(filter(str.isdigit, satir))
                if sayi: takipci = sayi
                continue
            if takip is None and ("takip" in kucuk and "takipçi" not in kucuk and "follower" not in kucuk):
                sayi = ''.join(filter(str.isdigit, satir))
                if sayi: takip = sayi
                continue
                
            if kucuk in buton_isimleri: continue
            
            biyografi_satirlari.append(satir)
            
    biyografi = "<br>".join(biyografi_satirlari)
    gonderi = gonderi if gonderi else "0"
    takipci = takipci if takipci else "0"
    takip = takip if takip else "0"
    
    pp_link = driver.execute_script("let img = document.querySelector('header img'); return img ? img.src : '';")
    profil_bilgisi = {'takipci': takipci, 'takip': takip, 'gonderi': gonderi, 'biyografi': biyografi, 'pp_link': pp_link, 'hikaye_isimleri': {}}

    indirilen_linkler = set()
    hikaye_kapaklari = []
    hikaye_grup_medyalari = []
    gonderiler = []
    
    print("\n[+] Öne Çıkanlar (Highlights) aranıyor...")
    hikaye_grup_sayisi = driver.execute_script("""
        return document.querySelectorAll('a[href*="/stories/"]').length;
    """)

    if hikaye_grup_sayisi > 0:
        print(f"[+] Toplam {hikaye_grup_sayisi} adet Hikaye/Öne Çıkanlar grubu bulundu. Sırayla giriliyor...")
        
        for i in range(hikaye_grup_sayisi):
            print(f"    -> {i+1}. Gruba giriliyor...")
            
            # --- YENİ: KAPAK VE İSİM AYIKLAMA ALGORİTMASI ---
            kapak_data = driver.execute_script(f"""
                let h = document.querySelectorAll('a[href*="/stories/"]');
                if(h.length > {i}) {{
                    let img = h[{i}].querySelector('img');
                    let src = img ? img.src : '';
                    
                    let li = h[{i}].closest('li');
                    let title = '';
                    if (li) {{
                        let lines = li.innerText.trim().split('\\n').filter(t => t.trim() !== '');
                        if(lines.length > 0) title = lines[lines.length - 1]; // İsmi en alt satırdan çeker
                    }}
                    return [src, title];
                }}
                return ['', ''];
            """)
            
            kapak_src = kapak_data[0]
            kapak_isim = kapak_data[1]
            
            hikaye_kapaklari.append(kapak_src)
            profil_bilgisi['hikaye_isimleri'][f"{i:02d}"] = kapak_isim
            # --------------------------------------------------
            
            tiklandi = driver.execute_script(f"""
                let h = document.querySelectorAll('a[href*="/stories/"]');
                if(h.length > {i}) {{ h[{i}].click(); return true; }}
                return false;
            """)
            
            if not tiklandi: continue
            time.sleep(5) 
            
            aktif_grup_linkleri = []
            
            if "/stories/" in driver.current_url:
                tekrarlanan_medya_sayaci = 0
                grup_baslangic_url = driver.current_url 
                
                while True:
                    eski_sayi = len(indirilen_linkler)
                    
                    aktif_hikaye = driver.execute_script("""
                        let imgs = Array.from(document.querySelectorAll('img')).filter(img => img.width > 300 && !img.src.includes('profile_pic')).map(i => i.src);
                        let vids = Array.from(document.querySelectorAll('video')).map(v => v.src);
                        return [...imgs, ...vids];
                    """)
                    
                    for m in aktif_hikaye:
                        if m and not m.startswith('blob:'):
                            if m not in indirilen_linkler:
                                indirilen_linkler.add(m)
                            if m not in aktif_grup_linkleri:
                                aktif_grup_linkleri.append(m)
                    
                    if len(indirilen_linkler) == eski_sayi:
                        tekrarlanan_medya_sayaci += 1
                    else:
                        tekrarlanan_medya_sayaci = 0
                        
                    if tekrarlanan_medya_sayaci >= 5:
                        break
                        
                    try:
                        driver.execute_script("""
                            let btn = document.querySelector('.coreSpriteRightChevron, button[aria-label="İleri"], button[aria-label="Next"]');
                            if(btn) btn.click();
                        """)
                        body = driver.find_element(By.TAG_NAME, 'body')
                        body.send_keys(Keys.RIGHT)
                        time.sleep(3.5)
                    except:
                        break
                        
                    yeni_url = driver.current_url
                    if "/stories/" not in yeni_url or yeni_url != grup_baslangic_url:
                        break
            
            if aktif_grup_linkleri:
                hikaye_grup_medyalari.append(aktif_grup_linkleri)
            
            driver.get(f"https://www.instagram.com/{hedef}/")
            time.sleep(4)
            
        print(f"[+] Tüm hikayeler bitti.")
    else:
        print("[-] Öne çıkan hikaye bulunamadı.")

    print("\n[+] İlk gönderi aranıyor...")
    gonderi_var = False
    try:
        ilk_post = driver.execute_script("""
            let p = document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]');
            if(p.length > 0) { p[0].click(); return true; }
            return false;
        """)
        
        if not ilk_post:
            print("[-] Ekranda gönderi bulunamadı. Sadece toplanan veriler kaydedilecek.")
        else:
            time.sleep(5) 
            gonderi_var = True
    except:
        print("[-] Gönderi bulunurken hata oluştu. Sadece toplanan veriler kaydedilecek.")

    if gonderi_var:
        print("[+] Gönderiler sırayla toplanıyor...")
        gonderi_sayaci = 1
        aktif_post = []
        
        while True:
            aktif_medyalar = driver.execute_script("""
                let popup = document.querySelector('[role="dialog"]');
                if(!popup) return [];
                let r = Array.from(popup.querySelectorAll('img')).filter(img => img.width > 350 && !img.src.includes('profile_pic')).map(img => img.src);
                let v = Array.from(popup.querySelectorAll('video')).map(vid => vid.src);
                return [...r, ...v];
            """)
            
            video_var_mi = any(('.mp4' in str(m) or 'video' in str(m)) for m in aktif_medyalar)
            
            for m in aktif_medyalar:
                if m and m not in indirilen_linkler and not m.startswith('blob:'):
                    indirilen_linkler.add(m)
                    aktif_post.append(m)

            try:
                kaydirildi = driver.execute_script("""
                    let popup = document.querySelector('[role="dialog"]');
                    if(!popup) return false;
                    let oklar = Array.from(popup.querySelectorAll('button')).filter(b => b.classList.length > 0 && (b.getAttribute('aria-label') === 'İleri' || b.getAttribute('aria-label') === 'Next'));
                    if (oklar.length > 0) {
                        for(let btn of oklar) {
                            if (btn.closest('ul') || btn.closest('.x1n2onr6')) {
                                btn.click();
                                return true;
                            }
                        }
                    }
                    return false;
                """)
                if kaydirildi:
                    time.sleep(3.5 if video_var_mi else 2.5)
                    continue 
            except:
                pass

            if aktif_post:
                gonderiler.append(aktif_post)
                aktif_post = []

            eski_post_url = driver.current_url

            try:
                body = driver.find_element(By.TAG_NAME, 'body')
                body.send_keys(Keys.RIGHT)
                time.sleep(4 if video_var_mi else 3)
            except:
                break
                
            if driver.current_url == eski_post_url:
                break
                
            print(f"\r[+] Taranan Gönderi: {gonderi_sayaci} | Hafızaya Alınan Medya: {len(indirilen_linkler)}", end="")
            gonderi_sayaci += 1

    driver.quit()

    if not indirilen_linkler and not profil_bilgisi.get('pp_link'):
        print("\n[-] Ekranda indirilecek hiçbir medya bulunamadı.")
        return

    os.makedirs(hedef_yolu, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"}
    
    print(f"\n\n[+] Toplam {len(indirilen_linkler)} adet dosya indiriliyor...")
    
    if profil_bilgisi.get('pp_link'):
        try:
            c = requests.get(profil_bilgisi['pp_link'], headers=headers)
            if c.status_code == 200:
                with open(os.path.join(hedef_yolu, "pp.jpg"), 'wb') as f: f.write(c.content)
        except: pass

    for idx, link in enumerate(hikaye_kapaklari):
        if link:
            try:
                c = requests.get(link, headers=headers)
                if c.status_code == 200:
                    with open(os.path.join(hedef_yolu, f"cover_{idx:02d}.jpg"), 'wb') as f: f.write(c.content)
            except: pass

    for g_idx, grup_medyalari in enumerate(hikaye_grup_medyalari):
        for m_idx, link in enumerate(grup_medyalari):
            try:
                c = requests.get(link, headers=headers)
                if c.status_code == 200:
                    uzanti = ".mp4" if "mp4" in link or "video" in link else ".jpg"
                    with open(os.path.join(hedef_yolu, f"hikaye_{g_idx:02d}_{m_idx:04d}{uzanti}"), 'wb') as f:
                        f.write(c.content)
            except: pass

    for p_idx, post_medyalari in enumerate(gonderiler):
        for m_idx, link in enumerate(post_medyalari):
            try:
                cevap = requests.get(link, headers=headers)
                if cevap.status_code == 200:
                    uzanti = ".mp4" if "mp4" in link or "video" in link else ".jpg"
                    with open(os.path.join(hedef_yolu, f"post_{p_idx:04d}_{m_idx:02d}{uzanti}"), 'wb') as f:
                        f.write(cevap.content)
            except: pass

    print("[+] Etkileşimli (Tıklamalı) HTML arayüzü inşa ediliyor...")
    yerel_html_olustur(hedef_yolu, hedef, profil_bilgisi)
    
    print("[+] Klasör ZIP formatına dönüştürülüyor...")
    shutil.make_archive(hedef_yolu, 'zip', hedef_yolu)
    shutil.rmtree(hedef_yolu)
    
    print(f"\n[✓] İŞLEM KUSURSUZ! Çevrimdışı Instagram Galerisi '{ana_klasor}/{hedef}.zip' içine kaydedildi.")

if __name__ == "__main__":
    hedef_hesap = input("Hedef Profilin Kullanıcı Adını Yaz: ").strip()
    if hedef_hesap:
        instagram_clicker(hedef_hesap)
