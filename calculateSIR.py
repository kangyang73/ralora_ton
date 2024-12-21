# -*- coding: UTF-8 -*-

import math
import random
import time
from itertools import islice
from itertools import combinations
import numpy as np
import sys

def getDistance(path):

    distanceList = []
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
            distanceList.append(float(dis))
            sf_index = int(linetmpId[5])
            if sf_index == 0:
                sf = 12
            elif sf_index == 1:
                sf = 11
            elif sf_index == 2:
                sf = 10
            elif sf_index == 3:
                sf = 9
            elif sf_index == 4:
                sf = 8
            else:
                sf = 7
            sfList.append(sf)

    return distanceList, sfList

def getTOA(sf, pl, cr, bandWidth):
    # unit: s

    t_sym = (math.pow(2, sf) * 1.0) / (bandWidth * 1.0)
    t_preamble = (8 + 4.25) * t_sym
    de = 1  # DE = 1 when the low data rate optimization is enabled , DE = 0 for disabled.
    h = 0   # h = 0 when the header is enabled and h = 1 when no header is present.
    n_payload = 8 + max(math.ceil((8 * pl - 4 * sf + 28 + 16 - 20 * h) * 1.0 / (4.0 * (sf - 2 * de))) * (cr + 4), 0)
    t_payload = n_payload * t_sym
    t_packet = t_preamble + t_payload

    return round(t_packet, 3)

def getRxPower(dis):
    m_exponent = 3.0

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

    maxRxPowerLinear = pow(10.0, rtxPowerDbm / 10.0) / 1000.0		# in Watts

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
    h = 0   # h = 0 when the header is enabled and h = 1 when no header is present.
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

def getSIR(dis, configureList, distanceList, sf):

    maxRxPowerLinear = getRxPower(dis)
    # noisePowerLinear = 0.000000000000005

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
    Ns = int(len(indexList) / 2)
    # Ns = 20
    la = (Ns * 1.0) / (5 * 60)
    tp = getTOA(sf, 32, 1, 125000)
    pa_t = la * 2 * tp

    symPro = getSymPro(sf)

    intra = 0.0
    for i in range(Ns):
        k = i + 1
        h_k = symPro * math.exp(-pa_t) * pow(pa_t, k) * 1.0 / (factorial(k))

        t_sum = 0.0
        #combinations_list = list(combinations(receivedpowerList, k))[0]
        combinations_list = getcombinationlist(receivedpowerList, k)
        for li in combinations_list:
            #print(li)
            try:
                t_li = sum(li)
            except TypeError as e:
                t_li = li
            
            t_sum = t_sum + t_li
        t_sum = (t_sum * 1.0) / len(combinations_list)

        intra = intra + t_sum * h_k

    return intra

def writeToFile(path_LoRaWAN, outpath_LoRaWAN, intraDict):

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
        # DeviceType = linetmpId[1]
        ID = int(linetmpId[0]) - gateway_num
        intra = intraDict[ID]

        strr = linetmp + "," + str(intra) + "\n"

        out.write(strr)

    out.close()

if __name__ == '__main__':

    scpritName = sys.argv[0]
    method = sys.argv[1]  # LoRaWAN2, LoRaICNP2, LoRaWANAT2

    # path_ATLoRa = "/home/conn/Desktop/workspace/LoRaWANAT2/src/lorawan/model/nodes.csv"
    path_LoRaWAN = "/home/conn/Desktop/workspace/" + method + "/src/lorawan/model/nodes1.csv"
    # path_LoRaWAN = "./nodes.csv"

    distanceList, sfList = getDistance(path_LoRaWAN)

    noise = 5.00359e-16
    # noisePowerLinear = 0.000000000000005  # 5e-15
    # print(noisePowerLinear)

    outpath_LoRaWAN = "/home/conn/Desktop/workspace/" + method + "/src/lorawan/model/nodes2.csv"
    # outpath_LoRaWAN = "./nodess.csv"

    intraDict = {}
    for i in range(len(distanceList)):
        nodeId = i
        dis = distanceList[nodeId]
        sf = sfList[nodeId]

        intra = getSIR(dis, sfList, distanceList, sf)
        intraDict[nodeId] = intra
        # print(i, intra)

    writeToFile(path_LoRaWAN, outpath_LoRaWAN, intraDict)
