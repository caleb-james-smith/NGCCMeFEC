# Read Unique ID for you and me!

import Hardware
import helpers
from Checksum import Check

class ID:
    def __init__(self, bus, slot):
        self.bus = bus
        self.slot = slot
        self.raw = self.getID()
        self.cooked = self.getSerial()

    def getID(self):
        Hardware.openChannel(self.slot, self.bus)
        # Reset entire board by writing 0x6 to 0x0.
        self.bus.write(0x00,[0x06])
        # Note that the i2c_select has register address 0x11
        # Value : 4 = 0x04 selects 0x50
        # Note that the SSN expects 32 bits (4 bytes) for writing (send 0x4, 0, 0, 0)
        self.bus.write(Hardware.getCardAddress(self.slot),[0x11,0x04,0,0,0])
        # Send 0x0 to 0x50 in order to set pointer for reading ID
        # This removes the permutation problem!
        self.bus.write(0x50,[0x00])
        self.bus.read(0x50,8)
        raw = self.bus.sendBatch()[-1]
        # Checksum
        check = Check(raw,0)
        if check.result != 0:
            print 'checksum error'
        return raw

    def getSerial(self):
        if int(self.raw.split()[1]) != 0x70:
            print 'Not in Family 0x70'
            return 'Family_Code_Error'
        serial = self.raw[2:-1] # cereal
        oats = helpers.reverseBytes(serial) # reversed
        eggs = helpers.toHex(oats,2) # hex
        return eggs
