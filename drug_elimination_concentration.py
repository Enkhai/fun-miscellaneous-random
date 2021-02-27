import numpy as np


def plasma_concentration(c0, half_life, t):
    """
    Calculates drug plasma levels after a given time.
    :param c0: initial concentration, can be measured in any metric
    :param half_life: drug half-life measured in hours
    :param t: time passed after initial concentration
    :return: drug plasma levels after t time
    """
    k = np.log(2) / half_life
    return c0 * np.exp(-k * t)


def accumulative_concentration(dose, n, interval, half_life):
    """
    Calculates drug plasma levels after n regular doses, assumes instant drug plasma levels increase after each dose.
    :param dose: amount of regular dose
    :param n: number of doses
    :param interval: number of hours between each dose
    :param half_life: drug half-life measured in hours
    :return: drug plasma levels after n doses
    """
    concentration = dose
    for _ in range(n):
        concentration = plasma_concentration(concentration, half_life, interval) + dose

    return concentration


if __name__ == '__main__':
    d = 14
    hl = 456

    acc_2month = accumulative_concentration(d, 60, 24, hl)
    three_day_skip = plasma_concentration(acc_2month, hl, 72)
    print("Accumulation of drug after 2 months in mg: " + str(acc_2month))
    print("Plasma levels after skipping drug for 3 days: " + str(three_day_skip))
    print("Plasma levels after skipping drug and taking a dose: " + str(three_day_skip + d))
    print(plasma_concentration(three_day_skip + d, hl, 48))
