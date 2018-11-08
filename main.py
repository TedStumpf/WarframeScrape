#   Main.py
#   Will do more in the future
#   For now it calls WebData
from webdata import *
from random import randrange
from pprint import pprint

def main():
    data = get_data(True)
    #test01(data)
    #test02(data)
    #test03(data)
    test04(data)
    


def test01(data):
    pv = data['Prova Vandal']
    expand_data(pv)
    print(pv['name'])
    pprint(pv)
    df = data['Dex Furis']
    expand_data(df)
    print(df['name'])
    pprint(df)

def test02(data):
    detail = [randrange(len(data)) for i in range(5)]
    for d in detail:
        entry = list(data.items())[d]
        print('\n', entry[0])
        expand_data(entry[1])
        pprint(entry[1])

def test03(data):
    i = 0
    for key, val in data.items():
        print(key, end = "   ")
        expand_data(val)
        i += 1
        print(i, "/", len(data))

def test04(data):
    run = True
    while(run):
        inp = input("Enter a weapon name: ").lower()
        if inp == "quit":
            run = False
        else:
            if inp in data.keys():
                entry = data[inp]
                expand_data(entry)
                pprint(entry)
            else:
                print("Weapon not found")



main()