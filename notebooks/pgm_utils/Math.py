import numpy as np
def product(a, b, step=1):
    if a==b:
        return a
    result = 1
    for i in range(a, b+1, step):
        result *= i
    return result

def perm(n, r):
    if r==0:
        return 1
    return product(n-r+1, n)

def comb(n, r):
    return perm(n, r)/product(1, r)
