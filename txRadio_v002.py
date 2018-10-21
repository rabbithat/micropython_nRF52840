# This program for an nRF52840 sends a one byte payload in a 
# packet once every second.

from micropython import const
import machine  # so can peek and poke different registers on the nRF5x
import uctypes
import utime

radioBuffer = bytearray(100)  # allocate IO buffer for use by nRF5x radio
radioBuffer_address = uctypes.addressof(radioBuffer)

target_prefixAddress = const(0xAA)
target_baseAddress = const(0xDEADBEEF)

NRF_POWER = const(0x40000000)
DCDCEN = const(0x578)
NRF_POWER___DCDCEN = const(NRF_POWER + DCDCEN)

NRF_CLOCK = const(0x40000000)
TASKS_HFCLKSTART = const(0)
EVENTS_HFCLKSTARTED = const(0x100)
NRF_CLOCK___TASKS_HFCLKSTART = const(NRF_CLOCK + TASKS_HFCLKSTART)
NRF_CLOCK___EVENTS_HFCLKSTARTED = const(NRF_CLOCK + EVENTS_HFCLKSTARTED)

NRF_RADIO = const(0x40001000)
BASE0 = const(0x51C)
PREFIX0 = const(0x524)
FREQUENCY = const(0x508)
PCNF1 = const(0x518)
PCNF0 = const(0x514)
MODE = const(0x510)
MODECNF0 = const(0x650)
CRCCNF = const(0x534)
PACKETPTR = const(0x504)
RXADDRESSES = const(0x530)
TXPOWER = const(0x50C)
TASKS_DISABLE = const(0x010)
STATE = const(0x550)
TASKS_TXEN = const(0)
EVENTS_READY = const(0x100)
TASKS_START = const(0x008)
NRF_RADIO___BASE0 = const(NRF_RADIO + BASE0)
NRF_RADIO___PREFIX0 = const(NRF_RADIO + PREFIX0)
NRF_RADIO___FREQUENCY = const(NRF_RADIO + FREQUENCY)
NRF_RADIO___PCNF1 = const(NRF_RADIO + PCNF1)
NRF_RADIO___PCNF0 = const(NRF_RADIO + PCNF0)
NRF_RADIO___MODE = const(NRF_RADIO + MODE)
NRF_RADIO___MODECNF0 = const(NRF_RADIO + MODECNF0)
NRF_RADIO___CRCCNF = const(NRF_RADIO + CRCCNF)
NRF_RADIO___PACKETPTR = const(NRF_RADIO + PACKETPTR)
NRF_RADIO___RXADDRESSES = const(NRF_RADIO + RXADDRESSES)
NRF_RADIO___TXPOWER = const(NRF_RADIO + TXPOWER)
NRF_RADIO___TASKS_DISABLE = const(NRF_RADIO + TASKS_DISABLE)
NRF_RADIO___STATE = const(NRF_RADIO + STATE)
NRF_RADIO___TASKS_TXEN = const(NRF_RADIO + TASKS_TXEN)
NRF_RADIO___EVENTS_READY = const(NRF_RADIO + EVENTS_READY)
NRF_RADIO___TASKS_START = const(NRF_RADIO + TASKS_START)

def initializeSerialOutput():
    print("Starting...")

def initializeHardware():  # enable the DCDC voltage regulator
    machine.mem32[NRF_POWER___DCDCEN] = 1  # NRF_POWER->DCDCEN=1;   
    
def initializeClocks():    # activate the high frequency crystal oscillator
    # NRF_CLOCK->TASKS_HFCLKSTART=1;  
    machine.mem32[NRF_CLOCK___TASKS_HFCLKSTART] = 1 
    # wait until high frequency clock start is confirmed
    # while (NRF_CLOCK->EVENTS_HFCLKSTARTED==0) {};  
    while (machine.mem32[NRF_CLOCK___EVENTS_HFCLKSTARTED] == 0):
        True
        
def initializeRadio():
    # print target address in hexadecimal
    print("Target address is 0x{:02X}".format(target_prefixAddress)
          + "{:08X}".format(target_baseAddress))
          
    machine.mem32[NRF_RADIO___BASE0] = target_baseAddress
    machine.mem32[NRF_RADIO___PREFIX0] = target_prefixAddress
    
    # value must be between 0 and 100
    machine.mem32[NRF_RADIO___FREQUENCY] = 98  # 2498Mhz.  
    
    # base address is 4 bytes long (possible range is 2 to 4) and 
    # max size of payload is 1,and 1 bytes of static length payload
    machine.mem32[NRF_RADIO___PCNF1] = 0x40101
    # S0,LENGTH, and S1 are all zero bits long.
    machine.mem32[NRF_RADIO___PCNF0] = 0
    
    machine.mem32[NRF_RADIO___MODE] = 1  # set 2Mbps datarate.
    machine.mem32[NRF_RADIO___MODECNF0] = 1  # enable fast ramp-up of radio from DISABLED state.
    
    machine.mem32[NRF_RADIO___CRCCNF] = 3  # CRC will be 3 bytes and is computed including the address field
    machine.mem32[NRF_RADIO___PACKETPTR] = radioBuffer_address  # pointer to the payload in radioBuffer
    
    machine.mem32[NRF_RADIO___RXADDRESSES] = 1  # receive on logical address 0.  Not important for transmitting.
    machine.mem32[NRF_RADIO___TXPOWER] = 4  # set to 4db transmit power, which is the maximum. max for nRF52840 is 8db
    
    machine.mem32[NRF_RADIO___TASKS_DISABLE] = 1  # DISABLE the radio to establish a known state.
    while (machine.mem32[NRF_RADIO___STATE] != 0):  # wait until radio is DISABLED (i.e. STATE=0);
        True
        
    machine.mem32[NRF_RADIO___TASKS_TXEN] = 1  # turn on the radio transmitter and shift into TXIDLE.
    while (machine.mem32[NRF_RADIO___EVENTS_READY] == 0):  # Busy-wait.  After event READY, radio shall be in state TXIDLE.
        True
        
    machine.mem32[const(NRF_RADIO___TASKS_START)] = 1  # Move from TXIDLE mode into TX mode.

def start():
    # Main setup    
    initializeSerialOutput()
    initializeHardware()
    initializeClocks()
    initializeRadio() 

    # Main loop
    while (True):
        if (machine.mem32[NRF_RADIO___STATE] != 11):  # if radio no longer in TX state, then it must have sent a packet
            utime.sleep_ms(1000)  # wait one second before sending next packet
            machine.mem32[radioBuffer_address] = ((machine.mem32[radioBuffer_address] + 1) % 256)  # increment the payload value to send something different
            machine.mem32[NRF_RADIO___TASKS_START] = 1  # Move from TXIDLE mode into TX mode to transmit another packet
