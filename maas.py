import json
import os
from datetime import datetime, timedelta
import calendar
import sys

DATA_FILE = "puantaj_kayitlari.json"
BACKUP_FOLDER = "backups"

def clear_console():
    """Konsolu temizle"""
    if os.name == 'nt':
        os.system('cls')
    elif os.environ.get('TERM'):
        os.system('clear')


def input_int(prompt, min_value=None, max_value=None):
    """Güvenli tam sayı girişi"""
    while True:
        try:
            value = input(prompt)
            if value.strip() == '':
                print("Lütfen bir değer giriniz.")
                continue

            value = int(value)
            if min_value is not None and value < min_value:
                print(f"Lütfen {min_value} veya daha büyük bir değer giriniz.")
                continue
            if max_value is not None and value > max_value:
                print(f"Lütfen {max_value} veya daha küçük bir değer giriniz.")
                continue
            return value
        except ValueError:
            print("Lütfen geçerli bir sayı giriniz.")


def input_float(prompt, min_value=None, max_value=None):
    """Güvenli ondalıklı sayı girişi"""
    while True:
        try:
            value = input(prompt)
            if value.strip() == '':
                print("Lütfen bir değer giriniz.")
                continue

            value = float(value)
            if min_value is not None and value < min_value:
                print(f"Lütfen {min_value} veya daha büyük bir değer giriniz.")
                continue
            if max_value is not None and value > max_value:
                print(f"Lütfen {max_value} veya daha küçük bir değer giriniz.")
                continue
            return value
        except ValueError:
            print("Lütfen geçerli bir sayı giriniz.")


def create_backup():
    """Veri yedekleme oluştur"""
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_FOLDER, f"puantaj_backup_{timestamp}.json")

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as source:
                data = source.read()
            with open(backup_file, "w", encoding="utf-8") as target:
                target.write(data)
            return True
        except Exception as e:
            print(f"Yedek oluşturulurken hata: {e}")
            return False
    return False


def load_data():
    """Verileri yükle"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Veri dosyası okunurken hata oluştu: {e}")
            # Yedeklerden geri yükleme seçeneği sun
            restore_backup_option = input("Yedekten geri yüklemek ister misiniz? (E/H): ").strip().upper()
            if restore_backup_option == 'E':
                return restore_backup()
            return {}
    else:
        return {}


def restore_backup():
    """Yedekten geri yükle"""
    if not os.path.exists(BACKUP_FOLDER):
        print("Yedek klasörü bulunamadı!")
        return {}

    backups = [f for f in os.listdir(BACKUP_FOLDER) if f.endswith('.json')]
    if not backups:
        print("Yedek dosyası bulunamadı!")
        return {}

    print("Mevcut yedekler:")
    for i, backup in enumerate(sorted(backups, reverse=True), 1):
        print(f"{i}. {backup}")

    try:
        choice = input("Hangi yedeği geri yüklemek istersiniz? (Çıkış için 0): ")
        if choice == '0':
            return {}

        choice = int(choice)
        if 1 <= choice <= len(backups):
            selected_backup = sorted(backups, reverse=True)[choice - 1]
            backup_path = os.path.join(BACKUP_FOLDER, selected_backup)

            with open(backup_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Ana veri dosyasına yaz
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"{selected_backup} başarıyla geri yüklendi!")
            return data
        else:
            print("Geçersiz seçim!")
            return {}
    except (ValueError, IndexError):
        print("Geçersiz seçim!")
        return {}


def save_data(data):
    """Verileri kaydet"""
    # Önce yedek oluştur
    create_backup()

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Veri kaydedilirken hata oluştu: {e}")
        return False


def get_personel_info(data, calisan_id):
    """Personel bilgilerini getir"""
    return data.get(calisan_id, [])


def personel_aktif_mi(data, calisan_id):
    """Personel aktif mi kontrol et"""
    kayitlar = get_personel_info(data, calisan_id)
    if not kayitlar:
        return True  # yeni personel
    return kayitlar[0].get("aktif", True)


def personel_isten_cikis_tarihi(data, calisan_id):
    """Personelin işten çıkış tarihini getir"""
    kayitlar = get_personel_info(data, calisan_id)
    if not kayitlar:
        return None
    return kayitlar[0].get("isten_cikma_tarihi")


def ay_str_to_datetime(ay_str):
    """Ay string'ini datetime'a çevir"""
    return datetime.strptime(ay_str + "-01", "%Y-%m-%d")


def get_current_month():
    """Geçerli ayı al"""
    return datetime.now().strftime("%Y-%m")


def get_month_days(ay_str):
    """Belirtilen aydaki gün sayısını hesapla"""
    try:
        ay_dt = ay_str_to_datetime(ay_str)
        _, num_days = calendar.monthrange(ay_dt.year, ay_dt.month)
        return num_days
    except ValueError:
        return 30  # Varsayılan değer


def validate_date(date_str, format="%Y-%m-%d"):
    """Tarih formatını doğrula"""
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_month(month_str):
    """Ay formatını doğrula"""
    return validate_date(month_str + "-01", "%Y-%m-%d")


def personel_listele(data):
    """Tüm personelleri listele"""
    if not data:
        print("Kayıtlı personel bulunamadı.")
        return []

    print("\n--- Tüm Personeller ---")
    for i, (calisan_id, kayitlar) in enumerate(data.items(), 1):
        aktif = kayitlar[0].get("aktif", True)
        durum = "AKTİF" if aktif else "PASİF"
        print(f"{i}. ID: {calisan_id}, Ad: {kayitlar[0]['ad_soyad']}, Durum: {durum}")

    return list(data.keys())


def puantaj_girisi_veya_devam():
    """Puantaj girişi yap veya devam et"""
    data = load_data()

    # Personel listesini göster ve seçim yap
    print("\n--- Puantaj Girişi ---")
    calisan_ids = personel_listele(data)
    if not calisan_ids:
        # Yeni personel ekleme seçeneği sun
        yeni_secim = input("Kayıtlı personel yok. Yeni personel eklemek ister misiniz? (E/H): ").strip().upper()
        if yeni_secim != 'E':
            return

        calisan_id = input("Yeni personel ID: ").strip()
        if not calisan_id:
            print("Personel ID boş olamaz!")
            return
        kayitlar = []
    else:
        try:
            secim = input("\nPersonel seçmek için numara girin (0: Yeni personel): ").strip()
            if secim == '0':
                calisan_id = input("Yeni personel ID: ").strip()
                if not calisan_id:
                    print("Personel ID boş olamaz!")
                    return
                kayitlar = []
            else:
                secim = int(secim)
                if 1 <= secim <= len(calisan_ids):
                    calisan_id = calisan_ids[secim - 1]
                    kayitlar = get_personel_info(data, calisan_id)
                else:
                    print("Geçersiz seçim!")
                    return
        except ValueError:
            print("Geçersiz giriş!")
            return

    yeni_personel = False

    isten_cikis_tarihi_str = personel_isten_cikis_tarihi(data, calisan_id)
    isten_cikis_tarihi = None
    if isten_cikis_tarihi_str:
        try:
            isten_cikis_tarihi = datetime.strptime(isten_cikis_tarihi_str, "%Y-%m-%d")
        except Exception:
            pass

    if kayitlar:
        print(f"\nBu ID ile kayıtlı personel bulundu: {kayitlar[0]['ad_soyad']}")
        print("Mevcut ay kayıtları:")
        for i, k in enumerate(kayitlar, 1):
            puantaj_sayisi = len(k['puantaj'])
            durum = k.get('durum', 'KAPATILMAMIŞ')
            print(f"{i}. {k['ay']} ({puantaj_sayisi} gün kayıtlı, {durum})")

        sec = input("\nDevam etmek istediğiniz ayı yazınız (ör: 2025-08), yoksa yeni ay için ENTER basınız: ").strip()
        ay_kayit = None

        if sec:
            for k in kayitlar:
                if k["ay"] == sec:
                    ay_kayit = k
                    break

        if ay_kayit:
            ad_soyad = ay_kayit["ad_soyad"]
            maas_tutari = ay_kayit["brut_maas"]
            ay = ay_kayit["ay"]
            ay_gun = ay_kayit["ay_gun"]
            print(f"{ay} ayı için kayıt devam ettiriliyor.")
        else:
            print("Yeni ay için kayıt başlatılıyor.")
            ad_soyad = kayitlar[0]["ad_soyad"]
            maas_tutari = kayitlar[0]["brut_maas"]

            while True:
                ay = input("Ay (örn: 2025-08) veya geçerli ay için ENTER: ").strip()
                if not ay:
                    ay = get_current_month()

                if validate_month(ay):
                    break
                else:
                    print("Geçersiz ay formatı! Örnek: 2025-08")

            ay_gun = get_month_days(ay)
            print(f"{ay} ayında {ay_gun} gün var.")

            ay_kayit = {
                "id": calisan_id,
                "ad_soyad": ad_soyad,
                "ay": ay,
                "brut_maas": maas_tutari,
                "ay_gun": ay_gun,
                "puantaj": [],
                "hesaplama": {},
                "durum": "KAPATILMAMIŞ",
                "aktif": kayitlar[0].get("aktif", True),
                "isten_cikma_tarihi": kayitlar[0].get("isten_cikma_tarihi", None)
            }
            data[calisan_id].append(ay_kayit)
    else:
        print("Bu ID ile kayıtlı personel yok. Yeni kayıt oluşturulacak.")
        yeni_personel = True
        ad_soyad = input("Ad Soyad: ")
        maas_tutari = input_float("Aylık Brüt Maaş (₺): ", min_value=0)

        while True:
            ay = input("Ay (örn: 2025-08) veya geçerli ay için ENTER: ").strip()
            if not ay:
                ay = get_current_month()

            if validate_month(ay):
                break
            else:
                print("Geçersiz ay formatı! Örnek: 2025-08")

        ay_gun = get_month_days(ay)
        print(f"{ay} ayında {ay_gun} gün var.")

        ay_kayit = {
            "id": calisan_id,
            "ad_soyad": ad_soyad,
            "ay": ay,
            "brut_maas": maas_tutari,
            "ay_gun": ay_gun,
            "puantaj": [],
            "hesaplama": {},
            "durum": "KAPATILMAMIŞ",
            "aktif": True,
            "isten_cikma_tarihi": None
        }
        if calisan_id in data:
            data[calisan_id].append(ay_kayit)
        else:
            data[calisan_id] = [ay_kayit]

    clear_console()

    # Eğer işten çıkış tarihi varsa ve seçili ay işten çıkış ayından büyükse puantaj engellenir
    if isten_cikis_tarihi:
        ay_dt = ay_str_to_datetime(ay_kayit["ay"])
        if ay_dt > isten_cikis_tarihi.replace(day=1):
            print("UYARI: İşten çıkış tarihinden sonraki ay için puantaj girişi yapılamaz!")
            return

    mevcut_gunler = {p["gun"] for p in ay_kayit["puantaj"]}
    # Eğer işten çıkış tarihi bu ayda ise, sadece çıkış gününe kadar izin ver
    max_gun = ay_kayit["ay_gun"]
    if isten_cikis_tarihi:
        ay_dt = ay_str_to_datetime(ay_kayit["ay"])
        if ay_dt.year == isten_cikis_tarihi.year and ay_dt.month == isten_cikis_tarihi.month:
            max_gun = isten_cikis_tarihi.day

    eksik_gunler = [g for g in range(1, max_gun + 1) if g not in mevcut_gunler]

    if not eksik_gunler:
        print("Bu ayın tüm günleri için puantaj zaten girilmiş.")
        return

    print(f"\n{ay_kayit['ad_soyad']} - {ay} ayı için puantaj girişi")
    print("=" * 50)
    print("Her gün için aşağıdaki kodlardan birini girin:")
    print("C: Çalıştı, I: İzinli, D: Devamsız, Y: Yarım Gün, S: Saatlik Kesinti, R: Resmi Tatil")
    print("Girişten çıkmak için 'q' tuşuna basabilirsiniz.")

    for g in eksik_gunler:
        # Günün haftasonu olup olmadığını kontrol et
        try:
            ay_dt = ay_str_to_datetime(ay)
            gun_dt = datetime(ay_dt.year, ay_dt.month, g)
            haftasonu = gun_dt.weekday() >= 5  # 5=Cumartesi, 6=Pazar

            gun_bilgisi = f"{g}. gün ({gun_dt.strftime('%a')})"
            if haftasonu:
                gun_bilgisi += " [Haftasonu]"
        except:
            gun_bilgisi = f"{g}. gün"

        while True:
            kod = input(f"{gun_bilgisi} durumu (C/I/D/Y/S/R veya q-Çıkış): ").strip().upper()

            if kod == "Q":
                print("Puantaj girişi durduruldu. Kaldığınız yerden devam edebilirsiniz.")
                if save_data(data):
                    print("Veriler kaydedildi.")
                return
            elif kod in ['C', 'I', 'D', 'Y', 'S', 'R']:
                if kod == 'S':
                    saat = input_int(f"  {g}. gün kaç saat kesinti var?: ", min_value=1, max_value=12)
                    ay_kayit["puantaj"].append({'gun': g, 'durum': kod, 'saat': saat})
                else:
                    ay_kayit["puantaj"].append({'gun': g, 'durum': kod, 'saat': 0})
                break
            else:
                print("Geçersiz kod! Lütfen C, I, D, Y, S, R veya q giriniz.")
                continue

        if not save_data(data):
            print("HATA: Veri kaydedilemedi!")
            return

    print("\nEklendi! Kaldığınız yerden istediğiniz zaman devam edebilirsiniz.")


def ay_hesapla_ve_kapat():
    """Ayı kapat ve hesaplama yap"""
    data = load_data()

    # Personel listesini göster ve seçim yap
    print("\n--- Ay Kapatma ---")
    calisan_ids = personel_listele(data)
    if not calisan_ids:
        return

    try:
        secim = input("\nPersonel seçmek için numara girin: ").strip()
        if not secim:
            print("Geçersiz seçim!")
            return

        secim = int(secim)
        if 1 <= secim <= len(calisan_ids):
            calisan_id = calisan_ids[secim - 1]
        else:
            print("Geçersiz seçim!")
            return
    except ValueError:
        print("Geçersiz giriş!")
        return

    kayitlar = get_personel_info(data, calisan_id)
    if not kayitlar:
        print("Bu ID'ye ait kayıt yok.")
        return

    print(f"\n{calisan_id} - {kayitlar[0]['ad_soyad']} için mevcut ay kayıtları:")
    kapatilabilir_kayitlar = [k for k in kayitlar if k.get('durum') != 'KAPATILDI']

    if not kapatilabilir_kayitlar:
        print("Tüm aylar zaten kapatılmış.")
        return

    for i, k in enumerate(kapatilabilir_kayitlar, 1):
        puantaj_sayisi = len(k['puantaj'])
        durum = k.get('durum', 'KAPATILMAMIŞ')
        print(f"{i}. {k['ay']} ({puantaj_sayisi} gün kayıtlı, {durum})")

    try:
        secim = input("\nKapatmak istediğiniz ayın numarasını girin: ").strip()
        if not secim:
            print("Geçersiz seçim!")
            return

        secim = int(secim)
        if 1 <= secim <= len(kapatilabilir_kayitlar):
            kayit = kapatilabilir_kayitlar[secim - 1]
        else:
            print("Geçersiz seçim!")
            return
    except ValueError:
        print("Geçersiz giriş!")
        return

    isten_cikis_tarihi_str = kayit.get("isten_cikma_tarihi")
    isten_cikis_tarihi = None
    if isten_cikis_tarihi_str:
        try:
            isten_cikis_tarihi = datetime.strptime(isten_cikis_tarihi_str, "%Y-%m-%d")
        except Exception:
            pass

    puantaj = kayit["puantaj"]
    ay_gun = kayit["ay_gun"]
    maas_tutari = kayit["brut_maas"]
    ay_dt = ay_str_to_datetime(kayit["ay"])

    # Eğer işten çıkış tarihi bu ayda ise, sadece o güne kadar olan puantajı dikkate al
    max_gun = ay_gun
    if isten_cikis_tarihi and ay_dt.year == isten_cikis_tarihi.year and ay_dt.month == isten_cikis_tarihi.month:
        max_gun = isten_cikis_tarihi.day

    puantaj_filtreli = [p for p in puantaj if p['gun'] <= max_gun]
    girilen_gunler = set([p['gun'] for p in puantaj_filtreli])
    eksik_gunler = [g for g in range(1, max_gun + 1) if g not in girilen_gunler]

    # Sadece işten çıkış YOKSA ve eksik gün varsa kapatma engellensin
    if not isten_cikis_tarihi and eksik_gunler:
        print(f"Uyarı: Eksik puantaj günleri var! Bu ay kapatılamaz.")
        print("Eksik günler:", ", ".join(str(g) for g in eksik_gunler))
        return

    # İşten çıkış varsa, sadece çıkış gününe kadar olan puantajın eksik olup olmadığına bakılır, eksikse yine engellenir
    if isten_cikis_tarihi and ay_dt.year == isten_cikis_tarihi.year and ay_dt.month == isten_cikis_tarihi.month and eksik_gunler:
        print(f"Uyarı: İşten çıkış ayı için eksik puantaj günleri var! Bu ay kapatılamaz.")
        print("Eksik günler:", ", ".join(str(g) for g in eksik_gunler))
        return

    gunluk_saat = 9
    net_tutar_gunluk = maas_tutari / ay_gun
    net_tutar_saatlik = net_tutar_gunluk / gunluk_saat

    calisilan_gun = izinli_gun = devamsiz_gun = yarim_gun = saatlik_kesinti_toplam = resmi_tatil_gun = 0
    yarim_gun_maaş = 0

    for p in puantaj_filtreli:
        kod = p['durum']
        saat = p['saat']
        if kod == 'C':
            calisilan_gun += 1
        elif kod == 'I':
            izinli_gun += 1
        elif kod == 'D':
            devamsiz_gun += 1
        elif kod == 'Y':
            yarim_gun += 1
            yarim_gun_maaş += net_tutar_gunluk / 2
        elif kod == 'S':
            saatlik_kesinti_toplam += saat
        elif kod == 'R':
            resmi_tatil_gun += 1

    # Hesaplamalar
    izinli_kesinti = izinli_gun * net_tutar_gunluk
    devamsiz_kesinti = devamsiz_gun * net_tutar_gunluk * 2
    saatlik_kesinti = saatlik_kesinti_toplam * net_tutar_saatlik
    toplam_maaş = (calisilan_gun * net_tutar_gunluk) + yarim_gun_maaş + (resmi_tatil_gun * net_tutar_gunluk)
    net_maaş = toplam_maaş - izinli_kesinti - devamsiz_kesinti - saatlik_kesinti

    kayit["hesaplama"] = {
        "calisilan_gun": calisilan_gun,
        "yarim_gun": yarim_gun,
        "izinli_gun": izinli_gun,
        "devamsiz_gun": devamsiz_gun,
        "resmi_tatil_gun": resmi_tatil_gun,
        "yarim_gun_maas": round(yarim_gun_maaş, 2),
        "izinli_kesinti": round(izinli_kesinti, 2),
        "devamsiz_kesinti": round(devamsiz_kesinti, 2),
        "saatlik_kesinti_toplam": saatlik_kesinti_toplam,
        "saatlik_kesinti": round(saatlik_kesinti, 2),
        "resmi_tatil_maas": round(resmi_tatil_gun * net_tutar_gunluk, 2),
        "toplam_maas": round(toplam_maaş, 2),
        "net_maas": round(max(0, net_maaş), 2)
    }

    kayit["durum"] = "KAPATILDI"
    kayit["kapatma_tarihi"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if save_data(data):
        print(f"\n{kayit['ay']} ayı kapatıldı! Net maaş: {kayit['hesaplama']['net_maas']}₺")
        if isten_cikis_tarihi:
            print("(İşten çıkış varsa sadece o güne kadar hesaplandı)")
    else:
        print("HATA: Veri kaydedilemedi!")


def kayit_goruntule():
    """Kayıtları görüntüle"""
    data = load_data()

    # Personel listesini göster ve seçim yap
    print("\n--- Kayıt Görüntüleme ---")
    calisan_ids = personel_listele(data)
    if not calisan_ids:
        return

    try:
        secim = input("\nPersonel seçmek için numara girin: ").strip()
        if not secim:
            print("Geçersiz seçim!")
            return

        secim = int(secim)
        if 1 <= secim <= len(calisan_ids):
            calisan_id = calisan_ids[secim - 1]
        else:
            print("Geçersiz seçim!")
            return
    except ValueError:
        print("Geçersiz giriş!")
        return

    kayitlar = get_personel_info(data, calisan_id)
    if not kayitlar:
        print("Bu ID'ye ait kayıt yok.")
        return

    print(f"\n{calisan_id} - {kayitlar[0]['ad_soyad']} için kayıtlı aylar:")
    for i, kayit in enumerate(kayitlar, 1):
        durum = kayit.get('durum', 'KAPATILMAMIŞ')
        print(f"{i}. {kayit['ay']} ({durum})")

    try:
        secim = input("\nGörüntülemek istediğiniz ayın numarasını girin (0: Tümü): ").strip()
        if secim == '0':
            # Tüm ayları göster
            for kayit in kayitlar:
                print_kayit_detay(kayit)
            return

        if not secim:
            print("Geçersiz seçim!")
            return

        secim = int(secim)
        if 1 <= secim <= len(kayitlar):
            kayit = kayitlar[secim - 1]
            print_kayit_detay(kayit)
        else:
            print("Geçersiz seçim!")
            return
    except ValueError:
        print("Geçersiz giriş!")
        return


def print_kayit_detay(kayit):
    """Kayıt detaylarını yazdır"""
    print("\n" + "=" * 60)
    print(f"Personel ID: {kayit['id']}")
    print(f"Ad Soyad: {kayit['ad_soyad']}")
    print(f"Ay: {kayit['ay']}")
    print(f"Brüt Maaş: {kayit['brut_maas']}₺")
    print(f"Ay Gün Sayısı: {kayit['ay_gun']}")
    durum = 'AKTİF' if kayit.get('aktif', True) else f'İŞTEN ÇIKTI ({kayit.get("isten_cikma_tarihi", "-")})'
    print(f"Durum: {durum}")
    print(f"Kayıt Durumu: {kayit.get('durum', 'KAPATILMAMIŞ')}")

    if kayit.get("hesaplama"):
        print("\n--- HESAPLAMA DETAYLARI ---")
        print(f"Çalışılan Gün: {kayit['hesaplama']['calisilan_gun']}")
        print(f"Yarım Gün: {kayit['hesaplama']['yarim_gun']}")
        print(f"İzinli Gün: {kayit['hesaplama']['izinli_gun']}")
        print(f"Devamsız Gün: {kayit['hesaplama']['devamsiz_gun']}")
        print(f"Resmi Tatil Gün: {kayit['hesaplama']['resmi_tatil_gun']}")
        print(f"Saatlik Kesinti: {kayit['hesaplama']['saatlik_kesinti_toplam']} saat")
        print(f"Yarım Gün Maaş: {kayit['hesaplama']['yarim_gun_maas']}₺")
        print(f"İzinli Kesinti: {kayit['hesaplama']['izinli_kesinti']}₺")
        print(f"Devamsız Kesinti: {kayit['hesaplama']['devamsiz_kesinti']}₺")
        print(f"Saatlik Kesinti: {kayit['hesaplama']['saatlik_kesinti']}₺")
        print(f"Resmi Tatil Maaş: {kayit['hesaplama']['resmi_tatil_maas']}₺")
        print(f"Toplam Maaş: {kayit['hesaplama']['toplam_maas']}₺")
        print(f"Net Maaş: {kayit['hesaplama']['net_maas']}₺")
    else:
        print("Bu ay henüz kapatılmamış.")

    print("\n--- GÜNLÜK PUANTAJ ---")
    if kayit['puantaj']:
        for p in sorted(kayit['puantaj'], key=lambda x: x['gun']):
            durum_aciklamasi = {
                'C': 'Çalıştı',
                'I': 'İzinli',
                'D': 'Devamsız',
                'Y': 'Yarım Gün',
                'S': 'Saatlik Kesinti',
                'R': 'Resmi Tatil'
            }
            durum = durum_aciklamasi.get(p['durum'], p['durum'])
            saat_bilgisi = f", {p['saat']} saat" if p['saat'] > 0 else ""
            print(f"  {p['gun']}. gün: {durum}{saat_bilgisi}")
    else:
        print("  Henüz puantaj girişi yapılmamış.")

    if kayit.get('kapatma_tarihi'):
        print(f"\nKapatma Tarihi: {kayit['kapatma_tarihi']}")

    print("=" * 60)


def personel_isten_cikar():
    """Personeli işten çıkar"""
    data = load_data()

    # Personel listesini göster ve seçim yap
    print("\n--- Personel İşten Çıkarma ---")
    calisan_ids = personel_listele(data)
    if not calisan_ids:
        return

    try:
        secim = input("\nİşten çıkarılacak personel numarasını girin: ").strip()
        if not secim:
            print("Geçersiz seçim!")
            return

        secim = int(secim)
        if 1 <= secim <= len(calisan_ids):
            calisan_id = calisan_ids[secim - 1]
        else:
            print("Geçersiz seçim!")
            return
    except ValueError:
        print("Geçersiz giriş!")
        return

    kayitlar = get_personel_info(data, calisan_id)
    if not kayitlar:
        print("Bu ID'ye ait personel yok.")
        return

    if not personel_aktif_mi(data, calisan_id):
        print("Bu personel zaten işten çıkmış!")
        return

    # Personel bilgilerini göster
    print(f"\nİşten çıkarılacak personel: {kayitlar[0]['ad_soyad']}")

    while True:
        tarih = input("İşten çıkış tarihi (örn: 2025-08-21) veya bugün için ENTER: ").strip()
        if not tarih:
            tarih = datetime.now().strftime("%Y-%m-%d")
            break
        elif validate_date(tarih):
            break
        else:
            print("Geçersiz tarih formatı! Örnek: 2025-08-21")

    # Onay al
    onay = input(
        f"{kayitlar[0]['ad_soyad']} isimli personeli işten çıkarmak istediğinize emin misiniz? (E/H): ").strip().upper()
    if onay != 'E':
        print("İşlem iptal edildi.")
        return

    # Tüm ay kayıtlarında işten çıkma bilgisini güncelle
    for k in kayitlar:
        k["aktif"] = False
        k["isten_cikma_tarihi"] = tarih

    if save_data(data):
        print("Personel başarıyla işten çıkarıldı.")
    else:
        print("HATA: Veri kaydedilemedi!")


def personel_duzenle():
    """Personel bilgilerini düzenle"""
    data = load_data()

    # Personel listesini göster ve seçim yap
    print("\n--- Personel Düzenleme ---")
    calisan_ids = personel_listele(data)
    if not calisan_ids:
        return

    try:
        secim = input("\nDüzenlenecek personel numarasını girin: ").strip()
        if not secim:
            print("Geçersiz seçim!")
            return

        secim = int(secim)
        if 1 <= secim <= len(calisan_ids):
            calisan_id = calisan_ids[secim - 1]
        else:
            print("Geçersiz seçim!")
            return
    except ValueError:
        print("Geçersiz giriş!")
        return

    kayitlar = get_personel_info(data, calisan_id)
    if not kayitlar:
        print("Bu ID'ye ait personel yok.")
        return

    print(f"\nDüzenlenecek personel: {kayitlar[0]['ad_soyad']}")
    print("1. Ad Soyad düzenle")
    print("2. Maaş bilgilerini düzenle")
    print("3. İşe geri al (pasif personeller için)")

    try:
        secim = input("Seçiminiz: ").strip()
        if not secim:
            print("Geçersiz seçim!")
            return

        secim = int(secim)
    except ValueError:
        print("Geçersiz seçim!")
        return

    if secim == 1:
        yeni_ad = input("Yeni Ad Soyad: ").strip()
        if yeni_ad:
            for k in kayitlar:
                k["ad_soyad"] = yeni_ad
            print("Ad Soyad güncellendi.")
    elif secim == 2:
        # Tüm aylar için maaş bilgisi güncelle
        yeni_maas = input_float("Yeni Brüt Maaş (₺): ", min_value=0)
        for k in kayitlar:
            if k.get('durum') != 'KAPATILDI':  # Sadece kapatılmamış ayları güncelle
                k["brut_maas"] = yeni_maas
        print("Maaş bilgileri güncellendi.")
    elif secim == 3:
        if personel_aktif_mi(data, calisan_id):
            print("Personel zaten aktif.")
        else:
            for k in kayitlar:
                k["aktif"] = True
                k["isten_cikma_tarihi"] = None
            print("Personel tekrar işe alındı.")
    else:
        print("Geçersiz seçim!")
        return

    if not save_data(data):
        print("HATA: Veri kaydedilemedi!")


def aylik_rapor_al():
    """Aylık rapor al"""
    data = load_data()

    while True:
        ay = input("Rapor alınacak ay (örn: 2025-08) veya geçerli ay için ENTER: ").strip()
        if not ay:
            ay = get_current_month()

        if validate_month(ay):
            break
        else:
            print("Geçersiz ay formatı! Örnek: 2025-08")

    print(f"\n{ay} ayı için personel raporları:")
    print("=" * 80)

    toplam_net_maas = 0
    toplam_kesinti = 0
    toplam_brut_maas = 0
    rapor_verileri = []

    for calisan_id, kayitlar in data.items():
        # Bu ayın kaydını bul
        ay_kaydi = None
        for kayit in kayitlar:
            if kayit['ay'] == ay:
                ay_kaydi = kayit
                break

        if ay_kaydi:
            if ay_kaydi.get('hesaplama'):
                rapor_verileri.append({
                    'ad_soyad': ay_kaydi['ad_soyad'],
                    'id': calisan_id,
                    'net_maas': ay_kaydi['hesaplama']['net_maas'],
                    'kesinti': ay_kaydi['hesaplama']['izinli_kesinti'] +
                               ay_kaydi['hesaplama']['devamsiz_kesinti'] +
                               ay_kaydi['hesaplama']['saatlik_kesinti'],
                    'durum': ay_kaydi.get('durum', 'KAPATILMAMIŞ'),
                    'brut_maas': ay_kaydi['brut_maas']
                })
            else:
                rapor_verileri.append({
                    'ad_soyad': ay_kaydi['ad_soyad'],
                    'id': calisan_id,
                    'net_maas': 0,
                    'kesinti': 0,
                    'durum': 'KAPATILMAMIŞ',
                    'brut_maas': ay_kaydi['brut_maas']
                })

    # Raporları sırala ve göster
    for veri in sorted(rapor_verileri, key=lambda x: x['ad_soyad']):
        print(f"{veri['ad_soyad']} ({veri['id']}):")
        if veri['durum'] == 'KAPATILDI':
            print(f"  Net Maaş: {veri['net_maas']}₺")
            print(f"  Kesintiler: {veri['kesinti']}₺")
        else:
            print("  Bu ay henüz kapatılmamış")
        print(f"  Durum: {veri['durum']}")
        print("-" * 40)

        if veri['durum'] == 'KAPATILDI':
            toplam_net_maas += veri['net_maas']
            toplam_kesinti += veri['kesinti']
        toplam_brut_maas += veri['brut_maas']

    print(f"\n{ay} ayı toplamları:")
    print(f"Toplam Brüt Maaş: {toplam_brut_maas}₺")
    print(f"Toplam Kesinti: {toplam_kesinti}₺")
    print(f"Toplam Net Maaş: {toplam_net_maas}₺")
    print("=" * 80)


def yedekleri_yonet():
    """Yedek yönetimi"""
    print("\n--- Yedek Yönetimi ---")
    print("1. Yedek oluştur")
    print("2. Yedekten geri yükle")
    print("3. Yedekleri listele")
    print("0. İptal")

    try:
        secim = input("Seçiminiz: ").strip()
        if not secim:
            print("Geçersiz seçim!")
            return

        secim = int(secim)
    except ValueError:
        print("Geçersiz seçim!")
        return

    if secim == 1:
        if create_backup():
            print("Yedek başarıyla oluşturuldu.")
        else:
            print("Yedek oluşturulamadı!")
    elif secim == 2:
        data = restore_backup()
        if data:
            print("Yedekten geri yükleme başarılı.")
        else:
            print("Yedekten geri yükleme başarısız!")
    elif secim == 3:
        if not os.path.exists(BACKUP_FOLDER):
            print("Yedek klasörü bulunamadı!")
            return

        backups = [f for f in os.listdir(BACKUP_FOLDER) if f.endswith('.json')]
        if not backups:
            print("Yedek dosyası bulunamadı!")
            return

        print("Mevcut yedekler:")
        for i, backup in enumerate(sorted(backups, reverse=True), 1):
            try:
                dosya_boyutu = os.path.getsize(os.path.join(BACKUP_FOLDER, backup))
                print(f"{i}. {backup} ({dosya_boyutu} byte)")
            except:
                print(f"{i}. {backup}")
    elif secim == 0:
        return
    else:
        print("Geçersiz seçim!")


def main():
    """Ana menü"""
    # Yedek klasörünü oluştur
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

    while True:
        print("\n--- Maaş & Puantaj Sistemi ---")
        print("1. Eksik günleri gir veya puantajı devam ettir")
        print("2. Ayı kapat ve hesaplama yap")
        print("3. Kayıt görüntüle")
        print("4. Personel işten çıkar")
        print("5. Personel düzenle")
        print("6. Aylık rapor al")
        print("7. Yedek yönetimi")
        print("8. Çıkış")

        secim = input("Seçiminiz: ").strip()

        if secim == "1":
            puantaj_girisi_veya_devam()
        elif secim == "2":
            ay_hesapla_ve_kapat()
        elif secim == "3":
            kayit_goruntule()
        elif secim == "4":
            personel_isten_cikar()
        elif secim == "5":
            personel_duzenle()
        elif secim == "6":
            aylik_rapor_al()
        elif secim == "7":
            yedekleri_yonet()
        elif secim == "8":
            print("Çıkış yapılıyor...")
            break
        else:
            print("Geçersiz seçim!")

        # Her işlemden sonra bekle
        input("\nDevam etmek için ENTER'a basın...")
        clear_console()


if __name__ == "__main__":
    main()
