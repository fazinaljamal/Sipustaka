from django.shortcuts import render,redirect
from django.db import connection
from django.contrib import messages
from datetime import date, timedelta



def dictfetchone(cursor):
    row = cursor.fetchone()

    if row is None:
        return None

    columns = [col[0] for col in cursor.description]

    return dict(zip(columns,row))

def dashboard(request):
    with connection.cursor() as cursor:
        # Total Buku (keseluruhan unit)
        cursor.execute("SELECT COALESCE(SUM(stok), 0) FROM buku")
        total_buku = cursor.fetchone()[0]
        
        # Total Judul (jumlah koleksi judul buku)
        cursor.execute("SELECT COUNT(*) FROM buku")
        total_judul = cursor.fetchone()[0]
        
        # Sedang Dipinjam (transaksi peminjaman aktif)
        cursor.execute("""
            SELECT COUNT(*) FROM peminjaman 
            WHERE status = 'Dipinjam'
        """)
        sedang_dipinjam = cursor.fetchone()[0]
        
        # Sudah Dikembalikan (transaksi yang sudah selesai)
        cursor.execute("""
            SELECT COUNT(*) FROM peminjaman 
            WHERE status = 'Dikembalikan'
        """)
        sudah_dikembalikan = cursor.fetchone()[0]
        

        cursor.execute("""
            SELECT judul, stok 
            FROM buku 
            ORDER BY stok DESC
        """)
        distribusi_stok = cursor.fetchall()
        
        # Status Peminjaman (ringkasan transaksi)
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM peminjaman 
            GROUP BY status
        """)
        status_peminjaman = cursor.fetchall()
    
    context = {
        'total_buku': total_buku,
        'total_judul': total_judul,
        'sedang_dipinjam': sedang_dipinjam,
        'sudah_dikembalikan': sudah_dikembalikan,
        'distribusi_stok': distribusi_stok,
        'status_peminjaman': status_peminjaman,
    }
    return render(request, 'dashboard.html', context)

def buku_list(request):
    with connection.cursor() as cursor:
        cursor.execute(""" SELECT id,judul,pengarang,kategori,penerbit,tahun_terbit,rak,stok,deskripsi FROM buku""")

        buku = cursor.fetchall()

    return render(
        request,
        'buku/list.html',
        {
            'buku_list': buku
        }
    )

def buku_detail(request, id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM buku
            WHERE id = %s
            """,
            [id]
        )
        buku = dictfetchone(cursor)    

    return render(request, 'buku/detail.html', {
        'buku': buku,
    })

def buku_create(request):
    if request.method == 'POST':

        judul = request.POST.get('judul')
        pengarang = request.POST.get('pengarang')
        kategori = request.POST.get('kategori')
        penerbit = request.POST.get('penerbit')
        tahun_terbit = request.POST.get('tahun_terbit')
        rak = request.POST.get('rak')
        stok = request.POST.get('stok')
        deskripsi = request.POST.get('deskripsi')


        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO buku
                (judul, pengarang,kategori,penerbit,tahun_terbit,rak,stok,deskripsi)

                VALUES (%s, %s, %s, %s, %s, %s, %s,  %s)
                """,
                [judul, pengarang,kategori,penerbit,tahun_terbit,rak,stok,deskripsi]
            )

        return redirect('buku_list')

    return render(request, 'buku/create.html')


def buku_update(request, id):

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM buku
            WHERE id = %s
            """,
            [id]
        )

        buku = dictfetchone(cursor)


    if request.method == 'POST':

        judul = request.POST.get('judul')
        pengarang = request.POST.get('pengarang')
        kategori = request.POST.get('kategori')
        penerbit = request.POST.get('penerbit')
        tahun_terbit = request.POST.get('tahun_terbit')
        rak = request.POST.get('rak')
        stok = request.POST.get('stok')
        deskripsi = request.POST.get('deskripsi')


        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE buku SET
                judul=%s,
                pengarang=%s,
                kategori=%s,
                penerbit=%s,
                tahun_terbit=%s,
                rak=%s,
                stok=%s,
                deskripsi=%s
                WHERE id=%s
                """,
                [
                    judul,
                    pengarang,
                    kategori,
                    penerbit,
                    tahun_terbit,
                    rak,
                    stok,
                    deskripsi,
                    id
                ]
            )

        return redirect('buku_list')


    return render(
        request,
        'buku/update.html',
        {
            'buku': buku
        }
    )

def buku_delete(request, id):

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM buku
            WHERE id = %s
            """,
            [id]
        )

        buku = dictfetchone(cursor)


    if request.method == 'POST':

        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM buku
                WHERE id = %s
                """,
                [id]
            )


        return redirect('buku_list')


    return render(
        request,
        'buku/delete.html',
        {
            'buku': buku
        }
    )

def peminjaman_list(request):
    today = date.today()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.id,
                s.nama as siswa_nama,
                b.judul as buku_judul,
                p.tanggal_pinjam,
                p.jatuh_tempo,
                p.status,
                p.keperluan
            FROM peminjaman p
            JOIN siswa s ON p.siswa_id = s.id
            JOIN buku b ON p.buku_id = b.id
            ORDER BY p.tanggal_pinjam DESC
        """)
        peminjaman_list = cursor.fetchall()
    
    return render(request, 'peminjaman/list.html', {
        'peminjaman_list': peminjaman_list,
        'today': today
    })

def peminjaman_create(request):
    with connection.cursor() as cursor:
        # Ambil daftar siswa untuk dropdown
        cursor.execute("SELECT id, nama, kelas, nis FROM siswa ORDER BY nama")
        siswa_list = cursor.fetchall()
        
        # Ambil daftar buku untuk dropdown
        cursor.execute("""
            SELECT id, judul, stok 
            FROM buku 
            WHERE stok > 0 
            ORDER BY judul
        """)
        buku_list = cursor.fetchall()
    
    if request.method == 'POST':
        siswa_id = request.POST.get('siswa_id')
        buku_id = request.POST.get('buku_id')
        tanggal_pinjam = request.POST.get('tanggal_pinjam')
        jatuh_tempo = request.POST.get('jatuh_tempo')
        keperluan = request.POST.get('keperluan', '')
        
        # Validasi
        if not all([siswa_id, buku_id, tanggal_pinjam, jatuh_tempo]):
            messages.error(request, 'Semua field wajib diisi!')
            return redirect('peminjaman_create')
        
        # Validasi stok buku
        with connection.cursor() as cursor:
            cursor.execute("SELECT stok FROM buku WHERE id = %s", [buku_id])
            stok = cursor.fetchone()
            
            if stok and stok[0] > 0:
                # Kurangi stok buku
                cursor.execute("UPDATE buku SET stok = stok - 1 WHERE id = %s", [buku_id])
                
                # Insert data peminjaman
                cursor.execute("""
                    INSERT INTO peminjaman (
                        siswa_id, buku_id, tanggal_pinjam, jatuh_tempo, 
                        keperluan, status
                    ) VALUES (%s, %s, %s, %s, %s, 'Dipinjam')
                """, [siswa_id, buku_id, tanggal_pinjam, jatuh_tempo, keperluan])
                
                messages.success(request, 'Peminjaman berhasil ditambahkan!')
                return redirect('peminjaman_list')
            else:
                messages.error(request, 'Stok buku tidak mencukupi!')
    
    context = {
        'siswa_list': siswa_list,
        'buku_list': buku_list,
        'today': date.today().strftime('%Y-%m-%d'),
        'default_jatuh_tempo': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
    }
    return render(request, 'peminjaman/create.html', context)

def peminjaman_kembalikan(request, id):
    with connection.cursor() as cursor:
        # Ambil data peminjaman
        cursor.execute("""
            SELECT 
                p.id,
                s.nama as siswa_nama,
                s.kelas,
                b.judul as buku_judul,
                p.tanggal_pinjam,
                p.jatuh_tempo,
                p.status,
                p.keperluan
            FROM peminjaman p
            JOIN siswa s ON p.siswa_id = s.id
            JOIN buku b ON p.buku_id = b.id
            WHERE p.id = %s
        """, [id])
        peminjaman = cursor.fetchone()
        
        if not peminjaman:
            messages.error(request, 'Data peminjaman tidak ditemukan!')
            return redirect('peminjaman_list')
        
        if peminjaman[6] == 'Dikembalikan':
            messages.warning(request, 'Buku ini sudah dikembalikan!')
            return redirect('peminjaman_list')
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Update status peminjaman
            cursor.execute("""
                UPDATE peminjaman 
                SET status = 'Dikembalikan'
                WHERE id = %s
            """, [id])
            
            # Tambah stok buku
            cursor.execute("""
                UPDATE buku 
                SET stok = stok + 1 
                WHERE id = (SELECT buku_id FROM peminjaman WHERE id = %s)
            """, [id])
        
        messages.success(request, f'Buku "{peminjaman[3]}" berhasil dikembalikan!')
        return redirect('peminjaman_list')
    
    context = {
        'peminjaman': peminjaman,
        'today': date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'peminjaman/kembalikan.html', context)

def user_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM siswa ORDER BY id")
        user_list = cursor.fetchall()
    return render(request, 'user/list.html', {'user_list': user_list})

def user_detail(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM siswa WHERE id = %s", [id])
        user = cursor.fetchone()
        
        # Hitung total peminjaman user
        cursor.execute("""
            SELECT COUNT(*) FROM peminjaman 
            WHERE siswa_id = %s
        """, [id])
        total_peminjaman = cursor.fetchone()[0]
        
        # Hitung peminjaman aktif (belum dikembalikan)
        cursor.execute("""
            SELECT COUNT(*) FROM peminjaman 
            WHERE siswa_id = %s AND status = 'Dipinjam'
        """, [id])
        peminjaman_aktif = cursor.fetchone()[0]
        
    context = {
        'user': user,
        'total_peminjaman': total_peminjaman,
        'peminjaman_aktif': peminjaman_aktif,
    }
    return render(request, 'user/detail.html', context)

def user_create(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        kelas = request.POST.get('kelas')
        nis = request.POST.get('nis')
        is_active = request.POST.get('is_active') == 'on'  # checkbox
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO siswa (nama, kelas, nis, is_active) 
                VALUES (%s, %s, %s, %s)
            """, [nama, kelas, nis, is_active])
        
        messages.success(request, 'User berhasil ditambahkan!')
        return redirect('user_list')
    
    return render(request, 'user/create.html')

def user_update(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM siswa WHERE id = %s", [id])
        user = cursor.fetchone()
    
    if request.method == 'POST':
        nama = request.POST.get('nama')
        kelas = request.POST.get('kelas')
        nis = request.POST.get('nis')
        is_active = request.POST.get('is_active') == 'on'
        
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE siswa 
                SET nama = %s, kelas = %s, nis = %s, is_active = %s 
                WHERE id = %s
            """, [nama, kelas, nis, is_active, id])
        
        messages.success(request, 'Data user berhasil diperbarui!')
        return redirect('user_detail', id=id)
    
    context = {
        'user': user,
        'is_active': user[4] if user else False
    }
    return render(request, 'user/update.html', context)

def user_delete(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM siswa WHERE id = %s", [id])
        user = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(*) FROM peminjaman 
            WHERE siswa_id = %s AND status = 'Dipinjam'
        """, [id])
        peminjaman_aktif = cursor.fetchone()[0]
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM siswa WHERE id = %s", [id])
        
        messages.success(request, f'User "{user[1]}" berhasil dihapus!')
        return redirect('user_list')
    
    context = {
        'user': user,
        'peminjaman_aktif': peminjaman_aktif,
        'is_active': user[4] if user else False
    }
    return render(request, 'user/delete.html', context)