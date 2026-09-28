### Tugas 4

Implementasi Tugas 4 mencakup:
- Register, login, dan logout.
- Session dan cookie last_login.
- Role Visitor, Regular User, Editor, dan Superuser.
- Server-side authorization dengan HTTP 403 untuk aksi yang tidak diizinkan.
- Editor menggunakan Django Group.
- Fitur star/unstar menggunakan ManyToManyField.
- API Projects tetap tersedia tanpa mengekspos informasi sensitif.

#### Refleksi
Pada Tugas 4, saya mempelajari perbedaan authentication dan authorization
serta bagaimana Django dapat digunakan untuk membatasi akses berdasarkan
role pengguna. Saya juga mempelajari penggunaan Group untuk membuat role
Editor, PermissionDenied untuk membatasi akses di server, dan
ManyToManyField untuk menyimpan hubungan antara user dan project melalui
fitur star.

Saya menggunakan AI sebagai alat bantu untuk memahami konsep Django
authentication, authorization, ManyToManyField, debugging error,
dan pengembangan template. Seluruh kode disesuaikan dan diuji kembali
secara manual pada project.