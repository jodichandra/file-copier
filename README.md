# 📁 File Copier - WinSCP Style

Aplikasi desktop sederhana berbasis **Python + Tkinter** untuk meng-copy file dari
**folder sumber** ke **folder tujuan** dengan **struktur folder otomatis** — 
mirip tampilan WinSCP dengan 2 panel.

Cocok untuk update project (PHP, Laravel, CodeIgniter, dll) tanpa harus 
drag-drop manual atau bikin folder satu-satu.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![License](https://img.shields.io/badge/License-Unlicense-green)

---

## ✨ Fitur

- 🪟 **Tampilan 2 panel** (kiri = sumber, kanan = tujuan) seperti WinSCP
- 📁 **Struktur folder otomatis** — kirim `Auth.php` dari `application\libraries`, di tujuan otomatis dibuat `application\libraries\Auth.php`
- 🎨 **Warna jelas** — folder kuning, file putih, striping baris, header kolom
- 📋 **Kolom lengkap**: Name, Size, Type, Changed
- 🔍 **Pencarian / filter** di kedua panel (realtime)
- 🗑️ **Klik kanan di folder tujuan** → Hapus file/folder (dengan konfirmasi)
- 📜 **Log pengiriman** — tampil dari folder mana → ke folder mana
- 💾 **Simpan config otomatis** — root sumber/tujuan & folder terakhir diingat saat aplikasi dibuka lagi
- ⚡ **Multi-select** — kirim/hapus banyak file sekaligus
- 🚀 **Copy thread** — progress bar, UI tidak nge-freeze
- 🧩 **Build jadi EXE** — bisa dipakai di komputer tanpa Python

---

## 🖼️ Screenshot

*(ganti dengan screenshot Anda sendiri)*

```
┌────────────────────────────────────────────────────────────┐
│ Root Sumber: C:\laragon\www\project                   │
│ Root Tujuan: D:\PROJECT UPDATE                               │
├────────────────────────┬───────────────────────────────────┤
│ SUMBER                 │ TUJUAN                            │
│ C:\...\controllers\... │ D:\PROJECT UPDATE                   │
│ [⬆Up][⟳Refresh]        │ [⬆Up][⟳Refresh]                   │
│ 🔍 [admin_______][✕]   │ 🔍 [___________][✕]               │
│ 📁 ..                  │ 📁 application                    │
│ 📁 front               │                                   │
│ 📄 Admin.php           │                                   │
│ 📄 Antrol.php          │                                   │
├────────────────────────┴───────────────────────────────────┤
│ [═════════════════════════════════════════════════] 100%   │
│ Selesai. 2 file berhasil dicopy.                           │
│ 📜 LOG PENGIRIMAN FILE                          [🗑 Bersihkan]│
│ [14:25:01] 📤 KIRIM FILE — 2026-10-15 14:25:01             │
│ [14:25:01]    Dari  : C:\laragon\www\project          │
│ [14:25:01]    Ke    : D:\PROJECT UPDATE                      │
│ [14:25:01] ✔ [1/2] Auth.php                                │
│ [14:25:01]      FROM: C:\...\application\libraries         │
│ [14:25:01]      TO  : D:\PROJECT UPDATE\...\libraries        │
└────────────────────────────────────────────────────────────┘
```

---

## 🚀 Cara Menggunakan

### A. Menjalankan dari Source Code (Python)

**Prasyarat:**
- Python 3.8 atau lebih baru → [download di sini](https://www.python.org/downloads/)
- Saat install, centang ✅ **"Add Python to PATH"**

**Langkah:**

```bash
# 1. Clone repository
git clone https://github.com/USERNAME/FileCopier.git
cd FileCopier

# 2. Jalankan aplikasi
python file_copier.py
```

Tidak butuh `pip install` apa pun — hanya pakai library bawaan Python (Tkinter).

> 💡 **Linux/Mac:** ganti perintah jadi `python3 file_copier.py`
> dan install Tkinter dulu kalau belum ada:
> - Ubuntu/Debian: `sudo apt install python3-tk`
> - macOS: sudah bawaan via Homebrew Python

### B. Menjalankan dari EXE (Windows)

1. Download `FileCopier.exe` dari halaman [**Releases**](../../releases)
2. **Klik 2×** untuk menjalankan
3. Kalau Windows Defender protes → klik *More info* → *Run anyway*

---

## 📖 Panduan Pemakaian

### 1️⃣ Set Root Sumber dan Root Tujuan

- **Root Sumber** = folder **pangkal** dari struktur yang mau di-copy.
- **Root Tujuan** = folder tempat struktur akan **dibentuk ulang**.

**Contoh:**
| | Path |
|---|---|
| Root Sumber | `C:\laragon\www\project` |
| Root Tujuan | `D:\PROJECT UPDATE` |

### 2️⃣ Kirim File

1. Di panel **kiri**, navigasi ke folder yang berisi file yang mau dikirim
   - **Double-click** folder → masuk
   - **⬆ Up** → naik satu level
2. **Klik kanan** file (bisa pilih banyak pakai Ctrl/Shift)
3. Pilih **📤 Kirim ke Folder Tujuan**
4. Konfirmasi → tunggu progress bar selesai

### 3️⃣ Hasil Struktur Otomatis

Kalau Anda kirim `Auth.php` dari:
```
Root Sumber = C:\laragon\www\project
Folder saat ini = C:\laragon\www\project\application\libraries
```

Maka di tujuan akan terbentuk:
```
D:\PROJECT UPDATE\application\libraries\Auth.php
```

**Perhatikan:** struktur `application\libraries\` dibuat **otomatis**,
walau di folder tujuan belum ada.

### 4️⃣ Hapus File di Tujuan

Kalau file tidak jadi dipindahkan:
1. **Klik kanan** file di panel **kanan** (TUJUAN)
2. Pilih **🗑 Hapus File/Folder**
3. Konfirmasi → file dihapus permanen

> ⚠️ File yang dihapus **TIDAK masuk Recycle Bin**. Hati-hati!

### 5️⃣ Cari File

- Ketik di kotak **🔍** di atas panel → hasil langsung terfilter
- Klik **✕** untuk reset

### 6️⃣ Lihat Log

Panel bawah menampilkan **riwayat lengkap**:
- Kapan dikirim
- Dari folder mana → ke folder mana
- Berhasil / gagal

Klik **🗑 Bersihkan Log** untuk reset log.

---

## 🔧 Build Sendiri jadi EXE

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Build 1 file EXE
pyinstaller --onefile --windowed --name "FileCopier" --clean file_copier.py

# 3. Hasil ada di folder dist/FileCopier.exe
```

Atau **double-click** `build.bat` (kalau sudah tersedia).

**Opsi build tambahan:**

| Opsi | Fungsi |
|---|---|
| `--icon app.ico` | Pakai icon custom (harus `.ico`) |
| `--onefile` | Hasil 1 file `.exe` |
| `--windowed` | Sembunyikan console hitam |
| `--upx-dir C:\upx` | Kompres pakai UPX (ukuran lebih kecil) |

---

## 📂 Dimana Config Disimpan?

Config otomatis disimpan di:
```
C:\Users\<NamaUser>\.file_copier_config.json
```

Isinya:
```json
{
  "source_root": "C:/laragon/www/project",
  "dest_root": "D:/PROJECT UPDATE",
  "source_current": "C:/laragon/www/project/application/controllers/admin",
  "dest_current": "D:/PROJECT UPDATE/application",
  "last_saved": "2026-10-15 14:25:01"
}
```

Klik **🗑 Reset Config** di aplikasi kalau ingin menghapusnya.

---

## 🛠️ Troubleshooting

| Masalah | Solusi |
|---|---|
| `python: command not found` | Install Python & centang "Add to PATH" |
| Icon emoji tampil kotak-kotak | Update Windows / install Segoe UI Emoji |
| Windows Defender blokir EXE | Klik *More info* → *Run anyway*, atau whitelist folder |
| EXE jalan tapi langsung tertutup | Build tanpa `--windowed` untuk lihat error |
| Folder tujuan tidak dibuat | Pastikan **Root Tujuan** sudah di-set dan punya izin tulis |

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah **The Unlicense** — 
**bebas pakai untuk apa saja**, termasuk komersial, tanpa perlu minta izin.

Lihat file [LICENSE](LICENSE) untuk detail.

Artinya:
- ✅ Boleh dipakai, dimodifikasi, dijual
- ✅ Boleh dipakai di proyek pribadi atau perusahaan
- ✅ Tidak wajib mencantumkan nama pembuat asli
- ❌ Tidak ada garansi apa pun

---

## 🤝 Kontribusi

Pull request & issue sangat diterima!

1. Fork repo ini
2. Buat branch: `git checkout -b fitur-baru`
3. Commit: `git commit -m "Tambah fitur X"`
4. Push: `git push origin fitur-baru`
5. Buka Pull Request

---

## ⭐ Dukungan

Kalau proyek ini bermanfaat, kasih ⭐ di GitHub ya!

---

Dibuat dengan ❤️ menggunakan Python + Tkinter.