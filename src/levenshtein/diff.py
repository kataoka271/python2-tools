def compare(x, y):
    return x == y or (y == '.' and not 0x20 <= ord(x) <= 0x7E)


def diffget(raw, asc):
    m = len(raw)
    n = len(asc)
    u = {}
    v = {}
    offset = m + n
    d = 0
    while d <= m + n:
        k = -d
        while k <= d:
            if d == 0:
                w = ""
                i = 0
            elif k == -d:
                w = u[offset + k + 1]
                i = v[offset + k + 1] + 1  # delete
            elif k == d:
                w = u[offset + k - 1]
                i = v[offset + k - 1]  # insert
                w = w + asc[i + k - 1]
            else:
                if v[offset + k + 1] + 1 >= v[offset + k - 1]:
                    w = u[offset + k + 1]
                    i = v[offset + k + 1] + 1  # delete
                else:
                    w = u[offset + k - 1]
                    i = v[offset + k - 1]  # insert
                    w = w + asc[i + k - 1]
                # i = max(v[offset + k + 1] + 1, v[offset + k - 1])
            while i < m and i + k < n and compare(raw[i], asc[i + k]):  # raw[i] == asc[i + k]:
                w = w + raw[i]
                i += 1
            if k == n - m and i == m:
                return d, w
            u[offset + k] = w
            v[offset + k] = i
            k += 2
        d += 1
    raise Exception("The routine has unexpectedly finished")


if __name__ == "__main__":
    print diffget("ki\x01\x02tten", "si..tting xyz")
