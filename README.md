# Naira Al Humayda - Personal Portfolio

Website portofolio pribadi yang dibuat menggunakan Django untuk menampilkan profil, pengalaman, dan proyek yang pernah dikerjakan.

## Deskripsi Proyek

Website ini dikembangkan sebagai bagian dari mata kuliah Pemrograman Berbasis Platform (PBP).

Website memiliki beberapa bagian utama:

- Profile
- Experience
- Projects
- About Me

Pada Individual Assignment 3, bagian Experience dikembangkan dengan fitur pengelolaan data menggunakan Django ModelForm dan JSON Data Delivery.

## Fitur Utama

### Profile

Menampilkan informasi singkat mengenai diri dan latar belakang pendidikan.

### Projects

- Menampilkan daftar proyek.
- Menambahkan proyek melalui form.
- Menghapus proyek.
- Menyediakan data proyek dalam format JSON.
- Pencarian proyek berdasarkan judul.

### Experience

- Menampilkan daftar pengalaman.
- Menambahkan pengalaman menggunakan ModelForm.
- Mengubah pengalaman menggunakan Update Form.
- Menghapus pengalaman.
- Menyediakan data pengalaman dalam format JSON.
- Melakukan deserialisasi JSON sebelum data ditampilkan.
- Pencarian pengalaman berdasarkan nama pengalaman.
- Konfirmasi sebelum menghapus data.

### UI/UX

- Template inheritance menggunakan `base.html`.
- Expandable navigation menu.
- Responsive layout.
- Card-based interface.
- Hover interaction pada card Projects dan Experience.
- About card dibuat sebagai informasi statis dan tidak menggunakan hover interaction.
- Form validation dan feedback message.

---

## Teknologi

- Python
- Django
- HTML5
- CSS3
- SQLite
- Git & GitHub

---

## Cara Menjalankan Project

### 1. Clone repository

```bash
git clone <URL_REPOSITORY>
cd myportofolio

### 2. Buat dan Aktifkan Virtual Environment
## Windows PowerShell
python -m venv env
.\env\Scripts\Activate.ps1
##dgn Command Prompt
env\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Jalankan migration
python manage.py migrate

### 5. Jalankan development server
python manage.py runserver

### Kemudian Buka
http://127.0.0.1:8000/

#TUGAS 3

1. ModelForm digunakan karena form dapat dibuat berdasarkan model Django secara langsung. Dengan ModelForm, field dan validasi dapat mengikuti struktur model sehingga tidak perlu membuat seluruh form HTML secara manual.

Pada tugas ini, ExperienceForm dibuat berdasarkan model Experience. Field yang dapat diisi pengguna didefinisikan melalui Meta.fields, sedangkan field seperti id tidak perlu dimasukkan secara manual.

{% csrf_token %} digunakan untuk memberikan token keamanan pada form yang melakukan request ke server. Token tersebut membantu Django memastikan bahwa request POST berasal dari halaman yang valid dan membantu mencegah serangan Cross-Site Request Forgery (CSRF)

2.JSON memiliki struktur yang relatif sederhana dan lebih ringkas sehingga mudah dibaca oleh manusia maupun diproses oleh program.

JSON juga menggunakan struktur key-value dan array yang sesuai dengan struktur data yang umum digunakan dalam aplikasi web. Karena itu, JSON banyak digunakan untuk pertukaran data antara server dan client, terutama dalam API.

XML memiliki kemampuan representasi data yang kuat, tetapi sintaksnya cenderung lebih verbose karena menggunakan tag pembuka dan penutup. Untuk kebutuhan data delivery pada project ini, JSON lebih praktis karena struktur datanya sederhana dan mudah diproses.

3. Pada project ini, data Experience pertama-tama diambil dari database menggunakan Django ORM.

Data tersebut kemudian diproses oleh fungsi get_experiences_json(). Karena object yang diperoleh dari Django ORM merupakan object Python/Django, data tersebut perlu diubah menjadi format yang dapat dikirim sebagai JSON.

Proses tersebut dilakukan menggunakan Django serializer:

'serializers.serialize("json", experiences)'

Hasil serialization kemudian dikembalikan melalui HttpResponse dengan content type application/json.

Pada halaman Experience, view show_experience() mengambil response JSON tersebut dan melakukan deserialization:

'serializers.deserialize(

    "json",

    json_response.content.decode("utf-8"),

)'

Object hasil deserialization kemudian digunakan untuk menampilkan data Experience pada template.

Serialization diperlukan karena object model Django tidak dapat langsung dikirim sebagai JSON. Serialization mengubah data model menjadi representasi data yang dapat dikirim dan diproses sebagai JSON.

#PROSES MINGGUAN

Tutorial 03

-Menggunakan template inheritance.

-Membuat form untuk Project.

-Menambahkan fitur create dan delete Project.

-Membuat JSON endpoint untuk Project.

-Menambahkan pencarian dan interaksi pada halaman Project.

Individual Assignment 3

-Membuat ExperienceForm.

-Menambahkan Create Experience.

-Menambahkan Update Experience.

-Menambahkan Delete Experience.

-Menambahkan JSON Data Delivery untuk Experience.

-Menambahkan deserialization sebelum data ditampilkan.

-Melakukan refactoring template agar menggunakan base.html.

-Menambahkan search pada Experience.

-Meningkatkan UI/UX melalui card layout, navigation menu, responsive styling, dan delete confirmation.

#AI Disclosure

Dalam proses pengembangan project ini, saya menggunakan ChatGPT sebagai supporting tool untuk membantu memahami konsep, melakukan debugging, mengevaluasi struktur implementasi, serta memberikan saran mengenai UI/UX.

AI digunakan terutama untuk:

membantu memahami implementasi ModelForm dan CRUD pada Django;

membantu debugging error pada URL, view, dan template;

memberikan contoh struktur implementasi JSON serialization dan deserialization;

memberikan saran struktur HTML dan CSS;

memberikan masukan mengenai responsive layout dan UI/UX.

Implementasi akhir tetap saya kerjakan, sesuaikan, dan uji pada project saya sendiri. Saran dari AI tidak langsung digunakan tanpa pengecekan karena beberapa contoh yang diberikan AI mengikuti struktur tutorial dan perlu disesuaikan dengan model, field, URL, dan desain yang sudah ada pada project.

Salah satu keterbatasan yang saya temukan adalah AI terkadang memberikan implementasi berdasarkan asumsi struktur model atau template yang berbeda dari project saya. Karena itu, saya perlu memeriksa kembali field model, URL pattern, template inheritance, dan hasil running website secara manual sebelum menggunakan solusi tersebut.

Pada tahap UI/UX, saya juga melakukan penyesuaian manual terhadap layout, warna, ukuran card, navigation menu, hover interaction, responsive behavior, serta struktur halaman agar sesuai dengan desain portfolio yang saya inginkan.
