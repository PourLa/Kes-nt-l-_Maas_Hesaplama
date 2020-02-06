from os import system

maaş_tutarı = int(input("Maaşınızı Giriniz:"))
ay_gun = int(input("Bu ay kaç gün:"))
gün = int(input("Kaç gün işe geldiniz:"))
gelınmeyen_gun = int(input("kaç gün izinli gelmediniz:"))
devamsız_gun = int(input("Kaç gün devamsızlık yaptınız:"))
saatlik_kesinti = int(input("Kaç saat kesintiniz var? yazınız:"))
izinsiz_saatlik_kesinti = int(input("İzinsiz Kaç saat kesintiniz var? yazınız:"))

"""system('cls') #windows için"""
system("clear") #linux tabanı için

#GÜNLÜK MAAŞ HESAPLAMA#

pazartesi_cuma = 9*5
cumartesi = 5
toplam_saat = pazartesi_cuma+cumartesi
toplam=toplam_saat/7
toplam_gun=ay_gun*toplam
net_tutar = maaş_tutarı/toplam_gun
günlük_maaş = net_tutar*toplam
günlük_net_maaş = günlük_maaş*gün

#İZİNLİ VEYA DEVAMSIZ KESİNTİLER#

ızınlı_maaş = gelınmeyen_gun*günlük_maaş
devamsız_maaş = (devamsız_gun*günlük_maaş)*2



#SAATLİK OLARAK KESİNTİLER#

saatlik = net_tutar*saatlik_kesinti
izinsiz_saatlik = net_tutar*izinsiz_saatlik_kesinti*2

#SONUÇ#

net_maaş=günlük_net_maaş-devamsız_maaş-saatlik-izinsiz_saatlik


print("{} gün izinli maaş kesinti tutarı:".format(gelınmeyen_gun),ızınlı_maaş)
print("{} gün devamsız maaş kesinti tutarı:".format(devamsız_gun),devamsız_maaş)
print("Normal {} saatlik kesinti tutarı:".format(saatlik_kesinti),saatlik)
print("İzinsiz {} saatlik kesinti tutarı:".format(izinsiz_saatlik_kesinti),izinsiz_saatlik)
print("\n Net Alacağı Maaş:",net_maaş)
