#Question 1: Swap Case
def swap_case(s):
    res = ''
    for ch in s:
        if ch.isupper():
            res += ch.lower()
        else:
            res += ch.upper()
    return res

if __name__ == '__main__':
    s = input()
    result = swap_case(s)
    print(result)


#Question 2:




#Question 3:



#Question 4: