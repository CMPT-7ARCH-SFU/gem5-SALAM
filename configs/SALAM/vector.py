import m5
from m5.objects import *
from m5.util import *
import ConfigParser
from HWAccConfig import *

def buildHead(options, system, clstr):
    # Specify the path to the mobilenet accelerator descriptions
    hw_path = options.accpath + "/vector/hw"
    hw_config_path = hw_path + "/configs/head/"
    hw_ir_path = hw_path + "/ir/head/"
    local_low = 0x2F000000
    local_high = 0x2F001ADE
    local_range = AddrRange(local_low, local_high)
    external_range = [AddrRange(0x00000000, local_low-1),
                      AddrRange(local_high+1, 0xFFFFFFFF)]
    clstr._attach_bridges(system, local_range, external_range)
    clstr._connect_caches(system, options, l2coherent=False)
    gic = system.realview.gic

    # Add the top function
    acc = "top"
    config = hw_config_path + acc + ".ini"
    ir = hw_ir_path + acc + ".ll"
    clstr.top = CommInterface(devicename=acc, gic=gic)
    AccConfig(clstr.top, config, ir)
    clstr._connect_hwacc(clstr.top)
    clstr.top.local = clstr.local_bus.slave
    # clstr.top.enable_debug_msgs = True

    # Add the Stream DMAs
    addr = local_low + 0x0041
    clstr.stream_dma0 = StreamDma(pio_addr=addr, pio_size=32, gic=gic, max_pending=32)
    clstr.stream_dma0.stream_addr=addr+32
    clstr.stream_dma0.stream_size=8
    clstr.stream_dma0.pio_delay='1ns'
    clstr.stream_dma0.rd_int = 210
    clstr.stream_dma0.wr_int = 211
    clstr._connect_dma(system, clstr.stream_dma0)

    # Add the cluster DMA
    addr = local_low + 0x00069
    clstr.dma = NoncoherentDma(pio_addr=addr, pio_size=21, gic=gic, int_num=95)
    clstr._connect_cluster_dma(system, clstr.dma)

    # Add the Normal Convolution
    acc = "S1"
    config = hw_config_path + acc + ".ini"
    ir = hw_ir_path + acc + ".ll"
    clstr.NormalConv = CommInterface(devicename=acc, gic=gic)
    AccConfig(clstr.NormalConv, config, ir)
    clstr._connect_hwacc(clstr.NormalConv)
    clstr.NormalConv.stream = clstr.stream_dma0.stream_out
    clstr.NormalConv.enable_debug_msgs = True

    addr = local_low + 0x0081
    spmRange = AddrRange(addr, addr+(160*2*3))
    clstr.NormalConvBuffer = ScratchpadMemory(range=spmRange)
    clstr.NormalConvBuffer.conf_table_reported = False
    clstr.NormalConvBuffer.ready_mode=True
    clstr.NormalConvBuffer.port = clstr.local_bus.master
    for i in range(1):
        clstr.NormalConv.spm = clstr.NormalConvBuffer.spm_ports

    addr = local_low + 0x0441
    spmRange = AddrRange(addr, addr+27)
    clstr.NormalConvWindow = ScratchpadMemory(range=spmRange)
    clstr.NormalConvWindow.conf_table_reported = False
    clstr.NormalConvWindow.ready_mode=True
    clstr.NormalConvWindow.port = clstr.local_bus.master
    for i in range(27):
        clstr.NormalConv.spm = clstr.NormalConvWindow.spm_ports

    addr = local_low + 0x045C
    spmRange = AddrRange(addr, addr+(24*27))
    clstr.NormalConvWeights = ScratchpadMemory(range=spmRange)
    clstr.NormalConvWeights.conf_table_reported = False
    clstr.NormalConvWeights.ready_mode=True
    clstr.NormalConvWeights.port = clstr.local_bus.master
    for i in range(1):
        clstr.NormalConv.spm = clstr.NormalConvWeights.spm_ports

    addr = local_low + 0x06E4
    spmRange = AddrRange(addr, addr+(24*6))
    clstr.NormalConvQParams = ScratchpadMemory(range=spmRange)
    clstr.NormalConvQParams.conf_table_reported = False
    clstr.NormalConvQParams.ready_mode=True
    clstr.NormalConvQParams.port = clstr.local_bus.master
    for i in range(1):
        clstr.NormalConv.spm = clstr.NormalConvQParams.spm_ports

    addr = local_low + 0x0774
    clstr.NormalConvOut = StreamBuffer(stream_address=addr, stream_size=1, buffer_size=8)
    clstr.NormalConv.stream = clstr.NormalConvOut.stream_in

    # Add the Depthwise Convolution
    acc = "S2"
    config = hw_config_path + acc + ".ini"
    ir = hw_ir_path + acc + ".ll"
    clstr.DWConv = CommInterface(devicename=acc, gic=gic)
    AccConfig(clstr.DWConv, config, ir)
    clstr._connect_hwacc(clstr.DWConv)
    clstr.DWConv.stream = clstr.NormalConvOut.stream_out

    addr = local_low + 0x0775
    spmRange = AddrRange(addr, addr+(80*2*24))
    clstr.DWConvBuffer = ScratchpadMemory(range=spmRange)
    clstr.DWConvBuffer.conf_table_reported = False
    clstr.DWConvBuffer.ready_mode=True
    clstr.DWConvBuffer.port = clstr.local_bus.master
    for i in range(1):
        clstr.DWConv.spm = clstr.DWConvBuffer.spm_ports

    addr = local_low + 0x1675
    spmRange = AddrRange(addr, addr+(9*24))
    clstr.DWConvWindow = ScratchpadMemory(range=spmRange)
    clstr.DWConvWindow.conf_table_reported = False
    clstr.DWConvWindow.ready_mode=True
    clstr.DWConvWindow.port = clstr.local_bus.master
    for i in range(1):
        clstr.DWConv.spm = clstr.DWConvWindow.spm_ports

    addr = local_low + 0x174D
    spmRange = AddrRange(addr, addr+24)
    clstr.DWConvOutBuffer = ScratchpadMemory(range=spmRange)
    clstr.DWConvOutBuffer.conf_table_reported = False
    clstr.DWConvOutBuffer.ready_mode=True
    clstr.DWConvOutBuffer.port = clstr.local_bus.master
    for i in range(1):
        clstr.DWConv.spm = clstr.DWConvOutBuffer.spm_ports

    addr = local_low + 0x1765
    spmRange = AddrRange(addr, addr+(24*10))
    clstr.DWConvWeights = ScratchpadMemory(range=spmRange)
    clstr.DWConvWeights.conf_table_reported = False
    clstr.DWConvWeights.ready_mode=True
    clstr.DWConvWeights.port = clstr.local_bus.master
    for i in range(1):
        clstr.DWConv.spm = clstr.DWConvWeights.spm_ports

    addr = local_low + 0x1855
    spmRange = AddrRange(addr, addr+(24*6))
    clstr.DWConvQParams = ScratchpadMemory(range=spmRange)
    clstr.DWConvQParams.conf_table_reported = False
    clstr.DWConvQParams.ready_mode=True
    clstr.DWConvQParams.port = clstr.local_bus.master
    for i in range(1):
        clstr.DWConv.spm = clstr.DWConvQParams.spm_ports

    addr = local_low + 0x18E5
    clstr.DWConvOut = StreamBuffer(stream_address=addr, stream_size=1, buffer_size=8)
    clstr.DWConv.stream = clstr.DWConvOut.stream_in

    # Add the Pointwise Convolution
    acc = "S3"
    config = hw_config_path + acc + ".ini"
    ir = hw_ir_path + acc + ".ll"
    clstr.PWConv = CommInterface(devicename=acc, gic=gic)
    AccConfig(clstr.PWConv, config, ir)
    clstr._connect_hwacc(clstr.PWConv)
    clstr.PWConv.stream = clstr.DWConvOut.stream_out

    addr = local_low + 0x18E6
    spmRange = AddrRange(addr, addr+24)
    clstr.PWConvLocalFeat = ScratchpadMemory(range=spmRange)
    clstr.PWConvLocalFeat.conf_table_reported = False
    clstr.PWConvLocalFeat.ready_mode=True
    clstr.PWConvLocalFeat.port = clstr.local_bus.master
    for i in range(1):
        clstr.PWConv.spm = clstr.PWConvLocalFeat.spm_ports

    addr = local_low + 0x18FE
    spmRange = AddrRange(addr, addr+(24*16))
    clstr.PWConvWeights = ScratchpadMemory(range=spmRange)
    clstr.PWConvWeights.conf_table_reported = False
    clstr.PWConvWeights.ready_mode=True
    clstr.PWConvWeights.port = clstr.local_bus.master
    for i in range(1):
        clstr.PWConv.spm = clstr.PWConvWeights.spm_ports

    addr = local_low + 0x1A7E
    spmRange = AddrRange(addr, addr+(16*6))
    clstr.PWConvQParams = ScratchpadMemory(range=spmRange)
    clstr.PWConvQParams.conf_table_reported = False
    clstr.PWConvQParams.ready_mode=True
    clstr.PWConvQParams.port = clstr.local_bus.master
    for i in range(1):
        clstr.PWConv.spm = clstr.PWConvQParams.spm_ports

    clstr.PWConv.stream = clstr.stream_dma0.stream_in


def makeHWAcc(options, system):
    system.head = AccCluster()
    buildHead(options, system, system.head)

