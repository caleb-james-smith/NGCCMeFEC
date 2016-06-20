# It is time to check your sum!
# CRC = Cyclic Redundancy Check

import collections

# Convert string of ints to list of ints.
def toIntList(message, base=10):
    mList = message.split()
    for byte in xrange(len(mList)):
        mList[byte] = int(mList[byte], base)
    return mList

# Check Sum function from Temp/Humi Documentation.
def checkCRC(message, numBytes, base=10):
    POLYNOMIAL = 0x131 # x^8 + x^5 + x^4 + 1 -> 9'b100110001 = 0x131
    crc = 0
    mList = toIntList(message, base)
    errorCode = mList[0]
    dataList = mList[1:-1]
    checksum = mList[-1]
    if errorCode != 0:
        return 'I2C_BUS_ERROR'
    # calculates 8-bit checksum with give polynomial
    for byteCtr in xrange(numBytes):
        crc ^= dataList[byteCtr]
        for bit in xrange(8,0,-1):
            if crc & 0x80:
                crc = (crc << 1) ^ POLYNOMIAL
            else:
                crc = (crc << 1)
    if crc != checksum:
        return 'CHECKSUM_ERROR'
    return 'CHECKSUM_OK'

# Two Binary Data Bytes
binaryData = '01110000 00111100'
# One Binary Checksum Byte
binaryChecksum = '10000011'

# message = 'errorCode byte1 byte2 checksum'

# Happy Data has a valid checksum! :)
binDataHappy = '0 01110000 00111100 10000011'
intDataHappy = '0 112 60 131'

# Sad Data has an invalid checksum. :(
binDataSad = '0 01110000 00111100 10000010'
intDataSad = '0 112 60 130'

# An I2S Bus Error is seen by a nonzero first bit (1).
binI2Cerror = '1 01110000 00111100 10000011'
intI2Cerror = '1 112 60 131'

# makes some lists to iterate through 3 tests
testList = ['Happy Data', 'Sad Data', 'I2C Error']
binDataList = [binDataHappy, binDataSad, binI2Cerror]
intDataList = [intDataHappy, intDataSad, intI2Cerror]

def testCRC(numTests):
    for test in xrange(numTests):
        print '\n',testList[test]
        print binDataList[test], ' : ', checkCRC(binDataList[test], 2, 2)
        print intDataList[test], ' : ', checkCRC(intDataList[test], 2, 10),'\n'

# numTests = 3... happy, sad, and I2C Error
testCRC(3)
