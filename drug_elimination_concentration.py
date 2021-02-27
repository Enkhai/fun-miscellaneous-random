import numpy as np


def plasma_concentration(c0, rate, t):
    k = np.log(2) / rate
    return c0 * np.exp(-k * t)


def accumulative_concentration(dose, n, interval, rate):
    conc = dose
    for _ in range(n):
        conc = plasma_concentration(conc, rate, interval) + dose

    return conc


if __name__ == '__main__':
    dose = 14
    rate = 456

    acc_2month = accumulative_concentration(dose, 60, 24, rate)
    three_day_skip = plasma_concentration(acc_2month, rate, 72)
    print("Accumulation of drug after 2 months in mg: " + str(acc_2month))
    print("Plasma levels after skipping drug for 3 days: " + str(three_day_skip))
    print("Plasma levels after skipping drug and taking a dose: " + str(three_day_skip + dose))
