Bana bir CV değerlendirme portalı (İşe Alım Takip Sistemi) yap. Proje Python ve Flask ile çalışmalı. 

İstediğim özellikler ve iş akışı şu şekilde:
1. Kullanıcı modern ve şık bir web arayüzünden PDF formatında CV yükleyebilsin.
2. Sistem bu PDF'in metnini çıkarsın.
3. Çıkan metni Gemini API'ye gönder. Gemini CV'yi analiz edip bana sadece tek bir JSON objesi dönsün. Objenin içinde: İsim, Email, Telefon, Yetenekler, Eğitim, Sınıflandırma, Puan (0-100 arası) ve yapay zekanın 2 cümlelik Özeti bulunsun.
4. Gemini "Sınıflandırma" kararı olarak adayın tecrübesine göre şu 3 seçenekten birini dönmeli: "işe alım", "mülakat" veya "deneme".
5. Gemini'den dönen bu verileri Google Sheets'te bir tabloya otomatik olarak kaydet.
6. Eğer işe alım olarak sınıflandırılmışsa Slackten mesaj yollasın.
7. Son olarak CV sunucudan silinsin ve adayın puanı, bilgileri, yapay zeka özeti yükleme ekranı yerinde aday bilgileri gösterilsin.

.env ve requirement.txt dosyası oluştur. Gerekli api keylerin olduğu değişkenleri ekle.
