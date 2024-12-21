import numpy as np
import os
import datetime
import re
import random
import shutil
from itertools import islice

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
    ## 3030 -> 00
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
    ## 3030 -> 0011 0000 0011 0000
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
    ## 00 -> 00110000 00110000
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

def file_to_dict(filedir, packetsize, nodeIDDict, freq, codingRate, sfList):
# function: transfer all packets payload into a data dict.

    filelists = os.listdir(filedir)
    #print(filelists)
    data = {}

    for file in filelists:
        if not file.endswith(".csv"):
            continue
        filename = filedir + file
        with open(filename, 'r') as f:

            line = f.readline()
            while line:
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
                        # print(len(string))

                        if (frequency == freq) and (codeRate == codingRate) and (datarate in sfList):
                            # continue
                            # payload = asciiToBin(string)
                            payload = string  # 3030
                            # print(payload)
                            if (len(payload) == packetsize * 2):

                                nodeID = nodeIDDict[datarate]
                                # print(datarate, nodeID)
                                # nodeID = "00"
                                # if len(payload) == 180:
                                #     nodeID = "03"
                                # if len(payload) == 90:
                                #     nodeID = "04"
                                # if len(payload) == 80:
                                #     nodeID = "05"
                                # if nodeID != "00":

                                if nodeID not in data:
                                    data[nodeID] = [(utcTime, payload, status, SNR)]
                                else:
                                    data[nodeID].append((utcTime, payload, status, SNR))
                                # if "04" in data:
                                #     print(data["04"])
                    except IndexError as e:
                        # print(line)
                        print("file_to_dict Function IndexError: ", e)
                        # nodeID = "00"

                line = f.readline()

    sorted_data = {}
    for node in data:
        node_packets = data[node]
        sorted_packets = sorted(node_packets, key=lambda x: (x[0], x[1]))

        # if node not in sorted_data:
        sorted_data[node] = sorted_packets

    print(len(sorted_data))

    for key in sorted_data:
        print("Summing data: ", key, len(sorted_data[key]))

    return sorted_data

def calculateER(dataDict, timeslot, packetsize, blocksize, node_to_SF, tempdir, prob):

    for node in dataDict:
        #context = node_to_SF[node]
        # if node != "00":  # noise data, it is not sent by our sensor.
        #  error: packets containing wrong bytes / packtes sent by sensor
        #  loss: missing packets / packtes sent by sensor
        #  reception: packets received by gateway correctly / packtes sent by sensor

        prrErrorFile = tempdir + "prrError_" + node_to_SF[node] + ".csv"
        prrLossFile = tempdir + "prrLoss_" + node_to_SF[node] + ".csv"
        prrReceptionFile = tempdir + "prrReception_" + node_to_SF[node] + ".csv"

        brrErrorFile = tempdir + "brrError_" + node_to_SF[node] + ".csv"
        brrLossFile = tempdir + "brrLoss_" + node_to_SF[node] + ".csv"
        brrReceptionFile = tempdir + "brrReception_" + node_to_SF[node] + ".csv"

        blrrErrorFile = tempdir + "blrrError_" + node_to_SF[node] + ".csv"
        blrrLossFile = tempdir + "blrrLoss_" + node_to_SF[node] + ".csv"
        blrrReceptionFile = tempdir + "blrrReception_" + node_to_SF[node] + ".csv"

        prr_error_f = open(prrErrorFile, "w")
        prr_loss_f = open(prrLossFile, "w")
        prr_reception_f = open(prrReceptionFile, "w")

        brr_error_f = open(brrErrorFile, "w")
        brr_loss_f = open(brrLossFile, "w")
        brr_reception_f = open(brrReceptionFile, "w")

        blrr_error_f = open(blrrErrorFile, "w")
        blrr_loss_f = open(blrrLossFile, "w")
        blrr_reception_f = open(blrrReceptionFile, "w")

        prrErrorList = []
        prrLossList = []
        prrReceptionList = []

        brrErrorList = []
        brrLossList = []
        brrReceptionList = []

        blrrErrorList = []
        blrrLossList = []
        blrrReceptionList = []

        payloadlist = dataDict[node]
        currentTime = payloadlist[0][0]
        current = datetime.datetime.strptime(currentTime, '%Y-%m-%d %H:%M:%S.%f')
        maxTime = current + datetime.timedelta(minutes=timeslot)

        # asciiToBin  # 3030 -> 00
        # asciiToBin2  # 3030 -> 00110000 00110000
        # stringToBin  # 00 -> 00110000 00110000

        if payloadlist[0][2] == "CRC_OK":
            originalData = asciiToBin(payloadlist[0][1])  # payload = asciiToBin(string)
        else:
            st = "".join("0" + "" for x in range(packetsize - 2))
            originalData = node + st
        # originalData = payloadlist[0][1]
        # try:
        #     t = int(originalData)
        # except Exception as e:
        #     st = "".join("0" + "" for x in range(packetsize - 2))
        #     originalData = node + st


        all_packets_counter = 0  # packets sent by sensor in one time slot.

        prr_error_number = 0
        prr_loss_number = 0
        prr_reception_number = 0

        brr_error_number = 0
        brr_loss_number = 0
        brr_reception_number = 0

        blrr_error_number = 0
        blrr_loss_number = 0
        blrr_reception_number = 0

        # for payload in payloadlist:
        for d in range(len(payloadlist)):
            payload = payloadlist[d]
            utcTime = payload[0]
            #originalData = str(originalData)
            packet = payload[1]  # received packet by gateway.
            status = payload[2]

            if not isinstance(originalData, str):
                # stt = '"0' + str(packetsize) + 'd'
                originalData = "%090d" % int(originalData)  # string 10 bytes
                # originalData = stt % int(originalData)  # string 10 bytes

            # x = (packet == originalData)
            # print(node, x, utcTime, packet, originalData)
            if datetime.datetime.strptime(utcTime, '%Y-%m-%d %H:%M:%S.%f') <= maxTime and (d != len(payloadlist) - 1):
            # if datetime.datetime.strptime(utcTime, '%Y-%m-%d %H:%M:%S.%f') <= maxTime:
                if asciiToBin(packet) == originalData:
                    prr_reception_number = prr_reception_number + 1
                else:
                    prr_error_number = prr_error_number + 1

                for x, y in zip(asciiToBin2(packet), stringToBin(originalData)):
                    # print(x, y, x==y)
                    if x == y:
                        brr_reception_number = brr_reception_number + 1
                    else:
                        brr_error_number = brr_error_number + 1

                originalDataList = []
                packetList = []
                # originalData = originalData
                for i in range(0, packetsize * 8, blocksize):
                    # originalDataList.append(originalData[i: i + blocksize])
                    # packetList.append(asciiToBin(packet)[i: i + blocksize])
                    originalDataList.append(stringToBin(originalData)[i: i + blocksize])
                    packetList.append(asciiToBin2(packet)[i: i + blocksize])

                for x, y in zip(originalDataList, packetList):
                    if x == y:
                        blrr_reception_number = blrr_reception_number + 1
                    else:
                        blrr_error_number = blrr_error_number + 1
            else:
                currentTime = utcTime
                current = datetime.datetime.strptime(currentTime, '%Y-%m-%d %H:%M:%S.%f')
                maxTime = current + datetime.timedelta(minutes=timeslot)

                if all_packets_counter != 0:

                    prrError = (prr_error_number * 1.0) / all_packets_counter * 1.0
                    prrErrorList.append(prrError)
                    prrLoss = (prr_loss_number * 1.0) / all_packets_counter * 1.0
                    prrLossList.append(prrLoss)
                    prrReception = (prr_reception_number * 1.0) / all_packets_counter * 1.0
                    prrReceptionList.append(prrReception)
                    # print("prr", all_packets_counter, prr_error_number + prr_loss_number + prr_reception_number, prr_error_number, prr_loss_number, prr_reception_number)
                    # print("prr", node, prrError, prrLoss, prrReception)


                    brrError = (brr_error_number * 1.0) / (all_packets_counter * packetsize * 8.0)
                    brrErrorList.append(brrError)
                    brrLoss = (brr_loss_number * 1.0) / (all_packets_counter * packetsize * 8.0)
                    brrLossList.append(brrLoss)
                    brrReception = (brr_reception_number * 1.0) / (all_packets_counter * packetsize * 8.0)
                    brrReceptionList.append(brrReception)
                    # print("brr", all_packets_counter * packetsize, brr_error_number + brr_loss_number + brr_reception_number, brr_error_number, brr_loss_number, brr_reception_number)



                    blrrError = (blrr_error_number * 1.0) / (all_packets_counter * int((packetsize * 8.0 / blocksize)))
                    blrrErrorList.append(blrrError)
                    blrrLoss = (blrr_loss_number * 1.0) / (all_packets_counter * int((packetsize * 8.0 / blocksize)))
                    blrrLossList.append(blrrLoss)
                    blrrReception = (blrr_reception_number * 1.0) / (all_packets_counter * int((packetsize * 8.0 / blocksize)))
                    blrrReceptionList.append(blrrReception)
                    # print("blrr", (all_packets_counter * int((packetsize / blocksize))), blrr_error_number +
                    #       blrr_loss_number + blrr_reception_number)
                    # print(prrError + prrLoss + prrReception, brrError + brrLoss + brrReception,
                    #       blrrError + blrrLoss + blrrReception)
                    print(blrrError + blrrLoss + blrrReception, blrrReception, blrrLoss, blrrError)
                else:
                    prrErrorList.append(100)
                    prrLossList.append(100)
                    prrReceptionList.append(100)

                    brrErrorList.append(100)
                    brrLossList.append(100)
                    brrReceptionList.append(100)

                    blrrErrorList.append(100)
                    blrrLossList.append(100)
                    blrrReceptionList.append(100)


                prr_error_number = 0
                prr_loss_number = 0
                prr_reception_number = 0

                brr_error_number = 0
                brr_loss_number = 0
                brr_reception_number = 0

                blrr_error_number = 0
                blrr_loss_number = 0
                blrr_reception_number = 0

                all_packets_counter = 0

                if asciiToBin(packet) == originalData:
                    prr_reception_number = prr_reception_number + 1
                else:
                    prr_error_number = prr_error_number + 1

                for x, y in zip(asciiToBin2(packet), stringToBin(originalData)):
                    # print(x, y, x==y)
                    if x == y:
                        brr_reception_number = brr_reception_number + 1
                    else:
                        brr_error_number = brr_error_number + 1

                originalDataList = []
                packetList = []
                # originalData = originalData
                for i in range(0, packetsize * 8, blocksize):
                    originalDataList.append(stringToBin(originalData)[i: i + blocksize])
                    packetList.append(asciiToBin2(packet)[i: i + blocksize])

                for x, y in zip(originalDataList, packetList):
                    # print(x, y, x == y)
                    if x == y:
                        blrr_reception_number = blrr_reception_number + 1
                    else:
                        blrr_error_number = blrr_error_number + 1

            # counter = counter + 1

            # if d < len(payloadlist) - 1:
            if d <= len(payloadlist) - 2:
                nextData = asciiToBin(payloadlist[d + 1][1])
                nextTime = payloadlist[d + 1][0]
                nextStatus = payloadlist[d + 1][2]

                try:
                    difference = int(nextData) - int(originalData)
                except Exception as e:
                    difference = 1

                originalData = int(originalData) + difference

                currentDi = datetime.datetime.strptime(utcTime, '%Y-%m-%d %H:%M:%S.%f')
                timeDelta = currentDi + datetime.timedelta(minutes=2)
                if datetime.datetime.strptime(nextTime, '%Y-%m-%d %H:%M:%S.%f') >= timeDelta:
                    difference = 1

                if difference >= 2:
                    difference = 1
                if difference < 1:
                    difference = 1
                if difference == 2:
                    random.seed(d)
                    indexR = d % 9
                    np.random.seed(d)
                    floatNum = np.random.uniform(0, 1, (10,))
                    np.random.seed(d + 1994)
                    np.random.shuffle(floatNum)
                    # floatNum = random.random()
                    if floatNum[indexR] < prob:
                        difference = 1

                prr_loss_number = prr_loss_number + (difference - 1)
                brr_loss_number = brr_loss_number + ((difference - 1) * packetsize * 8)
                blrr_loss_number = blrr_loss_number + ((difference - 1) * int((packetsize * 8 / blocksize)))
                all_packets_counter = all_packets_counter + difference

        for i in prrErrorList:
            prr_error_f.write(str(i) + "\n")
        for i in prrLossList:
            prr_loss_f.write(str(i) + "\n")
        for i in prrReceptionList:
            prr_reception_f.write(str(i) + "\n")

        for i in brrErrorList:
            brr_error_f.write(str(i) + "\n")
        for i in brrLossList:
            brr_loss_f.write(str(i) + "\n")
        for i in brrReceptionList:
            brr_reception_f.write(str(i) + "\n")

        for i in blrrErrorList:
            blrr_error_f.write(str(i) + "\n")
        for i in blrrLossList:
            blrr_loss_f.write(str(i) + "\n")
        for i in blrrReceptionList:
            blrr_reception_f.write(str(i) + "\n")

        prr_error_f.close()
        prr_loss_f.close()
        prr_reception_f.close()

        brr_error_f.close()
        brr_loss_f.close()
        brr_reception_f.close()

        blrr_error_f.close()
        blrr_loss_f.close()
        blrr_reception_f.close()

def combine(filedir, outdir):

    filelists = os.listdir(filedir)

    tempFiles = {}
    for file in filelists:
        file = str(file)

        if (file.find("XXXX") < 0):

            info = file.split("_")
            mertic = info[0]  # per ber bler
            location = info[1]  # location
            if mertic not in tempFiles:
                tempFiles[mertic] = [(location, file)]
            else:
                tempFiles[mertic].append((location, file))

    merLocFile = {}
    for k in tempFiles:
        files = tempFiles[k]

        tFiles = {}
        for file in files:
            location = file[0]
            filename = file[1]
            if location not in tFiles:
                tFiles[location] = [filename]
            else:
                tFiles[location].append(filename)

        for loc in tFiles:
            files = tFiles[loc]
            newKey = files[0].split("_")[0] + "_" + files[0].split("_")[1]

            merLocFile[newKey] = files

    for key in merLocFile:
        values = merLocFile[key]
        # print(values)

        sorted_values = sorted(values, key=lambda x: int(x.replace(".csv", "").split("_")[2][2:]), reverse=False)  # down to up

        outFile = outdir + key + ".csv"
        out = open(outFile, "w")

        data = []
        # print(key, values)
        print(key, sorted_values)
        # print("----------------------")
        for filex in sorted_values:
            filename = filedir + filex
            temp = []
            with open(filename, 'r') as f:
                line = f.readline()
                while line:
                    line = line.replace(")", "").replace("'", "").replace('"', '').replace('\n', '').replace(' ', '')
                    temp.append(line)
                    line = f.readline()
            data.append(temp[: -1])

        # data_temp = np.array(data).transpose()
        data_temp = []
        lengthList = []
        for i in range(len(data)):
            lengthList.append(len(data[i]))
        sorted_length = sorted(lengthList, key=lambda x: x, reverse=True)  # down to up

        for i in range(sorted_length[0]):
            temp = []
            for j in range(len(data)):
                try:
                    temp.append(data[j][i])
                except IndexError as e:
                    # print(e)
                    temp.append(str(2))
            data_temp.append(temp)

        for i in range(len(data_temp)):
            strr = "".join(s + "," if float(s) <= 1 else " ," for s in data_temp[i])[: -1]
            out.write(strr + "\n")
        out.close()

def combine2(outdir, outdir2):

    filelists = os.listdir(outdir)

    tempFiles = {}
    for file in filelists:
        file = str(file)

        if (file.find("XXXX") < 0):

            info = file.split("_")
            mertic = info[0]  # per ber bler
            location = info[1]  # location
            if mertic not in tempFiles:
                tempFiles[mertic] = [(location, file)]
            else:
                tempFiles[mertic].append((location, file))

    merLocFile = {}
    for k in tempFiles:
        files = tempFiles[k]

        tFiles = {}
        for file in files:
            location = file[0]
            filename = file[1]
            if location not in tFiles:
                tFiles[location] = [filename]
            else:
                tFiles[location].append(filename)

        for loc in tFiles:
            files = tFiles[loc]
            newKey = files[0].split("_")[0] + "_" + files[0].split("_")[1]

            merLocFile[newKey] = files

    for key in merLocFile:
        values = merLocFile[key]
        # print(values)

        sorted_values = sorted(values, key=lambda x: int(x.replace(".csv", "").split("_")[2][2:]), reverse=False)  # down to up

        outFile = outdir2 + key + ".csv"
        out = open(outFile, "w")

        data = []
        # print(key, values)
        print(key, sorted_values)
        # print("----------------------")
        for filex in sorted_values:
            filename = filedir + filex
            temp = []
            with open(filename, 'r') as f:
                line = f.readline()
                while line:
                    line = line.replace(")", "").replace("'", "").replace('"', '').replace('\n', '').replace(' ', '')
                    temp.append(line)
                    line = f.readline()
            data.append(temp[: -1])

        # data_temp = np.array(data).transpose()
        data_temp = []
        lengthList = []
        for i in range(len(data)):
            lengthList.append(len(data[i]))
        sorted_length = sorted(lengthList, key=lambda x: x, reverse=True)  # down to up

        for i in range(sorted_length[0]):
            temp = []
            for j in range(len(data)):
                try:
                    temp.append(data[j][i])
                except IndexError as e:
                    # print(e)
                    temp.append(str(2))
            data_temp.append(temp)

        for i in range(len(data_temp)):
            strr = "".join(s + "," if float(s) <= 1 else " ," for s in data_temp[i])[: -1]
            out.write(strr + "\n")
        out.close()

def combine3(outdir, outdir2):

    filelists = os.listdir(outdir)

    # tempFiles = []
    # for file in filelists:
    #     file = str(file)
    #     if (file.find("Reception") > 0):
    #         tempFiles.append(file)

    # prr
    prrfile = "prrReception_L1.csv"
    prrFile = outdir + prrfile
    input_file = open(prrFile)

    t1 = []
    t2 = []
    t3 = []
    for line in islice(input_file, 0, None):

        line = line.replace(")", "").replace("'", "").replace('"', '').replace('\n', '').split(",")
        print(line)
        # if line[0] == " ":
        #     line[0] = "0"
        try:
            l1 = float(line[0])
        except Exception as e:
            l1 = 0
        l2 = float(line[1])
        l3 = float(line[2])

        t1.append(l1)
        t2.append(l2)
        t3.append(l3)

    min_len = min(len(t1), len(t2), len(t3))
    outfile = outdir2 + prrfile
    out = open(outfile, "w")
    out.write("b1 = [")
    outStr = "".join([" " + str(s) for s in t1[: min_len]])[: -1]
    out.write(outStr)
    out.write("];")
    out.write("\n")

    out.write("b2 = [")
    outStr = "".join([" " + str(s) for s in t2[: min_len]])[: -1]
    out.write(outStr)
    out.write("];")
    out.write("\n")

    out.write("b3 = [")
    outStr = "".join([" " + str(s) for s in t3[: min_len]])[: -1]
    out.write(outStr)
    out.write("];")
    out.write("\n")
    out.close()

    # brr
    prrfile = "brrReception_L1.csv"

    prrFile = outdir + prrfile
    input_file = open(prrFile)

    t1 = []
    t2 = []
    t3 = []
    for line in islice(input_file, 0, None):
        line = line.replace(")", "").replace("'", "").replace('"', '').replace('\n', '').split(",")
        try:
            l1 = float(line[0])
        except Exception as e:
            l1 = 0
        l2 = float(line[1])
        l3 = float(line[2])

        t1.append(l1)
        t2.append(l2)
        t3.append(l3)

    min_len = min(len(t1), len(t2), len(t3))
    outfile = outdir2 + prrfile
    out = open(outfile, "w")
    out.write("b1 = [")
    outStr = "".join([" " + str(s) for s in t1[: min_len]])[: -1]
    out.write(outStr)
    out.write("];")
    out.write("\n")

    out.write("b2 = [")
    outStr = "".join([" " + str(s) for s in t2[: min_len]])[: -1]
    out.write(outStr)
    out.write("];")
    out.write("\n")

    out.write("b3 = [")
    outStr = "".join([" " + str(s) for s in t3[: min_len]])[: -1]
    out.write(outStr)
    out.write("];")
    out.write("\n")
    out.close()


    # blrr
    prrfile = "blrrReception_L1.csv"
    prrFile = outdir + prrfile
    input_file = open(prrFile)

    t1 = []
    t2 = []
    t3 = []
    for line in islice(input_file, 0, None):
        line = line.replace(")", "").replace("'", "").replace('"', '').replace('\n', '').split(",")
        try:
            l1 = float(line[0])
        except Exception as e:
            l1 = 0
        l2 = float(line[1])
        l3 = float(line[2])

        t1.append(l1)
        t2.append(l2)
        t3.append(l3)

    min_len = min(len(t1), len(t2), len(t3))
    outfile = outdir2 + prrfile
    out = open(outfile, "w")
    out.write("b1 = [")
    outStr = "".join([" " + str(s) for s in t1[: min_len]])[: -1]
    out.write(outStr)
    out.write("];")
    out.write("\n")

    out.write("b2 = [")
    outStr = "".join([" " + str(s) for s in t2[: min_len]])[: -1]
    out.write(outStr)
    out.write("];")
    out.write("\n")

    out.write("b3 = [")
    outStr = "".join([" " + str(s) for s in t3[: min_len]])[: -1]
    out.write(outStr)
    out.write("];")
    out.write("\n")
    out.close()


if __name__ == '__main__':
    # last version of calculating link quality.
    ############################################
    ############################################
    ############################################

    # These three lines may need to be changed.
    # nodeID = nodeIDDict[datarate]
    # originalData = "%090d" % int(originalData)  # string 10 bytes
    # timeDelta = currentDi + datetime.timedelta(minutes=10)
    dateDay = "09102020"  # experiment day that identify different experiment settings.
    timeslot = 5  # time slot, its unit is minutes.
    packetsize = 90  # payload size.
    blocksize = 9  # block size.
    freq = "904300000"
    codingRate = "45"
    # sfList = ["SF10", "SF9", "SF8", "SF7", "SF11", "SF12"]
    sfList = ["SF8", "SF9", "SF10"]
    # nodeIDDict = {"SF7": "01", "SF8": "02", "SF9": "03", "SF10": "04", "SF11": "05", "SF12": "06"}
    # node_to_SF = {"01": "L1_SF7", "02": "L1_SF8", "03": "L1_SF9", "04": "L1_SF10", "05": "L1_SF11", "06": "L1_SF12"}
    nodeIDDict = {"SF8": "04", "SF9": "03", "SF10": "01"}
    node_to_SF = {"01": "L1_SF10", "03": "L1_SF9", "04": "L1_SF8"}
    prob = 0.75  # The parameter will not be used in this code.

    filedir = "./packets/" + dateDay + "/"
    dataDict = file_to_dict(filedir, packetsize, nodeIDDict, freq, codingRate, sfList)

    tempdir = "./tempOut/" + dateDay + "/"
    deledir(tempdir)
    mkdir(tempdir)
    calculateER(dataDict, timeslot, packetsize, blocksize, node_to_SF, tempdir, prob)

    outdir = "./figureData/" + dateDay + "/"
    deledir(outdir)
    mkdir(outdir)
    combine(tempdir, outdir)

    outdir2 = "./motivation/" + dateDay + "/"
    deledir(outdir2)
    mkdir(outdir2)
    combine3(outdir, outdir2)




