Nama  : Naira Al Humayda

NPM   : 2506532233

Kelas : PBP E

## TUGAS 2

-- AI Disclosure --

Dalam pengerjaan Tugas 2, saya menggunakan ChatGPT sebagai bantuan belajar dan debugging. 
ChatGPT membantu menjelaskan konsep MVT Django, memberikan arahan mengenai implementasi 
model, view, URL, template, serta membantu mengecek dan memperbaiki error pada kode.

Implementasi kode, pengisian data project, pengujian aplikasi, dan pengecekan hasil akhir 
tetap saya lakukan sendiri.

1. USER
    |   -> Request pertama kali diproses oleh URL configuration utama pada 'portofolio/urls.py'
    PORTOFOLIO/URLS.PY
    |   -> URL diarahkan ke URL configuration pada app 'main' melalui 'main/urls.py'
    MAIN/URLS.PY
    |   -> route `projects/` diarahkan ke fungsi `show_projects` pada `main/views.py`
    SHOW_PROJECT()
    |   -> Database diambil menggunakan `Project.objects.all()` dan memasukkannya ke dalam context dengan nama `project_list`.
    PROJECT.OBJECT.ALL()
    |   -> View merender template `projects.html` dengan context tersebut.
    PROJECT.HTML
    |   -> Memunculkan ke Browser
    BROWSER

    Peran masing-masing komponen adalah:
    - `portofolio/urls.py`: mengatur URL utama project dan mengarahkan request ke app.
    - `main/urls.py`: menentukan URL pada app dan view yang menangani request tersebut.
    - `views.py`: memproses request, mengambil data dari model, dan mengirimkannya ke template.
    - `models.py`: mendefinisikan struktur data project yang disimpan dalam database.
    - `projects.html`: menampilkan data yang diberikan oleh view kepada pengguna.

2.  Data portfolio sebaiknya disimpan pada Model/database daripada langsung ditulis
    di dalam template karena data portfolio dapat berubah dan bertambah, sedangkan
    struktur tampilan tidak selalu perlu berubah.

    Pada project ini, data project seperti title, description, tech stack, GitHub URL,
    dan year disimpan pada model `Project`. View kemudian mengambil data tersebut
    menggunakan `Project.objects.all()` dan mengirimkannya ke template melalui
    context.

    Dengan pendekatan ini, ketika ingin menambahkan atau mengubah project, data
    dapat diubah pada database tanpa perlu mengubah struktur HTML. Hal ini membuat
    maintenance menjadi lebih mudah dan template menjadi lebih reusable. Jika jumlah
    project bertambah, template yang sama tetap dapat digunakan karena data
    ditampilkan menggunakan loop Django Template Language.

    Sebaliknya, jika data ditulis langsung pada template, setiap penambahan atau
    perubahan project mengharuskan developer mengubah file HTML secara manual.
    Semakin banyak data yang dimiliki, cara tersebut akan membuat maintenance dan
    pengembangan menjadi lebih sulit.

3.  `makemigrations` digunakan untuk membuat file migration berdasarkan perubahan
    pada Model Django. File tersebut berisi instruksi mengenai perubahan struktur
    database yang perlu dilakukan.

    Sementara itu, `migrate` digunakan untuk menerapkan migration yang sudah dibuat
    ke database sehingga struktur database benar-benar berubah.

    Contohnya pada Tugas 2 ini, setelah menambahkan model `Project` pada
    `main/models.py`, saya menjalankan `python manage.py makemigrations`. Django
    kemudian membuat file `main/migrations/0002_project.py` yang berisi migration
    untuk model `Project`. Setelah itu saya menjalankan `python manage.py migrate`
    untuk menerapkan migration tersebut ke database.

    Dengan demikian, `makemigrations` dapat dianggap sebagai proses membuat
    rencana perubahan database, sedangkan `migrate` merupakan proses menerapkan
    rencana tersebut ke database.

