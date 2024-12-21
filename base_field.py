# -*- coding: UTF-8 -*-

from itertools import islice
import os
import sys
import operator
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib
import shutil
import datetime


# freq = "904300000"  # file_to_dict
# codingRate = "45"  # file_to_dict
# codeDict = {"30": "0", "31": "1", "32": "2", "33": "3", "34": "4", "35": "5", "36": "6", "37": "7", "38": "8",
#             "39": "9"}  # file_to_dict
# packetsize = 64  # frame size. # file_to_dict, GetSentData
# nodeIDList = ["01", "02", "03", "04", "05", "06", "07", "08"]  # file_to_dict
# sfList = ["SF7", "SF8", "SF9"]  # define all SF that all nodes used.   # file_to_dict
# nodeSFDict = {"01": "SF7", "02": "SF8", "03": "SF8", "04": "SF7", "05": "SF8", "06": "SF9", "07": "SF9", "08": "SF8"}  # file_to_dict
# up_line = 0   # decided by start time of experiment.  #file_to_dict
# down_line = 150000  #file_to_dict
#
# # 64 also is used in GetSentData. formalize originalData from int to str. make sure its length must be 64.  # GetSentData
#
# payloadSize = 32  # parselog_lorawan
#
# nodeLorawanList = ["05", "06", "07", "08"]  # parselog_lorawan
#
# # nodeIcnpList = ["01", "02", "03", "04"]  # parselog_icnp, parselog_atlora, parselog_atlora_ber
#
# nodeIcnpList = ["05", "06", "07", "08"]  # parselog_icnp, parselog_atlora, parselog_atlora_ber
#
# nodeDict = {"01": "05", "02": "06", "03": "07", "04": "08", "05": "01", "06": "02", "07": "03", "08": "04"}  # findPacket
#
# slot = 1  # mean_ber


freq = "904300000"  # file_to_dict
codingRate = "45"  # file_to_dict
codeDict = {"30": "0", "31": "1", "32": "2", "33": "3", "34": "4", "35": "5", "36": "6", "37": "7", "38": "8",
            "39": "9"}  # file_to_dict
packetsize = 64  # frame size. # file_to_dict, GetSentData
nodeIDList = ["01", "02", "03", "04", "05", "06", "07", "08"]  # file_to_dict
sfList = ["SF8", "SF9", "SF10"]  # define all SF that all nodes used.   # file_to_dict
nodeSFDict = {"01": "SF9", "02": "SF8", "03": "SF8", "04": "SF9", "05": "SF10", "06": "SF9", "07": "SF9",
              "08": "SF10"}  # file_to_dict
up_line = 0  # decided by start time of experiment.  #file_to_dict
down_line = 100000000  # file_to_dict

# 64 also is used in GetSentData. formalize originalData from int to str. make sure its length must be 64.  # GetSentData

payloadSize = 32  # parselog_lorawan

nodeLorawanList = ["05", "06", "07", "08"]  # parselog_lorawan

# nodeIcnpList = ["01", "02", "03", "04"]  # parselog_icnp, parselog_atlora, parselog_atlora_ber
nodeIcnpList = ["05", "06", "07", "08"]  # parselog_icnp, parselog_atlora, parselog_atlora_ber

nodeDict = {"01": "05", "02": "06", "03": "07", "04": "08", "05": "01", "06": "02", "07": "03",
            "08": "04"}  # findPacket
slot = 1  # mean_ber


def isContainAphpa(string):
    my_re = re.compile(r'[A-Za-z]')

    return bool(re.match(my_re, string))

def is_number(string):
    try:
        float(string)
        return True
    except Exception as e:
        # print("is_number Function Error: ", e)
        return False

def strToHex(string):
    hex_int = int(string, 16)

    return hex_int

def asciiToBin(string):
    ## 3030 -> 00  hexdecimal to string
    outList = []
    for i in range(0, len(string), 2):
        asciiCode = string[i: i+2]
        binNum = chr(strToHex(asciiCode))
        #print(asciiCode, binNum)
        if not is_number(binNum):
            binNum = "X"

        outList.append(binNum)

    outStr = "".join(["" + s for s in outList])
    return outStr

def asciiToBin2(string):
    ## 3030 -> 0011 0000 0011 0000  hexdecimal to binary
    outList = []
    for i in range(0, len(string), 2):
        hexCode = string[i: i + 2]
        intNum = int(hexCode, 16)
        binNum = bin(intNum).replace('0b', '00').rjust(8, '0')[-8:]

        outList.append(binNum)

    outStr = "".join(["" + s for s in outList])
    # print(outStr)
    return outStr

def stringToBin(string):
    ## 00 -> 00110000 00110000  sting to binary
    outList = []
    for d in string:
        intNum = ord(d)
        binNum = bin(intNum).replace('0b', '00')[-8:]
        outList.append(binNum)

    outStr = "".join(["" + s for s in outList])
    # print(outStr)
    return outStr

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        print("The folder is already existing!")

def deledir(path):
    folder = os.path.exists(path)
    if not folder:
        pass
    else:
        shutil.rmtree(path)

def file_to_dict(filedir):

    # return: data[nodeID] = [(datarate, utcTime, payload, status, rssi, SNR)]

    filelists = os.listdir(filedir)
    data = {}

    j = 0
    for file in filelists:
        if not file.endswith(".csv"):
            continue
        filename = filedir + file

        input_file = open(filename)

        for line in islice(input_file, 0, None):
            j = j + 1
            if (j < up_line) or (j > down_line):
                continue
            line = line.replace(")", "").replace("'", "").replace('"', '').replace('\n', '')
            if not line.startswith("gateway"):
                try:
                    eachline = line.split(',')
                    # print(eachline)
                    utcTime = eachline[2][: -1]  # 2020-02-12 02:43:54.012Z delete last string Z.
                    frequency = eachline[4].replace(" ", "")
                    status = eachline[7].replace(" ", "")  # CRC_OK or CRC_BAD
                    datarate = eachline[11].replace(" ", "")  # SF*
                    codeRate = eachline[12].replace(" ", "").replace("/", "")
                    rssi = eachline[13].replace(" ", "")
                    SNR = eachline[14].replace(" ", "")
                    string = eachline[15].replace(" ", "").replace("-", "")

                    if (frequency == freq) and (codeRate == codingRate) and (datarate in sfList):
                        # continue
                        # payload = asciiToBin(string)
                        payload = string  # 3030 hexadecimal
                        # print(payload)
                        if (len(payload) == packetsize * 2):

                            nodeIDtemp = payload[0: 4]
                            try:
                                nodeID = codeDict[nodeIDtemp[0: 2]] + codeDict[nodeIDtemp[2: 4]]
                            except KeyError as e:
                                continue

                            if nodeID not in nodeIDList:
                                continue

                            if datarate != nodeSFDict[nodeID]:
                                continue

                            if nodeID not in data:
                                data[nodeID] = [(datarate, utcTime, payload, status, rssi, SNR)]
                            else:
                                data[nodeID].append((datarate, utcTime, payload, status, rssi, SNR))
                except IndexError as e:
                    # print("file_to_dict Function IndexError: ", e)
                    pass
    sorted_data = {}
    lenList = []
    for node in data:
        node_packets = data[node]
        lenList.append(len(node_packets))
        sorted_packets = sorted(node_packets, key=lambda x: (x[0], x[1]))

        # if node not in sorted_data:
        sorted_data[node] = sorted_packets

    for key in sorted(sorted_data):
        print("Summing data === NodeID: " + str(key) + " Packet number: " + str(len(sorted_data[key])))

    # min_len = min(lenList)
    # final_data = {}
    # for node in sorted_data:
    #     node_packets = sorted_data[node]
    #     final_data[node] = node_packets[0: min_len]
    #
    # for key in sorted(final_data):
    #     print("Second summing data === NodeID: " + str(key) + " Packet number: " + str(len(final_data[key])))

    return sorted_data

def GetSentData(dataDict):
    outDataDict = {}

    for node in dataDict:
        out_payloadlist = []
        # print(type(node), node)
        # print(dataDict)
        payloadlist = dataDict[node]

        # asciiToBin  # 3030 -> 00
        # asciiToBin2  # 3030 -> 00110000 00110000
        # stringToBin  # 00 -> 00110000 00110000

        # innitialize first data. originalData: the packet that node sends. (datarate, utcTime, payload, status, rssi, SNR)
        if payloadlist[0][3] == "CRC_OK":
            originalData = asciiToBin(payloadlist[0][2])  # payload = asciiToBin(string)
        else:
            st = "".join("0" + "" for x in range(packetsize - 2))
            originalData = node + st

        # for payload in payloadlist: (datarate, utcTime, payload, status, rssi, SNR)
        for d in range(len(payloadlist)):

            payload = payloadlist[d]
            sf = payload[0]
            utcTime = payload[1]
            packet = payload[2]  # received packet by gateway.
            status = payload[3]
            rssi = payload[4]
            SNR = payload[5]

            decimal_packet = asciiToBin(packet)  # 3030 -> 00

            binary_sent = stringToBin(originalData)   # 00 -> 00110000 00110000
            binary_received = stringToBin(decimal_packet)   # 00 -> 00110000 00110000

            out_str_list = []

            for x, y in zip(binary_received, binary_sent):
                # print(x, y, x==y)
                if x == y:
                    out_str_list.append(x)
                else:
                    out_str_list.append("9")

            outBinaryPacket = "".join(["" + s for s in out_str_list])
            out_payload = [sf, utcTime, outBinaryPacket, status, rssi, SNR]
            out_payloadlist.append(out_payload)

            if d <= len(payloadlist) - 2:
                nextSf = payloadlist[d + 1][0]
                nextUtcTime = payloadlist[d + 1][1]
                nextPacket= asciiToBin(payloadlist[d + 1][2])
                nextStatus = payloadlist[d + 1][3]
                nextRssi = payloadlist[d + 1][4]
                nextSNRs = payloadlist[d + 1][5]

                try:
                    difference = int(nextPacket) - int(originalData)
                except Exception as e:
                    difference = 1

                originalData = int(originalData) + difference

                if not isinstance(originalData, str):
                    originalData = "%064d" % int(originalData)

        outDataDict[node] = out_payloadlist

    # for node in sorted(outDataDict):
    #     print(node, len(outDataDict[node]))

    return outDataDict

def parselog_lorawan(dataDict):
    finalDataDict = {}

    for node in dataDict:

        if node not in nodeLorawanList:
            continue

        payloadlist = dataDict[node]

        # for payload in payloadlist: (datarate, utcTime, binary payload, status, rssi, SNR)
        for d in range(len(payloadlist)):

            payload = payloadlist[d]
            sf = payload[0].replace("SF", "")
            utcTime = payload[1]
            binary_packet = payload[2]  # received packet by gateway.
            status = payload[3]
            rssi = payload[4]
            SNR = payload[5]
            # if node == "07":
            #     print("SF", sf)

            # bits = binary_packet[0: (payloadSize * 8)] + "," + sf
            bits = binary_packet[-(payloadSize * 8):] + "," + sf

            if node not in finalDataDict:
                finalDataDict[node] = [bits]
            else:
                finalDataDict[node].append(bits)

    # print(len(finalDataDict))

    return finalDataDict

def parselog_icnp(dataDict):
    finalDataDict = {}

    for node in dataDict:

        if node not in nodeIcnpList:
            continue

        payloadlist = dataDict[node]

        # for payload in payloadlist: (datarate, utcTime, binary payload, status, rssi, SNR)
        for d in range(len(payloadlist)):

            payload = payloadlist[d]
            sf = int(payload[0].replace("SF", ""))
            utcTime = payload[1]
            binary_packet = payload[2]  # received packet by gateway.
            status = payload[3]
            rssi = payload[4]
            SNR = payload[5]

            float_snr = pow(10, float(SNR) / 10.0)
            # print(node, sf)
            sf_opt, bs_opt, bn_opt = getSFBsBnIcnp(float_snr, sf, node)
            # sf_opt = sf - 1
            # if node == "05":
            #     print("SF", sf_opt)
            if node == "05":
                sf_opt = sf
            # if node == "06":
            #     sf_opt = sf

            # bs = 2
            # bn = 16
            byteSize = (bs_opt + 1) * bn_opt

            if sf_opt == sf:
                binary_packet_opt = binary_packet
            else:
                binary_packet_opt = findPacket(utcTime, node, dataDict)

            # if node == "05":
            #     print("SF", sf_opt)

            bits = binary_packet_opt[0: (byteSize * 8)] + "," + str(sf_opt)
            # bits = binary_packet_opt[-(payloadSize * 8):] + "," + str(sf_opt)

            if node not in finalDataDict:
                finalDataDict[node] = [bits]
            else:
                finalDataDict[node].append(bits)

    # print(len(finalDataDict))

    return finalDataDict

def parselog_atlora(dataDict):
    finalDataDict = {}

    for node in dataDict:

        if node not in nodeIcnpList:
            continue

        payloadlist = dataDict[node]

        # for payload in payloadlist: (datarate, utcTime, binary payload, status, rssi, SNR)
        for d in range(len(payloadlist)):

            payload = payloadlist[d]
            sf = int(payload[0].replace("SF", ""))
            utcTime = payload[1]
            binary_packet = payload[2]  # received packet by gateway.
            status = payload[3]
            rssi = payload[4]
            SNR = payload[5]

            float_snr = pow(10, float(SNR) / 10.0)
            # print(node, sf)
            sf_opt, bs_opt, bn_opt = getSFBsBn(float_snr, sf, node)

            # if node == "07":
            #     sf_opt, bs_opt, bn_opt = getSFBsBnIcnp(float_snr, sf, node)

            # if node == "05":
            #     sf_opt = sf
            # if node == "08":
            #     sf_opt = sf
            # if node == "06":
            #     sf_opt = sf


            # sf_opt = sf
            # binary_packet_opt = binary_packet
            if sf_opt == sf:
                binary_packet_opt = binary_packet
            else:
                binary_packet_opt = findPacket(utcTime, node, dataDict)
                # binary_packet_opt = binary_packet
                # print("======")
                # print(type(binary_packet_opt), binary_packet_opt)
            if bs_opt != payloadSize:
                binary_size = (bs_opt + 1) * bn_opt * 8
            else:
                binary_size = (bs_opt) * bn_opt * 8

            di = binary_size - len(binary_packet_opt)
            # print(type(binary_packet_opt), binary_packet_opt)

            if (di > 0):
                for i in range(di):
                    binary_packet_opt = binary_packet_opt + "0"
            else:
                binary_packet_opt = binary_packet_opt[0: binary_size]

            # if node == "05":
            #     print("SF", sf_opt)

            bits = binary_packet_opt + "," + str(sf_opt)

            if node not in finalDataDict:
                finalDataDict[node] = [bits]
            else:
                finalDataDict[node].append(bits)

    # print(len(finalDataDict))

    return finalDataDict

def parselog_atlora_ber(dataDict):
    finalDataDict = {}

    for node in dataDict:

        if node not in nodeIcnpList:
            continue

        payloadlist = dataDict[node]

        # for payload in payloadlist: (datarate, utcTime, binary payload, status, rssi, SNR)
        for d in range(len(payloadlist)):

            payload = payloadlist[d]
            sf = int(payload[0].replace("SF", ""))
            utcTime = payload[1]
            binary_packet = payload[2]  # received packet by gateway.
            status = payload[3]
            rssi = float(payload[4])
            SNR = payload[5]



            float_snr = pow(10, float(SNR) / 10.0)

            bits = binary_packet + "," + str(sf) + "," + str(float_snr) + "," + str(rssi)

            if node not in finalDataDict:
                finalDataDict[node] = [bits]
            else:
                finalDataDict[node].append(bits)

    # print(len(finalDataDict))

    return finalDataDict

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

def calculateLifetime(sf, packetlength):
    t_cycle = 0.5 * 60
    e_batt = 3600 * 10 * 5 * 1.0

    p_mcu_on = 0.02348
    p_mcu_off = 1.7465 * pow(10, -6)
    p_r_off = 9.9 * pow(10, -5)
    p_r_tx = 0.30

    toa = getTOA(sf, packetlength, 1, 125000)
    transimission_time = toa

    e_cycle = (t_cycle - transimission_time) * (p_mcu_off + p_r_off) + transimission_time * (p_r_tx + p_mcu_on)

    node_life_t = t_cycle * (e_batt / e_cycle)
    node_life = (node_life_t * 1.0) / (3600.0 * 24 * 365)

    return node_life

def getSFBsBn(float_snr, sf, node):

    if node in ["01", "02", "03", "04"]:
        sfList = [sf, sf + 1]
    else:
        if sf > 7:
            sfList = [sf - 1, sf]
        else:
            sfList = [sf]

    lifetimeDict = {}
    for sf_i in sfList:
        ber = getBer(float_snr, sf_i)
        for bs in [2, 4, 8]:
            blrr = pow(1 - ber, (bs + 1) * 8.0)

            bn = math.ceil(payloadSize * 1.0 / (bs * blrr))
            ds = (bs + 1) * bn

            lifetime = calculateLifetime(sf_i, ds)
            keyy = str(sf_i) + "," + str(bs) + "," + str(bn)

            lifetimeDict[keyy] = lifetime

    for sf_i in sfList:
        ber = getBer(float_snr, sf_i)
        bs = 32
        prr = pow(1-ber, bs * 8.0)

        ds = 32 / prr
        bn = 1

        lifetime = calculateLifetime(sf_i, ds)
        keyy = str(sf_i) + "," + str(bs) + "," + str(bn)

        lifetimeDict[keyy] = lifetime


    a = sorted(lifetimeDict.items(), key=lambda x: x[1], reverse=True)

    optimalkey = a[0][0]
    temp = optimalkey.split(",")
    sf_op = int(temp[0])
    bs_op = int(temp[1])
    bn_op = int(temp[2])
    # print(sf_op, bs_op, bn_op)

    return sf_op, bs_op, bn_op

def getSFBsBnIcnp(float_snr, sf, node):

    if node in ["01", "02", "03", "04"]:
        sfList = [sf, sf + 1]
    else:
        if sf > 7:
            sfList = [sf - 1, sf]
        else:
            sfList = [sf]

    lifetimeDict = {}
    for sf_i in sfList:
        ber = getBer(float_snr / 1.3, sf_i)
        for bs in [2, 4, 8]:
            blrr = pow(1 - ber, (bs + 1) * 8.0)

            bn = math.ceil(payloadSize * 1.0 / (bs * blrr))
            ds = (bs + 1) * bn

            lifetime = calculateLifetime(sf_i, ds)
            # bn = int(payloadSize * 1.0 / bs)
            keyy = str(sf_i) + "," + str(bs) + "," + str(bn)

            lifetimeDict[keyy] = lifetime

    a = sorted(lifetimeDict.items(), key=lambda x: x[1], reverse=True)

    optimalkey = a[0][0]
    temp = optimalkey.split(",")
    sf_op = int(temp[0])
    bs_op = int(temp[1])
    bn_op = int((payloadSize * 1.0) / bs_op)
    # print(sf_op, bs_op, bn_op)

    return sf_op, bs_op, bn_op

def findPacket(packetTime, nodeId, dataDict):
    # nodeId is s string

    nodeKey = nodeDict[nodeId]

    current = datetime.datetime.strptime(packetTime, '%Y-%m-%d %H:%M:%S.%f')

    candidatePacketList = dataDict[nodeKey]

    timeDict = {}
    for candi in candidatePacketList:
        sf = candi[0].replace("SF", "")
        utcTime = candi[1]
        binary_packet = candi[2]  # received packet by gateway.
        status = candi[3]
        rssi = candi[4]
        SNR = candi[5]

        candiTime = datetime.datetime.strptime(utcTime, '%Y-%m-%d %H:%M:%S.%f')

        diff = abs((candiTime - current).total_seconds())

        timeDict[binary_packet] = diff
        if diff < 10:
            break

    a = sorted(timeDict.items(), key=lambda x: x[1], reverse=False)


    return a[0][0]

def getTOA(sf, pl, cr, bandWidth):
    # unit: s

    t_sym = (math.pow(2, sf) * 1.0) / (bandWidth * 1.0)
    t_preamble = (8 + 4.25) * t_sym
    de = 0
    h = 0
    n_payload = 8 + max(math.ceil((8 * pl - 4 * sf + 28 + 16 - 20 * h) * 1.0 / (4.0 * (sf - 2 * de))) * (cr + 4), 0)
    t_payload = n_payload * t_sym
    t_packet = t_preamble + t_payload

    return round(t_packet, 3)

def mean_ber(berlistF):
    berListt = []

    for i in range(0, len(berlistF), slot):
        temp = berlistF[i: i+slot]
        mean_temp = float(np.mean(temp))
        # if mean_temp < 0.1:
        berListt.append(mean_temp)

    return berListt

def snrTofloat(snr):

    return pow(10, (snr * 1.0) / 10.0)

def rssiToRx(rssi):

    return pow(10, (rssi * 1.0) / 10.0) / 1000.0  # in Watts
