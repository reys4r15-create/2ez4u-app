import csv
import time
import tkinter as tk
from tkinter import ttk, messagebox

from backend.m1_pesanan import CustomArray, CustomLinkedList
from backend.m2_antrean import CircularQueue, CustomStack
from backend.m3_laporan import insertion_sort_by_harga, binary_search_by_oid
from backend.m4_pencarian import CustomHashTable, merge_sort_by_time
from backend.m5_katalog import KatalogBST, MinHeapPriority
from backend.m6_peta import CustomGraph

class App2EZ4U:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U APP - Delivery Service Engine")
        self.root.geometry("850x600")

        self.data_pesanan = []
        self.graph = CustomGraph()
        self.hash_table = CustomHashTable()

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab M1 & M2
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="M1 & M2: Pesanan & Antrean")
        ttk.Button(tab1, text="Uji Struct Array vs LinkedList", command=self.test_m1).pack(pady=10)
        
        # Tab M3 & M4
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="M3 & M4: Sort & Search")
        ttk.Button(tab2, text="Jalankan Insertion Sort & Merge Sort", command=self.test_m3_m4).pack(pady=10)

        # Tab M5
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="M5: Katalog & Prioritas")
        ttk.Button(tab3, text="Cari Rentang Harga BST (10rb - 20rb)", command=self.test_m5).pack(pady=10)

        # Tab M6
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="M6: Peta & Navigasi")
        ttk.Button(tab4, text="Hitung Rute Terpendek (Dijkstra)", command=self.test_m6).pack(pady=10)

        # Log Text Box
        self.log_text = tk.Text(self.root, height=15)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def load_data(self):
        try:
            with open("data/pesanan.csv", mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                count = 0
                for row in reader:
                    if count >= 1000: # Limit sampel awal untuk demo UI
                        break
                    self.data_pesanan.append(row)
                    self.hash_table.put(row[0], row)
                    count += 1
            self.log(f"Berhasil memuat {len(self.data_pesanan)} data sampel pesanan ke Hash Table.")

            with open("data/peta.csv", mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    self.graph.add_edge(row[0], row[1], int(row[2]))
            self.log("Berhasil memuat data Peta Graf.\n")

        except Exception as e:
            self.log(f"Error loading CSV data: {e}")

    def test_m1(self):
        t0 = time.time()
        arr = CustomArray()
        ll = CustomLinkedList()
        for item in self.data_pesanan:
            arr.append(item)
            ll.append(item)
        dt = (time.time() - t0) * 1000
        self.log(f"[M1] Append {len(self.data_pesanan)} data ke Array & LinkedList selesai dalam {dt:.2f} ms")

    def test_m3_m4(self):
        t0 = time.time()
        sorted_arr = insertion_sort_by_harga(self.data_pesanan[:100])
        dt1 = (time.time() - t0) * 1000
        self.log(f"[M3] Insertion Sort (100 data): {dt1:.2f} ms")

        t0 = time.time()
        res_merge = merge_sort_by_time(self.data_pesanan[:500])
        dt2 = (time.time() - t0) * 1000
        self.log(f"[M4] Merge Sort (500 data): {dt2:.2f} ms")

    def test_m5(self):
        bst = KatalogBST()
        for item in self.data_pesanan:
            bst.insert(int(item[4]), item[3])
        res = bst.range_search(10000, 20000)
        self.log(f"[M5] BST Search harga (10.000 - 20.000) menyaring {len(res)} item menu.")

    def test_m6(self):
        dist, path = self.graph.dijkstra("kantin-pusat", "asrama")
        self.log(f"[M6] Rute Terpendek 'kantin-pusat' -> 'asrama': {' -> '.join(path)} (Total: {dist} menit)")

if __name__ == "__main__":
    root = tk.Tk()
    app = App2EZ4U(root)
    root.mainloop()