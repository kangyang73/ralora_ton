import linecache
import numpy as np
import os
import datetime
import re

def isContainAphpa(string):
    my_re = re.compile(r'[A-Za-z]')

    return bool(re.match(my_re, string))

def is_number(string):
    try:
        float(string)
        return True
    except Exception as e:
        #print(e)
        return False

def strToHex(string):
    hex_int = int(string, 16)

    return hex_int

def asciiToBin(string):

    # outStr = "XXXXXXXXXX"
    outList = []
    for i in range(0, len(string), 2):
        asciiCode = string[i: i+2]
        binNum = chr(strToHex(asciiCode))
        #print(asciiCode, binNum)
        if not is_number(binNum):
            binNum = "X"
        outList.append(binNum)

    outStr = "".join(["" + s for s in outList])
    #print(outStr)
    return outStr

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
                            payload = asciiToBin(string)
                            if (len(payload) == packetsize):
                                # try:
                                #     nodeID = payload[: 2]
                                # except Exception as e:
                                #
                                nodeIDTe = payload[: 2]
                                # if nodeID == "01":

                                nodeID = nodeIDDict[datarate]

                                if nodeID not in data:
                                    data[nodeID] = [(utcTime, payload)]
                                else:
                                    data[nodeID].append((utcTime, payload))

                    except IndexError as e:
                        print(line)
                        print(e)
                        # nodeID = "00"
                        #continue



                line = f.readline()

    sorted_data = {}
    for node in data:
        node_packets = data[node]
        sorted_packets = sorted(node_packets, key=lambda x: (x[0], x[1]))

        if node not in sorted_data:
            sorted_data[node] = sorted_packets
    #print(sorted_data)
    for key in sorted_data:
        print(key, len(sorted_data[key]))

    return sorted_data

def calculateER(dataDict, timeslot, packetsize, blocksize, node_to_SF, tempdir):

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

        originalData = payloadlist[0][1]
        try:

            originalData = int(originalData)
        except ValueError as e:
            print(e)
            st = "".join("0" + "" for x in range(packetsize - 2))
            # strr = "".join(s + "," for s in data_temp[i])[: -1]
            originalData = node + st

        all_packets_counter = 0  # packets sent by sensor in a time slot.
        # per_counter = 0

        prr_error_number = 0
        prr_loss_number = 0
        prr_reception_number = 0

        brr_error_number = 0
        brr_loss_number = 0
        brr_reception_number = 0

        blrr_error_number = 0
        blrr_loss_number = 0
        blrr_reception_number = 0

        #counter = 0
        # for payload in payloadlist:
        for d in range(len(payloadlist)):
            payload = payloadlist[d]
            utcTime = payload[0]
            #originalData = str(originalData)
            packet = payload[1]  # received packet by gateway.

            if not isinstance(originalData, str):
                # stt = '"0' + str(packetsize) + 'd'
                originalData = "%090d" % int(originalData)  # string 10 bytes
                # originalData = stt % int(originalData)  # string 10 bytes

            x = packet == originalData
            print(node, x, utcTime, packet, originalData)
            if datetime.datetime.strptime(utcTime, '%Y-%m-%d %H:%M:%S.%f') <= maxTime and (d != len(payloadlist) - 1):

                if packet == originalData:
                    prr_reception_number = prr_reception_number + 1
                else:
                    prr_error_number = prr_error_number + 1

                for x, y in zip(originalData, packet):
                    # print(x, y, x==y)
                    if x == y:
                        brr_reception_number = brr_reception_number + 1
                    else:
                        brr_error_number = brr_error_number + 1

                originalDataList = []
                packetList = []
                # originalData = originalData
                for i in range(0, packetsize, blocksize):
                    originalDataList.append(originalData[i: i + blocksize])
                    packetList.append(packet[i: i + blocksize])

                for x, y in zip(originalDataList, packetList):
                    #print(x, y, x == y)
                    if x == y:
                        blrr_reception_number = blrr_reception_number + 1
                    else:
                        blrr_error_number = blrr_error_number + 1
            else:
                currentTime = utcTime
                current = datetime.datetime.strptime(currentTime, '%Y-%m-%d %H:%M:%S.%f')
                maxTime = current + datetime.timedelta(minutes=timeslot)

                prrError = (prr_error_number * 1.0) / all_packets_counter * 1.0
                prrErrorList.append(prrError)
                prrLoss = (prr_loss_number * 1.0) / all_packets_counter * 1.0
                prrLossList.append(prrLoss)
                prrReception = (prr_reception_number * 1.0) / all_packets_counter * 1.0
                prrReceptionList.append(prrReception)
                # print("prr", all_packets_counter, prr_error_number + prr_loss_number + prr_reception_number, prr_error_number, prr_loss_number, prr_reception_number)


                brrError = (brr_error_number * 1.0) / (all_packets_counter * packetsize)
                brrErrorList.append(brrError)
                brrLoss = (brr_loss_number * 1.0) / (all_packets_counter * packetsize)
                brrLossList.append(brrLoss)
                brrReception = (brr_reception_number * 1.0) / (all_packets_counter * packetsize)
                brrReceptionList.append(brrReception)
                # print("brr", all_packets_counter * packetsize, brr_error_number + brr_loss_number + brr_reception_number, brr_error_number, brr_loss_number, brr_reception_number)


                blrrError = (blrr_error_number * 1.0) / (all_packets_counter * int((packetsize / blocksize)))
                blrrErrorList.append(blrrError)
                blrrLoss = (blrr_loss_number * 1.0) / (all_packets_counter * int((packetsize / blocksize)))
                blrrLossList.append(blrrLoss)
                blrrReception = (blrr_reception_number * 1.0) / (all_packets_counter * int((packetsize / blocksize)))
                blrrReceptionList.append(blrrReception)
                # print("blrr", (all_packets_counter * int((packetsize / blocksize))), blrr_error_number +
                #       blrr_loss_number + blrr_reception_number)
                print(prrError + prrLoss + prrReception, brrError + brrLoss + brrReception,
                      blrrError + blrrLoss + blrrReception)


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

                if packet == originalData:
                    prr_reception_number = prr_reception_number + 1
                else:
                    prr_error_number = prr_error_number + 1

                for x, y in zip(originalData, packet):
                    # print(x, y, x==y)
                    if x == y:
                        brr_reception_number = brr_reception_number + 1
                    else:
                        brr_error_number = brr_error_number + 1

                originalDataList = []
                packetList = []
                # originalData = originalData
                for i in range(0, packetsize, blocksize):
                    originalDataList.append(originalData[i: i + blocksize])
                    packetList.append(packet[i: i + blocksize])

                for x, y in zip(originalDataList, packetList):
                    # print(x, y, x == y)
                    if x == y:
                        blrr_reception_number = blrr_reception_number + 1
                    else:
                        blrr_error_number = blrr_error_number + 1

            # counter = counter + 1

            # if d < len(payloadlist) - 1:
            if d <= len(payloadlist) - 2:
                nextData = payloadlist[d + 1][1]
                nextTime = payloadlist[d + 1][0]
                try:
                    difference = int(nextData) - int(originalData)
                    # if difference > 100:
                    #     difference = 1
                    # if difference <= 0:
                    #     # difference = 1
                    #     continue
                except Exception as e:
                    #print(e)
                    difference = 1

                # if difference == 1:
                #     originalData = int(originalData) + 1
                #     all_packets_counter = all_packets_counter + 1
                # else:
                originalData = int(originalData) + difference

                currentDi = datetime.datetime.strptime(utcTime, '%Y-%m-%d %H:%M:%S.%f')
                timeDelta = currentDi + datetime.timedelta(minutes=20)

                if datetime.datetime.strptime(nextTime, '%Y-%m-%d %H:%M:%S.%f') >= timeDelta:
                    prr_loss_number = prr_loss_number + 1
                    brr_loss_number = brr_loss_number + (1 * packetsize)
                    blrr_loss_number = blrr_loss_number + (1 * int((packetsize / blocksize)))
                    all_packets_counter = all_packets_counter + 1
                else:
                    prr_loss_number = prr_loss_number + (difference - 1)
                    brr_loss_number = brr_loss_number + ((difference - 1) * packetsize)
                    blrr_loss_number = blrr_loss_number + ((difference - 1) * int((packetsize / blocksize)))
                    all_packets_counter = all_packets_counter + difference
            # else:
            #     originalData = payloadlist[d][1]  # sent packet by sensor.
            #     all_packets_counter = all_packets_counter + 1


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
        for i in prrReceptionList:
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
            data.append(temp)

        # data_temp = np.array(data).transpose()
        data_temp = []
        lengthList = []
        for i in range(len(data)):
            lengthList.append(len(data[i]))
        sorted_length = sorted(lengthList, key=lambda x: x, reverse=False)  # down to up

        for i in range(sorted_length[0]):
            temp = []
            for j in range(len(data)):
                temp.append(data[j][i])
            data_temp.append(temp)

        for i in range(len(data_temp)):
            strr = "".join(s + "," for s in data_temp[i])[: -1]
            out.write(strr + "\n")
        out.close()

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        print("There is the folder")


if __name__ == '__main__':
    # line 83: nodeID = nodeIDDict[datarate]
    # line 198: originalData = "%090d" % int(originalData)  # string 10 bytes
    # line 329: timeDelta = currentDi + datetime.timedelta(minutes=20)
    # dateDay = "09062020"
    # filedir = "./packets/" + dateDay + "/"
    # timeslot = 10  # unit: minutes
    # packetsize = 90
    # blocksize = 5
    #
    # freq = "904300000"
    # codingRate = "45"
    # sfList = ["SF7", "SF8", "SF9", "SF10"]
    # nodeIDDict = {"SF7": "01", "SF8": "02", "SF9": "03", "SF10": "04", "SF11": "05", "SF12": "06"}
    # node_to_SF = {"01": "L1_SF7", "02": "L1_SF8", "03": "L1_SF9", "04": "L1_SF10", "05": "L1_SF11", "06": "L1_SF12"}
    #
    # dataDict = file_to_dict(filedir, packetsize, nodeIDDict, freq, codingRate, sfList)
    #
    # tempdir = "./tempOut/" + dateDay + "/"
    # mkdir(tempdir)
    # calculateER(dataDict, timeslot, packetsize, blocksize, node_to_SF, tempdir)
    #
    # outdir = "./figureData/" + dateDay + "/"
    # mkdir(outdir)
    # combine(tempdir, outdir)

    temp = "00111001001110010011100100111001001110010011100100111001001110010011100000111000001110000011100000111000001110000011100000111000001101110011011100110111001101110011011100110111001101110011011100110110001101100011011000110110001101100011011000110110001101100011010100110101001101010011010100110101001101010011010100110101001101000011010000110100001101000011010000110100001101000011010000110011001100110011001100110011001100110011001100110011001100110011001000110010001100100011001000110010001100100011001000110010"

    wrongBits = 0
    for i in temp:
        if i == "9":
            wrongBits = wrongBits + 1

    ber = wrongBits * 1.0 / 72*8

    print(ber)







