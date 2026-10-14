def _ambil_kunci(baris, kunci):
    if kunci == "oid":
        return baris[0]
    elif kunci == "harga":
        return int(baris[4]) if baris[4] != "" else 0
    elif kunci == "selesai":
        # Kosong (belum selesai) diletakkan di paling akhir (nilai besar)
        return int(baris[7]) if len(baris) > 7 and baris[7] != "" else 999999999
    return baris[0]


def insertion_sort(arr, kunci="harga"):
    """Insertion sort stabil O(n^2). Mengembalikan (data_terurut, jml_perbandingan, jml_pemindahan)."""
    data = [x for x in arr]
    perbandingan = 0
    pemindahan = 0

    for i in range(1, len(data)):
        key_item = data[i]
        key_val = _ambil_kunci(key_item, kunci)
        j = i - 1
        while j >= 0:
            perbandingan += 1
            if _ambil_kunci(data[j], kunci) > key_val:  # '>' menjaga sifat stabil
                data[j + 1] = data[j]
                pemindahan += 1
                j -= 1
            else:
                break
        data[j + 1] = key_item
        pemindahan += 1

    return data, perbandingan, pemindahan


def merge_sort(arr, kunci="oid"):
    """Merge sort stabil O(n log n). Mengembalikan (data_terurut, jml_perbandingan, jml_pemindahan)."""
    pencacah = [0, 0]  # [perbandingan, pemindahan]

    def _urut(daftar):
        if len(daftar) <= 1:
            return daftar
        mid = len(daftar) // 2
        kiri = _urut(daftar[:mid])
        kanan = _urut(daftar[mid:])
        return _gabung(kiri, kanan)

    def _gabung(kiri, kanan):
        hasil = []
        i = 0
        j = 0
        while i < len(kiri) and j < len(kanan):
            pencacah[0] += 1
            # Pakai '<=' agar elemen kiri didahulukan saat kunci sama (stabil)
            if _ambil_kunci(kiri[i], kunci) <= _ambil_kunci(kanan[j], kunci):
                hasil.append(kiri[i])
                pencacah[1] += 1
                i += 1
            else:
                hasil.append(kanan[j])
                pencacah[1] += 1
                j += 1
        while i < len(kiri):
            hasil.append(kiri[i])
            pencacah[1] += 1
            i += 1
        while j < len(kanan):
            hasil.append(kanan[j])
            pencacah[1] += 1
            j += 1
        return hasil

    terurut = _urut([x for x in arr])
    return terurut, pencacah[0], pencacah[1]


def linear_search(arr, target_oid):
    """Linear search O(n). Mengembalikan (item, indeks, jml_perbandingan)."""
    perbandingan = 0
    for i in range(len(arr)):
        perbandingan += 1
        if arr[i][0] == target_oid:
            return arr[i], i, perbandingan
    return None, -1, perbandingan


def binary_search(sorted_arr, target_oid):
    """Binary search O(log n) pada data terurut oid. Mengembalikan (item, indeks, jml_perbandingan)."""
    lo = 0
    hi = len(sorted_arr) - 1
    perbandingan = 0

    while lo <= hi:
        mid = (lo + hi) // 2
        perbandingan += 1
        curr_oid = sorted_arr[mid][0]
        if curr_oid == target_oid:
            return sorted_arr[mid], mid, perbandingan
        elif curr_oid < target_oid:
            lo = mid + 1
        else:
            hi = mid - 1

    return None, -1, perbandingan
