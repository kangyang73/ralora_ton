# -*- coding: UTF-8 -*-

import math
import random
import time
from itertools import islice
from itertools import combinations
import numpy as np


def getDistance2(path):
    distance = []
    sfList = []

    input_file = open(path)
    i = 0
    for line in islice(input_file, 0, None):
        if i < 2:
            i = i + 1
            continue
        linetmp = line.replace("\n", "")
        linetmpId = linetmp.split(",")
        DeviceType = linetmpId[1]
        dis = linetmpId[4]
        # dataRateIndex = linetmpId[5]
        if DeviceType == "1":
            distance.append(float(dis))
            x_def = int(linetmpId[5])
            # print(x_def)
            if x_def == 0:
                x = 12
            elif x_def == 1:
                x = 11
            elif x_def == 2:
                x = 10
            elif x_def == 3:
                x = 9
            elif x_def == 4:
                x = 8
            else:
                x = 7

            sfList.append(x)

    return distance, sfList

def getTOA(sf, pl, cr, bandWidth):
    # unit: s

    t_sym = (math.pow(2, sf) * 1.0) / (bandWidth * 1.0)
    t_preamble = (8 + 4.25) * t_sym
    de = 1  # DE = 1 when the low data rate optimization is enabled , DE = 0 for disabled.
    h = 0  # h = 0 when the header is enabled and h = 1 when no header is present.
    n_payload = 8 + max(math.ceil((8 * pl - 4 * sf + 28 + 16 - 20 * h) * 1.0 / (4.0 * (sf - 2 * de))) * (cr + 4), 0)
    t_payload = n_payload * t_sym
    t_packet = t_preamble + t_payload

    return round(t_packet, 3)

def getRxPower(dis):
    m_exponent = 3.01

    txPowerDbm = 14
    # rtxPowerDbm = 0.0
    m_referenceDistance = 1.0
    m_referenceLoss = 46.6777
    distance = float(dis)

    if (distance <= m_referenceDistance):
        rtxPowerDbm = txPowerDbm
    else:
        pathLossDb = 10 * m_exponent * math.log10(distance / m_referenceDistance)
        rxc = -m_referenceLoss - pathLossDb

        rtxPowerDbm = txPowerDbm + rxc

    maxRxPowerLinear = pow(10.0, rtxPowerDbm / 10.0) / 1000.0  # in Watts

    return maxRxPowerLinear

def factorial(n):
    res = 1
    for i in range(1, n + 1):
        res = res * i

    return res

def getcombinationlist(receivedpowerList, k):
    combinationList = []

    if len(receivedpowerList) > k:
        for index in range(len(receivedpowerList)):
            end = (index + k)
            if end <= len(receivedpowerList):
                tempList = receivedpowerList[index: end]
                combinationList.append(tempList)
    else:
        combinationList.append(receivedpowerList)

    return combinationList

def getNumSym(sf, pl, cr, bandWidth):
    # unit: s

    t_sym = (math.pow(2, sf) * 1.0) / (bandWidth * 1.0)
    t_preamble = (8 + 4.25) * t_sym
    de = 1  # DE = 1 when the low data rate optimization is enabled , DE = 0 for disabled.
    h = 0  # h = 0 when the header is enabled and h = 1 when no header is present.
    n_payload = 8 + max(math.ceil((8 * pl - 4 * sf + 28 + 16 - 20 * h) * 1.0 / (4.0 * (sf - 2 * de))) * (cr + 4), 0)

    numSym = math.ceil(n_payload + t_preamble)

    return numSym

def getSymPro(sf):
    numSy = getNumSym(sf, 32, 1, 125000)
    d = 1.0 / (numSy * 1.0)

    t = 0.0
    for i in range(numSy):
        s = i + 1

        t = t + (s * d)
    re = t * d

    return re

def getSNR2(dis, configureList, distanceList, sf):
    maxRxPowerLinear = getRxPower(dis)
    # noisePowerLinear = random.uniform(0.0000000000000001, 0.000000000000001)
    # noisePowerLinear = 0.000000000000005
    noisePowerLinear = 5.00359e-16

    indexList = []
    for index in range(len(configureList)):
        if configureList[index] == sf:
            indexList.append(index)

    receivedpowerList = []
    for index in indexList:
        dis_t = distanceList[index]
        maxRxPowerLinear_t = getRxPower(dis_t)
        receivedpowerList.append(maxRxPowerLinear_t)

    # Ns = len(indexList)
    Ns = math.ceil(len(indexList) / 3)
    # Ns = 10
    la = (Ns * 1.0) / (15 * 60)
    tp = getTOA(sf, 32, 1, 125000)
    pa_t = la * 2 * tp

    # symPro = getSymPro(sf)
    symPro = 100

    intra = 0.0
    for i in range(1):
        k = i + 1
        h_k = symPro * math.exp(-pa_t) * pow(pa_t, k) * 1.0 / (factorial(k))

        t_sum = 0.0
        # combinations_list = list(combinations(receivedpowerList, k))[0]
        combinations_list = getcombinationlist(receivedpowerList, k)
        for li in combinations_list:
            try:
                t_li = sum(li)
            except TypeError as e:
                t_li = li

            t_sum = t_sum + t_li
        t_sum = (t_sum * 1.0) / len(combinations_list)

        intra = intra + t_sum * h_k

    noisePowerLinear = noisePowerLinear + intra
    snrDb = maxRxPowerLinear / noisePowerLinear

    return snrDb

def getBer(snr, sf):
    N = pow(2, sf) - 1
    sqrt_snr = pow(snr * (N + 1), 0.5)

    H_N = math.log(N) + (1.0 / (2 * N)) + 0.57722

    pi = 3.141592653
    pi_12 = pow(pi, 2) / 12.0
    temp = pow(H_N, 2) - pi_12
    top = sqrt_snr - pow(temp, 0.25)
    temp2 = H_N - pow(temp, 0.5) + 0.5
    bottom = pow(temp2, 0.5)

    x = top / bottom
    ber = 0.5 * 0.5 * math.erfc(x / pow(2, 0.5))
    # print("ber", ber, snr, 10*math.log10(snr), sf)

    return ber

def getPacketlength2(sf, dis, configureList, distanceList):
    snr = getSNR2(dis, configureList, distanceList, sf)

    ber = getBer(snr, sf)

    bs = 2  # payload: 32, bn: 16
    blrr = pow(1 - ber, (bs + 1) * 8.0)

    bn_gg = math.ceil(32 * 1.0 / (bs * blrr))
    ds = (bs + 1) * bn_gg

    return ds, ber

def calculateLifetime2(sf, dis, configureList, distanceList):
    t_cycle = 0.5 * 60
    e_batt = 3600 * 10 * 5 * 1.0

    p_mcu_on = 0.02348
    p_mcu_off = 1.7465 * pow(10, -6)
    p_r_off = 9.9 * pow(10, -5)
    p_r_tx = 0.30

    packetlength, ber = getPacketlength2(sf, dis, configureList, distanceList)

    toa = getTOA(sf, packetlength, 1, 125000)
    transimission_time = toa

    e_cycle = (t_cycle - transimission_time) * (p_mcu_off + p_r_off) + transimission_time * (p_r_tx + p_mcu_on)

    node_life_t = t_cycle * (e_batt / e_cycle)
    node_life = (node_life_t * 1.0) / (3600.0 * 24 * 365)

    # wrongBits = math.ceil(packetlength * ber)
    # print("wrongBits", wrongBits)
    # if wrongBits > 4:
    #     node_life = 0

    return node_life

def getCollisionProb(sf, sf_num):
    Ns = int(sf_num)

    la = (Ns * 1.0) / (15 * 60)
    tp = getTOA(sf, 32, 1, 125000)
    pa_t = la * 2 * tp

    h_0 = math.exp(-pa_t) * pow(pa_t, 0) * 1.0 / 1

    collision = 1 - h_0

    return collision

def getCollision(configureList):
    sfDisDict = {}

    for sf in configureList:
        if sf not in sfDisDict:
            sfDisDict[sf] = 1
        else:
            sfDisDict[sf] = sfDisDict[sf] + 1

    sfProb = []
    for sf_k in sfDisDict:
        sf_num = sfDisDict[sf_k]
        prob = getCollisionProb(sf_k, sf_num)
        sfProb.append(prob)

    sfProb_var = float(np.var(sfProb))

    return sfProb_var

def minLifetime2(configureList, distanceList):
    lifetimeList = []
    for i in range(len(configureList)):
        sf = configureList[i]
        dis = distanceList[i]
        lifetime = calculateLifetime2(sf, dis, configureList, distanceList)
        lifetimeList.append(lifetime)

    minLifetime = min(lifetimeList)
    maxLifetime = max(lifetimeList)

    sum_lf = 0
    for lf in lifetimeList:
        lf_t = ((lf - minLifetime) * 1.0) / ((maxLifetime - minLifetime) * 1.0)
        sum_lf = sum_lf + lf_t

    # print(configureList)
    # print(lifetimeList)
    # print(minimumLifetime)

    return round((sum_lf * 1.0) / len(lifetimeList), 4)

def getsf(configureList):
    ns_def = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    for x_def in configureList:
        if x_def == 7:
            ns_def[0] += 1
        elif x_def == 8:
            ns_def[1] += 1
        elif x_def == 9:
            ns_def[2] += 1
        elif x_def == 10:
            ns_def[3] += 1
        elif x_def == 11:
            ns_def[4] += 1
        elif x_def == 12:
            ns_def[5] += 1

    sum_list = sum(ns_def)

    te = []
    for val in ns_def:
        x = val * 1.0 / sum_list
        te.append(x)

    arr_mean = np.mean(te)

    arr_std = np.std(te, ddof=1)
    arr_var = np.var(te)

    print("sf distribution:", arr_mean, arr_std, arr_var, te)

    return te

def writeToFile(path_LoRaWAN, outpath_LoRaWAN, sfDict):
    gateway_num = 1
    out = open(outpath_LoRaWAN, "w")

    input_file = open(path_LoRaWAN)
    i = 0
    for line in islice(input_file, 0, None):
        if i < 1 + gateway_num:
            out.write(line)
            i = i + 1
            continue
        linetmp = line.replace("\n", "")
        linetmpId = linetmp.split(",")

        DeviceType = linetmpId[0]
        NodeId = linetmpId[1]
        Position_x = linetmpId[2]
        Position_y = linetmpId[3]
        DistanceToClosestGW = linetmpId[4]
        DataRateIndex = linetmpId[5]

        ID = int(DeviceType) - gateway_num
        sf = sfDict[ID]
        if sf == 12:
            sf_index = 0
        elif sf == 11:
            sf_index = 1
        elif sf == 10:
            sf_index = 2
        elif sf == 9:
            sf_index = 3
        elif sf == 8:
            sf_index = 4
        else:
            sf_index = 5

        strr = DeviceType + "," + NodeId + "," + Position_x + "," + Position_y + "," + DistanceToClosestGW + "," + str(
            sf_index) + "\n"

        out.write(strr)

    out.close()

def runAlgo(path):
    distanceList, alloc_0 = getDistance2(path)
    # print("alloc_0: ", alloc_0)

    alloc_n = []
    for i in alloc_0:
        alloc_n.append(i)

    minLife = minLifetime2(alloc_0, distanceList)
    minLife0 = minLife

    delta = 0.1
    # sfList = [7, 8, 9, 10, 11, 12]
    # sfList = [7, 8, 9, 10, 11, 12][::-1]
    print("minLife0", minLife0)

    while True:
        for i in range(len(alloc_0)):
            sf = alloc_0[i]
            dis = distanceList[i]
            if ((sf == 10) and (dis > 3000)):
                continue
            # if ((sf == 9) and (dis > 2500)):
            #     continue
            # if ((sf == 8) and (dis > 2000)):
            #     continue
            # if ((sf == 7) and (dis > 3000)):
            #     continue
            if (sf == 7):
                sfList = [sf, sf + 1]
            elif ((sf > 7) and (sf < 10)):
                sfList = [sf - 1, sf, sf + 1]
            else:
                sfList = [sf - 1, sf]
            tList = []
            for s in sfList:
                st_t = time.time()
                s_t = alloc_0[i]
                alloc_0[i] = s
                minLife_t = minLifetime2(alloc_0, distanceList)
                alloc_0[i] = s_t
                # print("Node ID: " + str(i) + " === SF: " + str(s) + " === MinLife_t: " + str(minLife_t))
                if minLife_t > minLife:
                    minLife = minLife_t
                    # alloc_n[i] = s
                    alloc_0[i] = s
                    print("=================")
                    print("Node ID: " + str(i + 1) + " === OriSF: " + str(sf) + " === NewSF: " + str(s) + " === minLife: " + str(minLife))
                en_t = time.time()
                tList.append(en_t - st_t)
                print("time", en_t - st_t)

            print("timeeeeeeeeee", np.mean(tList))

        diff = abs(minLife - minLife0)

        minLife0 = minLife
        print("diff", diff)
        if diff < delta:
            break

    print("old alloc: ", alloc_n)
    getsf(alloc_n)

    print("new alloc: ", alloc_0)
    getsf(alloc_0)

    print("\n")
    print(distanceList)

    sfDict = {}

    for i in range(len(alloc_0)):
        sfDict[i] = alloc_0[i]

    return sfDict


if __name__ == '__main__':
    path = "/home/conn/Desktop/workspace/LoRaWANAT2/src/lorawan/model/nodes.csv"

    # path = "/home/conn/Desktop/workspace/LoRaWAN2/output/temp.csv"
    # path = "distance-5-3000.txt"
    # nodes = 100

    outpath = "/home/conn/Desktop/workspace/LoRaWANAT2/src/lorawan/model/nodes1.csv"

    start = time.clock()
    sfDict = runAlgo(path)

    end = time.clock()

    print(end - start)
    # writeToFile(path, outpath, sfDict)
