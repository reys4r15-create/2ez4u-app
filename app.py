import tkinter as tk
from tkinter import messagebox
import csv
import time
import os

# Import hanya M1 sampai M3
from backend import m1_pesanan
from backend import m2_antrean
from backend import m3_laporan

class App2EZ4U(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2EZ4U Food Delivery - Demo Progress (M1 - M3)")
        self.geometry("1080x680")
        self.configure(bg="#f4f6f9")

        # Inisialisasi Struktur Data sesuai nama class di backend Anda
        self.arr = m1_pesanan.CustomArray()
        self.ll = m1_pesanan.CustomLinkedList()
        self.antrean = m2_antrean.CircularQueue(capacity=5000)
        self.undo_stack = m2_antrean.CustomStack()

        self.laporan_terurut = []
        self.data_loaded = False

        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#1e3d59", height=50)
        header.pack(fill=tk.X)
        tk.Label(header, text="2EZ4U Food Delivery (M1 - M3)", fg="white", bg="#1e3d59", 
                 font=("Segoe UI", 14, "bold"), padx=15, pady=10).pack(side=tk.LEFT)

        # Main Container
        main_frame = tk.Frame(self, bg="#f4f6f9")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panel Kiri (Sidebar Menu)
        sidebar = tk.Frame(main_frame, bg="#ffffff", width=270, relief=tk.RIDGE, bd=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)

        def add_section(judul):
            tk.Label(sidebar, text=judul, bg="#ffffff", fg="#555555", 
                     font=("Segoe UI", 8, "bold"), anchor="w").pack(fill=tk.X, padx=10, pady=(10, 2))

        def add_btn(teks, cmd):
            btn = tk.Button(sidebar, text=teks, command=cmd, anchor="w", bg="#f8f9fa", 
                            fg="#212529", relief=tk.GROOVE, font=("Segoe UI", 9), padx=8, pady=3)
            btn.pack(fill=tk.X, padx=10, pady=1)

        add_section("DATA")
        add_btn("Load", self.menu_load)

        add_section("M1 - DATA PESANAN")
        add_btn("ARRAY - LIHAT PESANAN", lambda: self.menu_lihat("ARRAY"))
        add_btn("ARRAY - TAMBAH PESANAN REGULER", lambda: self.menu_tambah("ARRAY", "REGULER", 3))
        add_btn("ARRAY - TAMBAH PESANAN PRIORITAS", lambda: self.menu_tambah("ARRAY", "PRIORITAS", 2))
        add_btn("ARRAY - TAMBAH PESANAN VIP", lambda: self.menu_tambah("ARRAY", "VIP", 1))
        add_btn("ARRAY - HAPUS PESANAN", lambda: self.menu_hapus("ARRAY"))
        
        add_btn("LINKEDLIST - LIHAT PESANAN", lambda: self.menu_lihat("LINKEDLIST"))
        add_btn("LINKEDLIST - TAMBAH PESANAN REGULER", lambda: self.menu_tambah("LINKEDLIST", "REGULER", 3))
        add_btn("LINKEDLIST - TAMBAH PESANAN PRIORITAS", lambda: self.menu_tambah("LINKEDLIST", "PRIORITAS", 2))
        add_btn("LINKEDLIST - TAMBAH PESANAN VIP", lambda: self.menu_tambah("LINKEDLIST", "VIP", 1))
        add_btn("LINKEDLIST - HAPUS PESANAN", lambda: self.menu_hapus("LINKEDLIST"))

        add_section("M2 - ANTREAN DAN UNDO")
        add_btn("Isi antrean FIFO", self.menu_isi_antrean)
        add_btn("Layani berikutnya", self.menu_layani)
        add_btn("Undo", self.menu_undo)

        add_section("M3 - LAPORAN DAN PENCARIAN")
        add_btn("Laporan harian", self.menu_laporan)
        add_btn("Cari di laporan", self.menu_cari_laporan)

        tk.Button(sidebar, text="CLEAR", bg="#1e3d59", fg="white", font=("Segoe UI", 9, "bold"),
                  command=self.clear_output).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Panel Kanan (Form, Output, Command Log)
        right_panel = tk.Frame(main_frame, bg="#ffffff", relief=tk.RIDGE, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.form_frame = tk.Frame(right_panel, bg="#ffffff", padx=15, pady=15)
        self.form_frame.pack(fill=tk.X)

        self.output_text = tk.Text(right_panel, height=18, font=("Consolas", 10), bg="#fcfcfc", relief=tk.SUNKEN, bd=1)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        tk.Label(right_panel, text="COMMAND", bg="#ffffff", fg="#555555", 
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill=tk.X, padx=15)
        
        self.cmd_log = tk.Text(right_panel, height=6, font=("Consolas", 9), bg="#f1f3f5", relief=tk.SUNKEN, bd=1)
        self.cmd_log.pack(fill=tk.X, padx=15, pady=(0, 15))

    def log_command(self, cmd_name, module_name, elapsed_ms):
        log_line = f"{cmd_name:<25} -> {module_name:<15} {elapsed_ms:>8.2f} ms\n"
        self.cmd_log.insert("1.0", log_line)

    def clear_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)
        self.cmd_log.delete("1.0", tk.END)

    def _pastikan_data_dimuat(self):
        if not self.data_loaded or self.arr.size() == 0:
            messagebox.showwarning("Peringatan", "Silakan klik tombol 'Load' di kiri atas terlebih dahulu!")
            return False
        return True

    # --- FUNGSI LOAD DATA ---
    def menu_load(self):
        self.clear_form()
        tk.Label(self.form_frame, text="Memuat Data dari data/pesanan.csv...", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w")
        self.update_idletasks()
        
        csv_path = os.path.join("data", "pesanan.csv")
        if not os.path.exists(csv_path):
            messagebox.showerror("Error", f"File {csv_path} tidak ditemukan!")
            return

        # Reset struktur data M1
        self.arr = m1_pesanan.CustomArray()
        self.ll = m1_pesanan.CustomLinkedList()

        t0 = time.perf_counter()
        count = 0
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row:
                    self.arr.append(row)
                    self.ll.append(row)
                    count += 1
        t1 = time.perf_counter()
        ms = (t1 - t0) * 1000
        self.data_loaded = True

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"[LOAD SUKSES]\nBerhasil memuat {count:,} baris pesanan ke CustomArray dan CustomLinkedList.\n")
        self.output_text.insert(tk.END, f"Ukuran Array      : {self.arr.size():,}\n")
        self.output_text.insert(tk.END, f"Ukuran LinkedList : {self.ll.size():,}\n")
        self.output_text.insert(tk.END, f"Waktu Eksekusi    : {ms:.2f} ms\n\n")
        self.output_text.insert(tk.END, f"Contoh 3 Pesanan Pertama:\n")
        for i in range(min(3, self.arr.size())):
            self.output_text.insert(tk.END, f"  [{i}] {self.arr.get(i)}\n")
        self.log_command("load", "M1 - init", ms)

    # --- FUNGSI M1: LIHAT, TAMBAH, HAPUS ---
    def menu_lihat(self, struktur):
        self.clear_form()
        tk.Label(self.form_frame, text=f"{struktur}: Lihat Pesanan pada Indeks ke-i", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(self.form_frame, text="Array = O(1) akses langsung | LinkedList = O(n) telusur dari head", fg="#666666", bg="#ffffff").pack(anchor="w")
        
        frm = tk.Frame(self.form_frame, bg="#ffffff")
        frm.pack(anchor="w", pady=8)
        tk.Label(frm, text="Masukkan Indeks (0 s/d n-1):", bg="#ffffff").pack(side=tk.LEFT)
        ent_idx = tk.Entry(frm, width=15)
        ent_idx.insert(0, "100000")
        ent_idx.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._pastikan_data_dimuat(): return
            try:
                idx = int(ent_idx.get())
            except ValueError:
                messagebox.showerror("Error", "Indeks harus berupa angka bulat!")
                return

            target = self.arr if struktur == "ARRAY" else self.ll
            t0 = time.perf_counter()
            if hasattr(target, 'get'):
                hasil = target.get(idx)
            else:
                # Fallback jika get belum ada di CustomLinkedList
                curr = target.head
                for _ in range(idx):
                    if not curr: break
                    curr = curr.next
                hasil = curr.data if curr else None
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.output_text.insert("1.0", f"[{struktur} - LIHAT INDEKS {idx}]\n  Hasil : {hasil}\n  Waktu : {ms:.4f} ms\n\n")
            self.log_command(f"{struktur.lower()}_get", f"M1 - {struktur.lower()}", ms)

        tk.Button(frm, text="LIHAT PESANAN", bg="#1e3d59", fg="white", font=("Segoe UI", 9, "bold"), command=aksi).pack(side=tk.LEFT)

    def menu_tambah(self, struktur, jenis, prio):
        self.clear_form()
        ket = {
            3: "masuk paling belakang (append)",
            2: "menyerobot ke tengah barisan (indeks n//2)",
            1: "langsung ke urutan pertama (indeks 0 / head)"
        }[prio]
        tk.Label(self.form_frame, text=f"{struktur}: pesanan {jenis}, {ket}", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_frame, bg="#ffffff")
        frm.pack(anchor="w", pady=8)
        tk.Label(frm, text="Nama pelanggan:", bg="#ffffff").pack(side=tk.LEFT)
        ent_nama = tk.Entry(frm, width=22)
        ent_nama.insert(0, "Pelanggan Baru")
        ent_nama.pack(side=tk.LEFT, padx=8)

        tk.Label(frm, text="Menu:", bg="#ffffff").pack(side=tk.LEFT)
        ent_menu = tk.Entry(frm, width=18)
        ent_menu.insert(0, "nasi-goreng")
        ent_menu.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._pastikan_data_dimuat(): return
            target = self.arr if struktur == "ARRAY" else self.ll
            ukuran_skrg = target.size()
            oid_baru = f"O-{ukuran_skrg + 1:06d}"
            data_baru = [oid_baru, ent_nama.get(), "kafe-teknik", ent_menu.get(), "18000", str(prio), "50000", "", "ANTRE"]
            
            t0 = time.perf_counter()
            if struktur == "ARRAY":
                if prio == 3:
                    self.arr.append(data_baru)
                    pos = ukuran_skrg
                elif prio == 2:
                    pos = ukuran_skrg // 2
                    self.arr.insert(pos, data_baru)
                elif prio == 1:
                    pos = 0
                    self.arr.insert(0, data_baru)
            else:
                if prio == 3:
                    self.ll.append(data_baru)
                    pos = ukuran_skrg
                elif prio == 2:
                    pos = ukuran_skrg // 2
                    self.ll.insert_at(pos, data_baru)
                elif prio == 1:
                    pos = 0
                    self.ll.insert_head(data_baru)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.output_text.insert("1.0", f"[{struktur} - TAMBAH {jenis} (Posisi #{pos})]\n  Data  : {data_baru}\n  Total : {target.size():,} pesanan | Waktu: {ms:.4f} ms\n\n")
            self.log_command(f"{struktur.lower()}_add_{jenis.lower()}", f"M1 - {struktur.lower()}", ms)

        tk.Button(frm, text="TAMBAH", bg="#1e3d59", fg="white", font=("Segoe UI", 9, "bold"), command=aksi).pack(side=tk.LEFT, padx=5)

    def menu_hapus(self, struktur):
        self.clear_form()
        tk.Label(self.form_frame, text=f"{struktur}: Hapus Pesanan pada Indeks ke-i", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w")

        frm = tk.Frame(self.form_frame, bg="#ffffff")
        frm.pack(anchor="w", pady=8)
        tk.Label(frm, text="Indeks yang dihapus:", bg="#ffffff").pack(side=tk.LEFT)
        ent_idx = tk.Entry(frm, width=15)
        ent_idx.insert(0, "0")
        ent_idx.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._pastikan_data_dimuat(): return
            try:
                idx = int(ent_idx.get())
            except ValueError:
                messagebox.showerror("Error", "Indeks harus berupa angka bulat!")
                return

            target = self.arr if struktur == "ARRAY" else self.ll
            t0 = time.perf_counter()
            terhapus = target.remove_at(idx)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.output_text.insert("1.0", f"[{struktur} - HAPUS INDEKS {idx}]\n  Terhapus : {terhapus}\n  Sisa     : {target.size():,} pesanan | Waktu: {ms:.4f} ms\n\n")
            self.log_command(f"{struktur.lower()}_del", f"M1 - {struktur.lower()}", ms)

        tk.Button(frm, text="HAPUS", bg="#c0392b", fg="white", font=("Segoe UI", 9, "bold"), command=aksi).pack(side=tk.LEFT)

    # --- FUNGSI M2: ANTREAN (CIRCULAR QUEUE) & UNDO (STACK) ---
    def menu_isi_antrean(self):
        self.clear_form()
        tk.Label(self.form_frame, text="M2: Isi Antrean FIFO (CircularQueue)", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w")
        
        frm = tk.Frame(self.form_frame, bg="#ffffff")
        frm.pack(anchor="w", pady=8)
        tk.Label(frm, text="Jumlah pesanan dimasukkan ke antrean:", bg="#ffffff").pack(side=tk.LEFT)
        ent_jml = tk.Entry(frm, width=10)
        ent_jml.insert(0, "100")
        ent_jml.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._pastikan_data_dimuat(): return
            batas = int(ent_jml.get())
            self.antrean = m2_antrean.CircularQueue(capacity=max(1000, batas + 100))
            self.undo_stack = m2_antrean.CustomStack()

            t0 = time.perf_counter()
            masuk = 0
            for i in range(min(batas, self.arr.size())):
                pesanan = self.arr.get(i)
                if pesanan and self.antrean.enqueue(pesanan):
                    masuk += 1
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.output_text.insert("1.0", f"[M2 - ISI ANTREAN FIFO]\n  Berhasil memasukkan {masuk} pesanan ke CircularQueue.\n  Ukuran Antrean sekarang: {self.antrean.size()} | Waktu: {ms:.4f} ms\n\n")
            self.log_command("isi_antrean", "M2 - queue", ms)

        tk.Button(frm, text="ISI ANTREAN", bg="#1e3d59", fg="white", font=("Segoe UI", 9, "bold"), command=aksi).pack(side=tk.LEFT)

    def menu_layani(self):
        self.clear_form()
        tk.Label(self.form_frame, text="M2: Layani Pesanan Berikutnya (Dequeue -> Push ke Undo Stack)", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w")
        
        t0 = time.perf_counter()
        dilayani = self.antrean.dequeue()
        if dilayani is not None:
            self.undo_stack.push(dilayani)
        t1 = time.perf_counter()
        ms = (t1 - t0) * 1000

        if dilayani:
            self.output_text.insert("1.0", f"[M2 - LAYANI BERIKUTNYA]\n  Dilayani     : {dilayani}\n  Sisa Antrean : {self.antrean.size()} | Waktu: {ms:.4f} ms\n\n")
        else:
            self.output_text.insert("1.0", f"[M2 - LAYANI BERIKUTNYA] Antrean kosong! Klik 'Isi antrean FIFO' dulu.\n\n")
        self.log_command("layani_berikutnya", "M2 - queue", ms)

    def menu_undo(self):
        self.clear_form()
        tk.Label(self.form_frame, text="M2: Undo Pelayanan Terakhir (Pop dari CustomStack)", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w")

        t0 = time.perf_counter()
        batal = self.undo_stack.pop()
        if batal is not None:
            self.antrean.enqueue(batal)
        t1 = time.perf_counter()
        ms = (t1 - t0) * 1000

        if batal:
            self.output_text.insert("1.0", f"[M2 - UNDO PELAYANAN]\n  Dikembalikan : {batal}\n  Sisa Antrean : {self.antrean.size()} | Waktu: {ms:.4f} ms\n\n")
        else:
            self.output_text.insert("1.0", f"[M2 - UNDO] Stack Undo kosong! Belum ada pesanan yang dilayani.\n\n")
        self.log_command("undo", "M2 - stack", ms)

    # --- FUNGSI M3: LAPORAN (INSERTION SORT) & PENCARIAN (BINARY SEARCH) ---
    def menu_laporan(self):
        self.clear_form()
        tk.Label(self.form_frame, text="M3: Laporan Harian Terurut (insertion_sort_by_harga)", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w")
        
        frm = tk.Frame(self.form_frame, bg="#ffffff")
        frm.pack(anchor="w", pady=8)
        tk.Label(frm, text="Jumlah sampel data (N):", bg="#ffffff").pack(side=tk.LEFT)
        ent_n = tk.Entry(frm, width=10)
        ent_n.insert(0, "1000")
        ent_n.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._pastikan_data_dimuat(): return
            n = min(int(ent_n.get()), self.arr.size())
            sampel = [self.arr.get(i) for i in range(n)]

            t0 = time.perf_counter()
            self.laporan_terurut = m3_laporan.insertion_sort_by_harga(sampel)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            teks_hasil = f"[M3 - INSERTION SORT BY HARGA ({n} Data)]\n  Waktu Eksekusi: {ms:.2f} ms\n  10 Pesanan Termurah:\n"
            for item in self.laporan_terurut[:10]:
                teks_hasil += f"    OID: {item[0]} | Pelanggan: {item[1]:<22} | Menu: {item[3]:<15} | Harga: Rp{item[4]}\n"
            self.output_text.insert("1.0", teks_hasil + "\n")
            self.log_command("laporan_harian", "M3 - sort", ms)

        tk.Button(frm, text="URUTKAN LAPORAN", bg="#1e3d59", fg="white", font=("Segoe UI", 9, "bold"), command=aksi).pack(side=tk.LEFT)

    def menu_cari_laporan(self):
        self.clear_form()
        tk.Label(self.form_frame, text="M3: Cari Pesanan dengan Binary Search (binary_search_by_oid)", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w")
        
        frm = tk.Frame(self.form_frame, bg="#ffffff")
        frm.pack(anchor="w", pady=8)
        tk.Label(frm, text="Masukkan OID (contoh: O-000005):", bg="#ffffff").pack(side=tk.LEFT)
        ent_oid = tk.Entry(frm, width=20)
        ent_oid.insert(0, "O-000005")
        ent_oid.pack(side=tk.LEFT, padx=8)

        def aksi():
            if not self._pastikan_data_dimuat(): return
            target_oid = ent_oid.get().strip()

            # Data di self.arr.data dari CSV sudah terurut berdasarkan OID (O-000001 s/d O-200000)
            t0 = time.perf_counter()
            hasil = m3_laporan.binary_search_by_oid(self.arr.data, target_oid)
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.output_text.insert("1.0", f"[M3 - BINARY SEARCH OID '{target_oid}']\n  Hasil : {hasil}\n  Waktu : {ms:.4f} ms\n\n")
            self.log_command("cari_laporan", "M3 - bsearch", ms)

        tk.Button(frm, text="CARI OID", bg="#1e3d59", fg="white", font=("Segoe UI", 9, "bold"), command=aksi).pack(side=tk.LEFT)

if __name__ == "__main__":
    app = App2EZ4U()
    app.mainloop()
