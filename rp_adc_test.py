# Pico MicroPython: ADC test code
# See https://iosoft.blog/pico-adc-dma for description

import time, array, uctypes, rp_devices as devs
from machine import Pin
import utime
led0 = Pin(24, Pin.OUT)
led0.low()
led = Pin(25, Pin.OUT)
led.low()
counter = 5
# Set ADC input channel
ADC_CHAN = 0
ADC_PIN  = 26 + ADC_CHAN
adc = devs.ADC_DEVICE
pin = devs.GPIO_PINS[ADC_PIN]
pad = devs.PAD_PINS[ADC_PIN]
pin.GPIO_CTRL_REG = devs.GPIO_FUNC_NULL
pad.PAD_REG = 0

adc.CS_REG = adc.FCS_REG = 0
adc.CS.EN = 1
adc.CS.AINSEL = ADC_CHAN
adc.CS.START_ONCE = 1
print(adc.RESULT_REG)

# Multiple ADC samples using DMA
DMA_CHAN = 0
NSAMPLES = 10
RATE = 100000
dma_chan = devs.DMA_CHANS[DMA_CHAN]
dma = devs.DMA_DEVICE

adc.FCS.EN = adc.FCS.DREQ_EN = 1
adc_buff = array.array('H', (0 for _ in range(NSAMPLES)))
adc.DIV_REG = (48000000 // RATE - 1) << 8
adc.FCS.THRESH = adc.FCS.OVER = adc.FCS.UNDER = 1

dma_chan.READ_ADDR_REG = devs.ADC_FIFO_ADDR
dma_chan.WRITE_ADDR_REG = uctypes.addressof(adc_buff)
dma_chan.TRANS_COUNT_REG = NSAMPLES

dma_chan.CTRL_TRIG_REG = 0
dma_chan.CTRL_TRIG.CHAIN_TO = DMA_CHAN
dma_chan.CTRL_TRIG.INCR_WRITE = dma_chan.CTRL_TRIG.IRQ_QUIET = 1
dma_chan.CTRL_TRIG.TREQ_SEL = devs.DREQ_ADC
dma_chan.CTRL_TRIG.DATA_SIZE = 1

while True :
    ADC_CHAN=ADC_CHAN+1
    if ADC_CHAN>3:
        ADC_CHAN=0
    adc.CS.AINSEL = ADC_CHAN
    DMA_CHAN = ADC_CHAN
    
    ADC_PIN  = 26 + ADC_CHAN
    adc = devs.ADC_DEVICE
    pin = devs.GPIO_PINS[ADC_PIN]
    pad = devs.PAD_PINS[ADC_PIN]
    pin.GPIO_CTRL_REG = devs.GPIO_FUNC_NULL
    pad.PAD_REG = 0  

    # Multiple ADC samples using DMA
    dma_chan = devs.DMA_CHANS[DMA_CHAN]
    dma = devs.DMA_DEVICE

    dma_chan = devs.DMA_CHANS[DMA_CHAN]
    dma_chan.CTRL_TRIG.CHAIN_TO = DMA_CHAN
    
    dma_chan.READ_ADDR_REG = devs.ADC_FIFO_ADDR
    dma_chan.WRITE_ADDR_REG = uctypes.addressof(adc_buff)
    dma_chan.TRANS_COUNT_REG = NSAMPLES
    
    dma_chan.CTRL_TRIG_REG = 0
    dma_chan.CTRL_TRIG.CHAIN_TO = DMA_CHAN
    dma_chan.CTRL_TRIG.INCR_WRITE = dma_chan.CTRL_TRIG.IRQ_QUIET = 1
    dma_chan.CTRL_TRIG.TREQ_SEL = devs.DREQ_ADC
    dma_chan.CTRL_TRIG.DATA_SIZE = 1
    
    dma_chan.CTRL_TRIG.EN = 1
    while adc.FCS.LEVEL:
        x = adc.FIFO_REG
    
    adc.CS.START_MANY = 1
    while dma_chan.CTRL_TRIG.BUSY:
        time.sleep_ms(10)
    adc.CS.START_MANY = 0
    dma_chan.CTRL_TRIG.EN = 0
    
    vals = [("%1.3f" % (val*3.3/4096)) for val in adc_buff]
    print(str(ADC_CHAN)+','+str(vals))
    led.toggle()
    time.sleep_ms(100)


# EOF

