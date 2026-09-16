def insertion_sort_by_harga(arr):
    # Mengurutkan array of tuples/lists berdasarkan harga (index 4)
    data = [x for x in arr]
    for i in range(1, len(data)):
        key = data[i]
        j = i - 1
        while j >= 0 and int(data[j][4]) > int(key[4]):
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key
    return data

def binary_search_by_oid(sorted_arr, target_oid):
    left = 0
    right = len(sorted_arr) - 1
    while left <= right:
        mid = (left + right) // 2
        curr_oid = sorted_arr[mid][0]
        if curr_oid == target_oid:
            return sorted_arr[mid]
        elif curr_oid < target_oid:
            left = mid + 1
        else:
            right = mid - 1
    return None