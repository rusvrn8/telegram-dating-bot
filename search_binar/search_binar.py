def search_binar(lst, item):
    low = 0
    high = len(lst) - 1
    while low <= high:
        mid = (high + low)//2
        val = lst[mid]
        if val == item:
            return mid
        elif val < item:
            low = mid + 1
        else:
            high = mid - 1
    return None


if __name__ == '__main__':
    my_list = [1, 4, 6, 43, 65]
    print(search_binar(my_list, 1))