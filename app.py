import tkinter as tk
from tkinter import ttk, messagebox
import csv
import time
import os

from backend import m1_pesanan
from backend import m2_antrean
from backend import m3_laporan


def format_jam(detik_str):
    if not detik_str:
        return "-"
    try:
        s = int(detik_str)
        jam = (s // 3600) % 24
        mnt = (s % 3600) // 60
        dtk = s % 60
        return f"{jam:02d}:{mnt:02d}:{dtk:02d}"
    except ValueError:
        return "-"


def format_rupiah(angka_str):
    try:
        val = int(angka_str)
        return f"{val:,}".replace(",", ".")
    except ValueError:
        return str(angka_str)


class App2EZ4U(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2EZ4U Food Delivery")
        self.geometry("1150x720")
        self.configure(bg="#e9ecef")

        # Struktur Data M1
        self.arr = m1_pesanan.CustomArray()
        self.ll = m1_pesanan.CustomLinkedList()

        # Struktur Data M2
        self.q_naif = m2_antrean.NaiveQueue()
        self.q_circ = m2_antrean.CircularQueue(capacity=32768)
        self.undo_stack = m2_antrean.CustomStack()
        self.redo_stack = m2_antrean.CustomStack()

        # Cache M3 untuk Binary Search
        self.daftar_terurut_oid = None
        self.waktu_bangun_oid_ms = 0.0
        self.data_loaded = False
        self.next_oid_num = 200001

        self._build_ui()

    def _build_ui(self):
        # Top Header Bar
        header = tk.Frame(self, bg="#223a5e", height=45)
        header.pack(fill=tk.X)
        tk.Label(header, text="2EZ4U Food Delivery", fg="white", bg="#223a5e",
                 font=("Segoe UI", 13, "bold"), padx=15, pady=8).pack(side=tk.LEFT)

        # Main Area
        main_frame = tk.Frame(self, bg="#e9ecef")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Left Sidebar (Scrollable / Compact untuk M1 - M3)
        sidebar_container = tk.Frame(main_frame, bg="#f8f9fa", width=275, relief=tk.RIDGE, bd=1)
        sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        sidebar_container.pack_propagate(False)

        def add_sec(title):
            tk.Label(sidebar_container, text=title, bg="#f8f9fa", fg="#6c757d",
                     font=("Segoe UI", 7, "bold"), anchor="w").pack(fill=tk.X, padx=8, pady=(6, 1))

        def add_btn(text, cmd):
            b = tk.Button(sidebar_container, text=text, command=cmd, anchor="w", bg="#ffffff",
                          fg="#212529", activebackground="#dce4ec", relief=tk.SOLID, bd=1,
                          font=("Segoe UI", 8), padx=6, pady=2)
            b.pack(fill=tk.X, padx=8, pady=1)

        add_sec("DATA")
        add_btn("Load", self.menu_load)

        add_sec("M1 - DATA PESANAN")
        add_btn("ARRAY - LIHAT PESANAN", lambda: self.menu_m1_lihat("ARRAY"))
        add_btn("ARRAY - TAMBAH PESANAN REGULER", lambda: self.menu_m1_tambah("ARRAY", "REGULER", 3))
        add_btn("ARRAY - TAMBAH PESANAN PRIORITAS", lambda: self.menu_m1_tambah("ARRAY", "PRIORITAS", 2))
        add_btn("ARRAY - TAMBAH PESANAN VIP", lambda: self.menu_m1_tambah("ARRAY", "VIP", 1))
        add_btn("ARRAY - HAPUS PESANAN", lambda: self.menu_m1_hapus("ARRAY"))
        add_btn("LINKEDLIST - LIHAT PESANAN", lambda: self.menu_m1_lihat("LINKEDLIST"))
        add_btn("LINKEDLIST - TAMBAH PESANAN REGULER", lambda: self.menu_m1_tambah("LINKEDLIST", "REGULER", 3))
        add_btn("LINKEDLIST - TAMBAH PESANAN PRIORITAS", lambda: self.menu_m1_tambah("LINKEDLIST", "PRIORITAS", 2))
        add_btn("LINKEDLIST - TAMBAH PESANAN VIP", lambda: self.menu_m1_tambah("LINKEDLIST", "VIP", 1))
        add_btn("LINKEDLIST - HAPUS PESANAN", lambda: self.menu_m1_hapus("LINKEDLIST"))

        add_sec("M2 - STACK DAN QUEUE")
        add_btn("STACK - POSTFIX (MESIN KASIR)", self.menu_m2_postfix)
        add_btn("STACK - UNDO", self.menu_m2_undo)
        add_btn("STACK - REDO", self.menu_m2_redo)
        add_btn("QUEUE - ENQUEUE", self.menu_m2_enqueue)
        add_btn("QUEUE - DEQUEUE NAIF", self.menu_m2_dequeue_naif)
        add_btn("QUEUE - DEQUEUE CIRCULAR", self.menu_m2_dequeue_circular)

        add_sec("M3 - SORT DAN SEARCH")
        add_btn("SORT - INSERTION SORT", self.menu_m3_insertion_sort)
        add_btn("SORT - MERGE SORT", self.menu_m3_merge_sort)
        add_btn("SEARCH - LINEAR SEARCH", self.menu_m3_linear_search)
        add_btn("SEARCH - BINARY SEARCH", self.menu_m3_binary_search)

        # Status Badge Kiri Bawah (seperti di screenshot PDF)
        self.status_badge = tk.Label(sidebar_container, text="[Ready] 0.00 ms", bg="#223a5e", fg="white",
                                     font=("Consolas", 9, "bold"), anchor="w", padx=10, pady=5)
        self.status_badge.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=8)

        # Right Content Area
        right_panel = tk.Frame(main_frame, bg="#ffffff", relief=tk.RIDGE, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.form_area = tk.Frame(right_panel, bg="#ffffff", padx=15, pady=10)
        self.form_area.pack(fill=tk.X)

        self.info_label = tk.Label(right_panel, text="", bg="#ffffff", fg="#212529",
                                   font=("Segoe UI", 9), justify=tk.LEFT, anchor="w", padx=15)
        self.info_label.pack(fill=tk.X, pady=(0, 5))

        # Tabel Hasil (Treeview) di Tengah
        tree_frame = tk.Frame(right_panel, bg="#ffffff", padx=15)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, show="headings", height=12)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Panel COMMAND di Bawah
        tk.Label(right_panel, text="COMMAND", bg="#ffffff", fg="#6c757d",
                 font=("Segoe UI", 8, "bold"), anchor="w", padx=15).pack(fill=tk.X, pady=(6, 0))

        self.cmd_log = tk.Text(right_panel, height=5, font=("Consolas", 9), bg="#f8f9fa", relief=tk.SOLID, bd=1)
        self.cmd_log.pack(fill=tk.X, padx=15, pady=(2, 6))

        # Kotak Penjelasan Kuning di Paling Bawah Kanan
        self.note_label = tk.Label(right_panel, text="Klik tombol 'Load' di kiri atas untuk memuat 200.000 baris pesanan.",
                                   bg="#fff9db", fg="#5c4d00", font=("Segoe UI", 8), anchor="w", justify=tk.LEFT,
                                   padx=10, pady=6, relief=tk.SOLID, bd=1)
        self.note_label.pack(fill=tk.X, padx=15, pady=(0, 12))

    def catat_command(self, cmd_name, modul, ms, catatan_kuning=""):
        baris = f"{cmd_name:<24} -> {modul:<20} {ms:>7.2f} ms\n"
        self.cmd_log.insert("1.0", baris)
        self.status_badge.config(text=f"[{modul}] {ms:.2f} ms")
        if catatan_kuning:
            self.note_label.config(text=catatan_kuning)

    def bersihkan_form(self):
        for w in self.form_area.winfo_children():
            w.destroy()
        self.info_label.config(text="")

    def atur_tabel(self, kolom_list, lebar_list, rows):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = kolom_list
        for kol, lbr in zip(kolom_list, lebar_list):
            self.tree.heading(kol, text=kol)
            self.tree.column(kol, width=lbr, anchor="w")
        for r in rows:
            self.tree.insert("", tk.END, values=r)

    def tampilkan_detail_satu_pesanan(self, p):
        if not p:
            self.atur_tabel(["kolom", "isi"], [180, 450], [("Hasil", "Tidak ditemukan")])
            return
        rows = [
            ("oid", p[0]),
            ("pelanggan", p[1]),
            ("resto", p[2]),
            ("menu", p[3]),
            ("harga", format_rupiah(p[4])),
            ("prioritas", p[5]),
            ("masuk", format_jam(p[6])),
            ("selesai", format_jam(p[7]) if len(p) > 7 else "-"),
            ("status", p[8] if len(p) > 8 else "-")
        ]
        self.atur_tabel(["kolom", "isi"], [180, 450], rows)

    def _cek_load(self):
        if not self.data_loaded:
            messagebox.showwarning("Belum Load Data", "Silakan klik menu 'Load' di kiri atas terlebih dahulu!")
            return False
        return True

    # =========================================================================
    # MENU DATA: LOAD
    # =========================================================================
    def menu_load(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Data: Muat 200.000 baris pesanan.csv", font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        self.update_idletasks()

        csv_path = os.path.join("data", "pesanan.csv")
        if not os.path.exists(csv_path):
            messagebox.showerror("Error", f"Berkas {csv_path} tidak ditemukan!")
            return

        self.arr = m1_pesanan.CustomArray()
        self.ll = m1_pesanan.CustomLinkedList()
        self.q_naif = m2_antrean.NaiveQueue()
        self.q_circ = m2_antrean.CircularQueue(capacity=32768)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.daftar_terurut_oid = None

        t0 = time.perf_counter()
        jml_antre = 0
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row:
                    self.arr.append(row)
                    self.ll.append(row)
                    if len(row) > 8 and row[8] == "ANTRE":
                        self.q_naif.enqueue(row)
                        self.q_circ.enqueue(row)
                        jml_antre += 1
        t1 = time.perf_counter()
        ms = (t1 - t0) * 1000
        self.data_loaded = True
        self.next_oid_num = self.arr.size() + 1

        self.info_label.config(text=f"Berhasil memuat {self.arr.size():,} baris ke Array & LinkedList.\n"
                                    f"{jml_antre:,} pesanan berstatus ANTRE otomatis masuk ke Antrean Naif & Circular.")
        sample_rows = []
        for i in range(min(15, self.arr.size())):
            r = self.arr.get(i)
            sample_rows.append((i + 1, r[0], r[1], r[2], r[3], format_rupiah(r[4]), r[8]))
        self.atur_tabel(["#", "oid", "pelanggan", "resto", "menu", "harga", "status"],
                        [45, 95, 160, 120, 120, 80, 80], sample_rows)
        self.catat_command("load", "M1 - init", ms,
                           "200.000 baris dimuat ke Array dan Linked List, serta pesanan ANTRE dimasukkan ke kedua antrean M2.")

    # =========================================================================
    # MENU M1: ARRAY vs LINKED LIST
    # =========================================================================
    def menu_m1_lihat(self, struktur):
        self.bersihkan_form()
        tk.Label(self.form_area, text=f"{struktur.title()}: lihat pesanan pada indeks ke-i",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Akses indeks ke-i: Array O(1) langsung, Linked List O(n) telusur dari head.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Indeks ke-i:", bg="#ffffff").pack(side=tk.LEFT)
        ent = tk.Entry(frm, width=15)
        ent.insert(0, "100000")
        ent.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._cek_load(): return
            idx = int(ent.get())
            target = self.arr if struktur == "ARRAY" else self.ll
            t0 = time.perf_counter()
            p = target.get(idx)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000
            self.info_label.config(text=f"Membuka pesanan indeks ke-{idx:,} dari {target.size():,} baris.")
            self.tampilkan_detail_satu_pesanan(p)
            self.catat_command(f"{struktur.lower()}_get", f"M1 - {struktur.lower()}", ms,
                               "Array langsung menghitung alamat memori O(1), sedangkan Linked List menelusuri simpul dari head O(n).")

        tk.Button(frm, text="LIHAT", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)

    def menu_m1_tambah(self, struktur, jenis, prio):
        self.bersihkan_form()
        ket = {
            3: "masuk paling belakang",
            2: "menyerobot ke tengah barisan",
            1: "langsung ke urutan pertama"
        }[prio]
        tk.Label(self.form_area, text=f"{struktur.title()}: pesanan {jenis}, {ket}",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Nama pelanggan:", bg="#ffffff").pack(side=tk.LEFT)
        ent = tk.Entry(frm, width=25)
        ent.insert(0, "Pelanggan Baru")
        ent.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._cek_load(): return
            oid_baru = f"O-{self.next_oid_num:06d}"
            self.next_oid_num += 1
            item = [oid_baru, ent.get(), "kafe-teknik", "roti-bakar", "12000", str(prio), "28800", "", "ANTRE"]

            target = self.arr if struktur == "ARRAY" else self.ll
            n = target.size()

            t0 = time.perf_counter()
            if struktur == "ARRAY":
                if prio == 3:
                    self.arr.append(item)
                    pos = n
                elif prio == 2:
                    pos = n // 2
                    self.arr.insert(pos, item)
                else:
                    pos = 0
                    self.arr.insert(0, item)
            else:
                if prio == 3:
                    self.ll.append(item)
                    pos = n
                elif prio == 2:
                    pos = n // 2
                    self.ll.insert_at(pos, item)
                else:
                    pos = 0
                    self.ll.insert_head(item)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.info_label.config(text=f"Pesanan {oid_baru} ({jenis}) disisipkan pada posisi #{pos:,}. Panjang sekarang: {target.size():,}.")
            self.tampilkan_detail_satu_pesanan(item)
            self.catat_command(f"{struktur.lower()}_add_{jenis.lower()}", f"M1 - {struktur.lower()}", ms,
                               f"Penyisipan {jenis}: perhatikan selisih waktu Array vs Linked List pada panel COMMAND.")

        tk.Button(frm, text="TAMBAH", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)

    def menu_m1_hapus(self, struktur):
        self.bersihkan_form()
        tk.Label(self.form_area, text=f"{struktur.title()}: hapus pesanan ke-i",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Indeks ke-i:", bg="#ffffff").pack(side=tk.LEFT)
        ent = tk.Entry(frm, width=15)
        ent.insert(0, "0")
        ent.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._cek_load(): return
            idx = int(ent.get())
            target = self.arr if struktur == "ARRAY" else self.ll
            t0 = time.perf_counter()
            terhapus = target.remove_at(idx)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000
            self.info_label.config(text=f"Pesanan pada indeks #{idx:,} dicabut. Sisa barisan: {target.size():,}.")
            self.tampilkan_detail_satu_pesanan(terhapus)
            self.catat_command(f"{struktur.lower()}_del", f"M1 - {struktur.lower()}", ms,
                               "Menghapus di indeks 0 memaksa Array menggeser seluruh isi O(n), sedangkan Linked List cukup memajukan head O(1).")

        tk.Button(frm, text="HAPUS", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)

    # =========================================================================
    # MENU M2: STACK (POSTFIX, UNDO, REDO) & QUEUE (ENQUEUE, NAIF, CIRCULAR)
    # =========================================================================
    def menu_m2_postfix(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Stack: hitung struk lewat postfix",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Struk ditulis infix, lalu dihitung dua tahap dengan stack: Tahap 1 konversi ke postfix, Tahap 2 evaluasi nilai.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Struk belanja (infix):", bg="#ffffff").pack(side=tk.LEFT)
        ent = tk.Entry(frm, width=32)
        ent.insert(0, "(3 * 12000) + (2 * 8500) - 5000")
        ent.pack(side=tk.LEFT, padx=8)

        def aksi():
            ekspresi = ent.get()
            t0 = time.perf_counter()
            postfix_tokens, log_tahap1 = m2_antrean.ke_postfix(ekspresi)
            total, log_tahap2 = m2_antrean.hitung_postfix(postfix_tokens)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            postfix_str = " ".join(postfix_tokens)
            self.info_label.config(text=f"Struk   : {ekspresi}\nPostfix : {postfix_str}\nTOTAL   : Rp {format_rupiah(total)}")
            semua_langkah = log_tahap1 + log_tahap2
            self.atur_tabel(["langkah", "token", "tindakan", "stack", "output"],
                            [70, 70, 260, 160, 220], semua_langkah)
            self.catat_command("stack_postfix", "M2 - stack", ms,
                               "Baris 1.x adalah tahap konversi, baris 2.x tahap evaluasi. Operand kanan selalu keluar lebih dulu saat pop.")

        tk.Button(frm, text="HITUNG", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)
        aksi()  # Langsung tampilkan contoh saat menu diklik

    def menu_m2_enqueue(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Queue: pesanan baru masuk ke belakang",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Menambah pesanan di ujung belakang kedua antrean sekaligus, yang naif maupun yang circular.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Nama pelanggan:", bg="#ffffff").pack(side=tk.LEFT)
        ent = tk.Entry(frm, width=20)
        ent.insert(0, "X2")
        ent.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._cek_load(): return
            oid_baru = f"O-{self.next_oid_num:06d}"
            self.next_oid_num += 1
            pesanan = [oid_baru, ent.get(), "kafe-teknik", "roti-bakar", "12000", "2", "28800", "", "ANTRE"]

            t0 = time.perf_counter()
            self.q_naif.enqueue(pesanan)
            self.q_circ.enqueue(pesanan)
            # Catat ke undo stack & kosongkan redo stack
            self.undo_stack.push(("ENQUEUE", [pesanan]))
            self.redo_stack.clear()
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.info_label.config(text=f"{oid_baru} masuk ke barisan paling belakang pada KEDUA antrean.\n"
                                        f"Panjang sekarang: naif {self.q_naif.size():,}, circular {self.q_circ.size():,}.")
            self.tampilkan_detail_satu_pesanan(pesanan)
            self.catat_command("queue_enqueue", "M2 - queue", ms,
                               "enqueue selalu menempel di belakang, jadi O(1) pada kedua versi. Perbedaannya baru muncul saat dequeue.")

        tk.Button(frm, text="ENQUEUE", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)

    def menu_m2_dequeue_naif(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Queue naif: ambil dari depan dengan menggeser isi",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Mengambil indeks 0 lalu menggeser seluruh sisa isi satu petak ke kiri. Biayanya O(n) setiap kali.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Berapa kali dequeue:", bg="#ffffff").pack(side=tk.LEFT)
        ent = tk.Entry(frm, width=10)
        ent.insert(0, "2")
        ent.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._cek_load(): return
            k = int(ent.get())
            keluar = []
            total_geser = 0

            t0 = time.perf_counter()
            for _ in range(k):
                item, geser = self.q_naif.dequeue()
                if item is None:
                    break
                keluar.append(item)
                total_geser += geser
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            rata_geser = (total_geser // len(keluar)) if keluar else 0
            self.info_label.config(text=f"{len(keluar)} pesanan keluar dari depan antrean naif.\n"
                                        f"Total {total_geser:,} elemen digeser, rata-rata {rata_geser:,} geseran per dequeue.\n"
                                        f"Sisa antrean naif {self.q_naif.size():,}.")
            rows = [(i + 1, p[0], p[1], p[2], p[3], format_jam(p[6])) for i, p in enumerate(keluar[:50])]
            self.atur_tabel(["#", "oid", "pelanggan", "resto", "menu", "masuk"],
                            [45, 95, 170, 130, 130, 90], rows)
            self.catat_command("queue_dequeue_naive", "M2 - queue naif", ms,
                               "Mengambil indeks 0 memaksa seluruh sisa isi bergeser satu petak ke kiri, jadi O(n) per dequeue. Bandingkan dengan DEQUEUE CIRCULAR.")

        tk.Button(frm, text="DEQUEUE", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)

    def menu_m2_dequeue_circular(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Queue circular: ambil dari depan dengan memajukan penunjuk",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Hanya penunjuk front yang maju memakai sisa bagi terhadap kapasitas. Isi larik tidak digeser sama sekali.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Berapa kali dequeue:", bg="#ffffff").pack(side=tk.LEFT)
        ent = tk.Entry(frm, width=10)
        ent.insert(0, "2")
        ent.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._cek_load(): return
            k = int(ent.get())
            keluar = []

            t0 = time.perf_counter()
            for _ in range(k):
                item = self.q_circ.dequeue()
                if item is None:
                    break
                keluar.append(item)
            if keluar:
                # Sinkronkan juga q_naif jika panjangnya masih di atas q_circ agar saat undo/redo konsisten
                while self.q_naif.size() > self.q_circ.size():
                    self.q_naif.dequeue()
                self.undo_stack.push(("DEQUEUE", keluar))
                self.redo_stack.clear()
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.info_label.config(text=f"{len(keluar)} pesanan keluar dari depan antrean circular.\n"
                                        f"Tidak ada elemen yang digeser. front sekarang {self.q_circ.front}, rear {self.q_circ.rear}, kapasitas {self.q_circ.capacity:,}.\n"
                                        f"Sisa antrean circular {self.q_circ.size():,}.")
            rows = [(i + 1, p[0], p[1], p[2], p[3], format_jam(p[6])) for i, p in enumerate(keluar[:50])]
            self.atur_tabel(["#", "oid", "pelanggan", "resto", "menu", "masuk"],
                            [45, 95, 170, 130, 130, 90], rows)
            self.catat_command("queue_dequeue_circular", "M2 - queue circular", ms,
                               "Yang berpindah hanya penunjuk front memakai sisa bagi terhadap kapasitas. Isi larik tidak disentuh sama sekali, jadi O(1).")

        tk.Button(frm, text="DEQUEUE", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)

    def menu_m2_undo(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Stack: batalkan aksi antrean terakhir",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Mengambil catatan teratas tumpukan undo, lalu menjalankan kebalikannya. Aksi terakhirlah yang dibatalkan lebih dulu.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)

        def aksi():
            if self.undo_stack.is_empty():
                self.info_label.config(text="Tumpukan undo kosong, tidak ada aksi untuk dibatalkan.")
                return

            t0 = time.perf_counter()
            jenis_aksi, daftar_item = self.undo_stack.pop()
            if jenis_aksi == "ENQUEUE":
                for _ in daftar_item:
                    self.q_naif.pop_back()
                    self.q_circ.pop_back()
                ket_aksi = f"Pembatalan enqueue: {daftar_item[0][0]} dikeluarkan lagi dari belakang."
            else:
                self.q_naif.prepend_batch(daftar_item)
                self.q_circ.prepend_batch(daftar_item)
                ket_aksi = f"Pembatalan dequeue: {len(daftar_item)} pesanan dikembalikan ke DEPAN antrean."

            self.redo_stack.push((jenis_aksi, daftar_item))
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.info_label.config(text=f"{ket_aksi}\nPanjang antrean sekarang: naif {self.q_naif.size():,}, circular {self.q_circ.size():,}. "
                                        f"Tumpukan undo tersisa {self.undo_stack.size()} catatan.")
            rows = [(i + 1, p[0], p[1], p[2], p[3]) for i, p in enumerate(daftar_item[:20])]
            self.atur_tabel(["#", "oid", "pelanggan", "resto", "menu"], [45, 100, 180, 140, 140], rows)
            self.catat_command("stack_undo", "M2 - stack", ms,
                               "Undo mengambil dari puncak tumpukan undo, menjalankan kebalikannya, lalu mendorong catatan itu ke tumpukan redo.")

        tk.Button(frm, text="UNDO", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)

    def menu_m2_redo(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Stack: kerjakan lagi aksi yang dibatalkan",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Mengambil catatan teratas tumpukan redo, lalu mengerjakan ulang aksi aslinya. Aksi baru apa pun mengosongkan tumpukan ini.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)

        def aksi():
            if self.redo_stack.is_empty():
                self.info_label.config(text="Tumpukan redo kosong, tidak ada yang diulang.")
                return

            t0 = time.perf_counter()
            jenis_aksi, daftar_item = self.redo_stack.pop()
            if jenis_aksi == "ENQUEUE":
                for p in daftar_item:
                    self.q_naif.enqueue(p)
                    self.q_circ.enqueue(p)
                ket_aksi = f"Enqueue dikerjakan lagi: {daftar_item[0][0]} masuk kembali ke belakang."
            else:
                for _ in daftar_item:
                    self.q_naif.dequeue()
                    self.q_circ.dequeue()
                ket_aksi = f"Dequeue dikerjakan lagi: {len(daftar_item)} pesanan keluar lagi dari depan antrean."

            self.undo_stack.push((jenis_aksi, daftar_item))
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.info_label.config(text=f"{ket_aksi}\nPanjang antrean sekarang: naif {self.q_naif.size():,}, circular {self.q_circ.size():,}. "
                                        f"Tumpukan undo {self.undo_stack.size()}, redo {self.redo_stack.size()}.")
            rows = [(i + 1, p[0], p[1], p[2], p[3]) for i, p in enumerate(daftar_item[:20])]
            self.atur_tabel(["#", "oid", "pelanggan", "resto", "menu"], [45, 100, 180, 140, 140], rows)
            self.catat_command("stack_redo", "M2 - stack", ms,
                               "Redo mengerjakan ULANG aksi aslinya, bukan kebalikannya, lalu mengembalikan catatannya ke tumpukan undo.")

        tk.Button(frm, text="REDO", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)

    # =========================================================================
    # MENU M3: SORT (INSERTION & MERGE) DAN SEARCH (LINEAR & BINARY)
    # =========================================================================
    def menu_m3_insertion_sort(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Sort: insertion sort, O(n²)",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Setiap elemen digeser mundur sampai menemukan tempatnya. Sederhana, tetapi kerjanya tumbuh kuadratik.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Jumlah baris diurutkan:", bg="#ffffff").pack(side=tk.LEFT)
        ent_n = tk.Entry(frm, width=10)
        ent_n.insert(0, "1000")
        ent_n.pack(side=tk.LEFT, padx=(6, 15))

        tk.Label(frm, text="Diurutkan menurut:", bg="#ffffff").pack(side=tk.LEFT)
        cmb_kunci = ttk.Combobox(frm, values=["harga", "oid", "selesai"], width=12, state="readonly")
        cmb_kunci.set("harga")
        cmb_kunci.pack(side=tk.LEFT, padx=6)

        def aksi():
            if not self._cek_load(): return
            n = int(ent_n.get())
            kunci = cmb_kunci.get()
            if n > 20000:
                messagebox.showwarning("Ditolak", "DITOLAK: batas insertion sort adalah 20.000 baris agar aplikasi tidak membeku. Gunakan Merge Sort untuk data penuh!")
                return

            potongan = self.arr.data[:n]
            t0 = time.perf_counter()
            terurut, banding, pindah = m3_laporan.insertion_sort(potongan, kunci)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.info_label.config(text=f"{len(terurut):,} pesanan diurutkan menurut {kunci}.\n"
                                        f"{banding:,} perbandingan, {pindah:,} pemindahan.")
            rows = [(i + 1, p[0], format_rupiah(p[4]), format_jam(p[7]), p[2], p[3]) for i, p in enumerate(terurut[:100])]
            self.atur_tabel(["#", "oid", "harga", "selesai", "resto", "menu"],
                            [45, 95, 85, 90, 140, 140], rows)
            self.catat_command("insertion_sort", "M3 - insertion sort", ms,
                               "Setiap elemen digeser mundur sampai menemukan tempatnya, jadi biayanya tumbuh kuadratik O(n²): melipatduakan n membuat kerjanya ~4x lipat.")

        tk.Button(frm, text="URUTKAN", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT, padx=8)

    def menu_m3_merge_sort(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Sort: merge sort, O(n log n)",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Larik dibelah dua terus-menerus, lalu potongan yang sudah terurut disatukan kembali.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Jumlah baris diurutkan:", bg="#ffffff").pack(side=tk.LEFT)
        ent_n = tk.Entry(frm, width=10)
        ent_n.insert(0, "4000")
        ent_n.pack(side=tk.LEFT, padx=(6, 15))

        tk.Label(frm, text="Diurutkan menurut:", bg="#ffffff").pack(side=tk.LEFT)
        cmb_kunci = ttk.Combobox(frm, values=["oid", "harga", "selesai"], width=12, state="readonly")
        cmb_kunci.set("oid")
        cmb_kunci.pack(side=tk.LEFT, padx=6)

        def aksi():
            if not self._cek_load(): return
            n = min(int(ent_n.get()), self.arr.size())
            kunci = cmb_kunci.get()
            potongan = self.arr.data[:n]

            t0 = time.perf_counter()
            terurut, banding, pindah = m3_laporan.merge_sort(potongan, kunci)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.info_label.config(text=f"{len(terurut):,} pesanan diurutkan menurut {kunci}.\n"
                                        f"{banding:,} perbandingan, {pindah:,} pemindahan.")
            rows = [(i + 1, p[0], format_rupiah(p[4]), format_jam(p[7]), p[2], p[3]) for i, p in enumerate(terurut[:100])]
            self.atur_tabel(["#", "oid", "harga", "selesai", "resto", "menu"],
                            [45, 95, 85, 90, 140, 140], rows)
            self.catat_command("merge_sort", "M3 - merge sort", ms,
                               "Larik dibelah dua terus-menerus lalu potongan yang sudah terurut disatukan kembali O(n log n). Hasilnya sama persis dengan insertion sort karena stabil.")

        tk.Button(frm, text="URUTKAN", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT, padx=8)

    def menu_m3_linear_search(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Search: linear search, O(n)",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Memeriksa pesanan satu per satu dari depan. Tidak menuntut data terurut.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Nomor pesanan (oid):", bg="#ffffff").pack(side=tk.LEFT)
        ent = tk.Entry(frm, width=18)
        ent.insert(0, "O-137442")
        ent.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._cek_load(): return
            target = ent.get().strip()
            t0 = time.perf_counter()
            item, idx, banding = m3_laporan.linear_search(self.arr.data, target)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            if item:
                self.info_label.config(text=f"Ditemukan pada indeks {idx:,}.\n{banding:,} perbandingan.")
            else:
                self.info_label.config(text=f"Tidak ditemukan setelah memeriksa {banding:,} baris.")
            self.tampilkan_detail_satu_pesanan(item)
            self.catat_command("linear_search", "M3 - linear search", ms,
                               f"Data tidak perlu terurut, tetapi setiap pesanan diperiksa satu per satu dari depan. Kasus terburuk menyentuh seluruh {self.arr.size():,} baris.")

        tk.Button(frm, text="CARI", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)

    def menu_m3_binary_search(self):
        self.bersihkan_form()
        tk.Label(self.form_area, text="Search: binary search, O(log n)",
                 font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_area, text="Membuang separuh sisa daftar pada setiap perbandingan. Menuntut daftar yang sudah terurut menurut oid.",
                 font=("Segoe UI", 8), fg="#6c757d", bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_area, bg="#ffffff")
        frm.pack(anchor="w", pady=6)
        tk.Label(frm, text="Nomor pesanan (oid):", bg="#ffffff").pack(side=tk.LEFT)
        ent = tk.Entry(frm, width=18)
        ent.insert(0, "O-137442")
        ent.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._cek_load(): return
            target = ent.get().strip()

            # Bangun daftar terurut oid sekali dengan merge sort bila belum ada
            if self.daftar_terurut_oid is None:
                t_sort0 = time.perf_counter()
                self.daftar_terurut_oid, _, _ = m3_laporan.merge_sort(self.arr.data, "oid")
                t_sort1 = time.perf_counter()
                self.waktu_bangun_oid_ms = (t_sort1 - t_sort0) * 1000

            t0 = time.perf_counter()
            item, idx, banding = m3_laporan.binary_search(self.daftar_terurut_oid, target)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            if item:
                self.info_label.config(text=f"Daftar terurut oid dibangun sekali dengan merge sort, {self.waktu_bangun_oid_ms:.2f} ms.\n"
                                            f"Ditemukan pada baris ke-{idx + 1:,} dari {len(self.daftar_terurut_oid):,} baris.\n"
                                            f"{banding} perbandingan, bandingkan dengan linear search.")
            else:
                self.info_label.config(text=f"Daftar terurut oid dibangun sekali dengan merge sort, {self.waktu_bangun_oid_ms:.2f} ms.\n"
                                            f"Tidak ditemukan ({banding} perbandingan).")
            self.tampilkan_detail_satu_pesanan(item)
            self.catat_command("binary_search", "M3 - binary search", ms,
                               "Setiap perbandingan membuang separuh sisa daftar, jadi 200.000 baris habis dalam paling banyak 18 langkah. Syaratnya daftar harus SUDAH terurut menurut oid.")

        tk.Button(frm, text="CARI", bg="#223a5e", fg="white", font=("Segoe UI", 8, "bold"), width=12, command=aksi).pack(side=tk.LEFT)


if __name__ == "__main__":
    app = App2EZ4U()
    app.mainloop()
