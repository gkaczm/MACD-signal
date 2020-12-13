from matplotlib import pyplot as plt
import pandas as pd
fpath = "dane.csv"
kapitalInit = 1000
datalen = 1000


def srednia(max, data, index, colname):
    a = 1 - 2 / (max + 1)
    licznik = data.loc[index, colname]
    mianownik = 1
    for j in range(1, max + 1):
        licznik += (a ** j) * data.loc[index - j, colname]
        mianownik += a ** j
    srednia = licznik / mianownik
    return srednia


def macdf(data, len, colname):
    x = 12
    d = 26
    #ax = 1 - 2/(x+1)
    #ad = 1 - 2/(d+1)
    macd = data.copy()
    for i in range(len-1, d-1, -1):
        emax = srednia(d, data, i, colname)
        emad = srednia(x, data, i, colname)
        macd.at[i, colname] = emax - emad
    for i in range(0, d):
        macd.at[i, colname] = 0
    return macd


def signalf(data, len, colname):
    n = 9
    signal = data.filter([colname])
    for i in range(len-1, n-1, -1):
        ema = srednia(n, data, i, colname)
        signal.at[i, colname] = ema
    for i in range(0, n):
        signal.at[i, colname] = 0
    return signal


def investsim(nok, rates, msdf, ln, exchname, macdname, signalname):
#macd>signal - buy
    signalAboveMACD = True #zmienna służąca do monitorowania stanu signal>macd
    eur = 0
    hold = 0
    nokinit = nok
    for i in range(0, ln):
        if hold != 0:
            hold -= 1
        if msdf.loc[i, macdname] > msdf.loc[i, signalname] and signalAboveMACD == True:
            #kup
            if hold == 0 and nok!=0:
                eur = nok / rates.loc[i, exchname]
                nok = 0
                #print("buy")
                #print(rates.loc[i, "Data"]) # - program może drukować 'raport' działań
            hold = 23
            signalAboveMACD = False
        elif msdf.loc[i, macdname] < msdf.loc[i, signalname] and signalAboveMACD == False:
            #sprzedaj
            if hold == 0 and eur != 0:
                nok = eur * rates.loc[i, exchname]
                eur = 0
                #print("sell")
                #print(rates.loc[i, "Data"])
            hold = 23
            signalAboveMACD = True
    if nok == 0:
        nok = eur * rates.loc[ln-1, exchname]
    statystyka = (nok/nokinit)*100
    print("Kapitał końcowy to ", "%.2f" % statystyka, "% kapitału początkowego.")
    return 0

def checker(stats, ln, macdname, signalname): #FUNKCJA SPRAWDZZAJACA CZESTOTLIWOSC ZMIAN SIGNAL/MACD
    listofzeros = [0] * 35
    signalAboveMACD = True
    counter = -26
    highest = 0
    for i in range(0, ln):
        counter += 1
        if stats.loc[i, macdname] > stats.loc[i, signalname] and signalAboveMACD == True:
            signalAboveMACD = False
            listofzeros[counter] += 1
            if counter > highest:
                highest = counter
            counter = 0
        elif stats.loc[i, macdname] < stats.loc[i, signalname] and signalAboveMACD == False:
            signalAboveMACD = True
            listofzeros[counter] += 1
            if counter > highest:
                highest = counter
            counter = 0
    liszta = [0, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31, 32,33,34]
    plt.bar(liszta, listofzeros, align='center')
    plt.show()
    return listofzeros

data = pd.read_csv(fpath)
macd = macdf(data, datalen,'EUR/NOK')
signal = signalf(macd, datalen, 'EUR/NOK')
#todo: zamiast wrzucać te rzeczy do osobnych baz, powiększaj podstawową!
data = data.rename(columns={"Date" : "Data"})
data.plot(x = "Data", title = "Cena euro wyrażona w koronach norweskich (1000 dni)")
stats = macd.merge(signal, left_index=True, right_index=True)
stats = stats.rename(columns={"EUR/NOK_x": "MACD", "EUR/NOK_y": "SIGNAL"})
investsim(kapitalInit, data, stats, datalen, 'EUR/NOK', 'MACD', 'SIGNAL')
stats.plot(x = "Date", title = "Analiza MACD + SIGNAL")
plt.show()
liszt = checker(stats, datalen, 'MACD', 'SIGNAL') #-statystyki

