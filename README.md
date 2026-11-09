# MyPortofolio

Website portofolio berbasis **Django, DRF, HTML, CSS, dan JavaScript** untuk menampilkan profil, Projects, dan Experience.

## Fitur

- **Projects:** daftar, pencarian, CRUD, dan star (Tutorial 7).
- **Experience:** REST API CRUD, pencarian, star, modal tambah/edit, dan interaksi tanpa reload.
- **Fitur tambahan:** filter kategori, sorting, reset filter, toast, dan tampilan responsif.
- **Keamanan:** validasi serializer, permission empat peran, dan CSRF.

## Cara Menjalankan

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Jalankan pengujian dengan `python manage.py test main`.

## API Experience

Prefix: `/api/v1/experiences/`.

| Method | Endpoint | Akses |
|---|---|---|
| GET / POST | `/` | Baca publik; tambah superuser |
| GET / PUT / PATCH / DELETE | `/<uuid>/` | Baca publik; edit Editor/superuser; hapus superuser |
| POST | `/<uuid>/star/` | Pengguna login |

Pencarian, filter, dan sorting menggunakan parameter `title`, `category`, dan `ordering`.

## Refleksi Tugas 6

1. **REST:** JSON merupakan format data, sedangkan REST juga mengatur resource, HTTP method, dan status respons. PUT memperbarui seluruh data, PATCH hanya bagian tertentu.
2. **Serializer:** memvalidasi input, mengatur field API, dan melindungi field perhitungan agar *read-only*.
3. **Permission:** autentikasi memastikan identitas pengguna; otorisasi menentukan tindakan yang boleh dilakukan. Pengecekan harus ada di server.
4. **CSRF:** pada `SessionAuthentication`, request yang mengubah data memerlukan perlindungan CSRF agar sesi pengguna tidak disalahgunakan.

## Penggunaan AI

Saya menggunakan **ChatGPT** untuk membantu memahami DRF, serializer, permission, API, debugging, dan merapikan kode serta dokumentasi. Kode yang digunakan disesuaikan dengan kebutuhan proyek dan diuji kembali secara manual.

## Pengumpulan

- **Repository:** https://github.com/nairalhmyda/myportofolio