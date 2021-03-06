# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import io
import pandas as pd


# Description of Transfer Control Descriptor (21.3.17/415 - 21.3.30/426)
TCD_DESCRIPTIONS_TSV = '''
full_name	short_description	description	page
SADDR	Source Address	Memory address pointing to the source data.	21.3.17/415
SOFF	Source Address Signed offset	Sign-extended offset applied to the current source address to form the next-state value as each source read is completed.	21.3.18/415
ATTR.SMOD	Source Address Modulo.	0: Source address modulo feature is disabled, Not 0: This value defines a specific address range specified to be the value after SADDR + SOFF calculation is performed or the original register value. The setting of this field provides the ability to implement a circular data queue easily. For data queues requiring power-of-2 size bytes, the queue should start at a 0-modulo-size address and the SMOD field should be set to the appropriate value for the queue, freezing the desired number of upper address bits. The value programmed into this field specifies the number of lower address bits allowed to change. For a circular queue application, the SOFF is typically set to the transfer size to implement post-increment addressing with the SMOD function constraining the addresses to a 0-modulo-size range.	21.3.19/416
ATTR.SSIZE	Source data transfer size	000: 8-bit, 001: 16-bit, 010: 32-bit, 100: 16-byte	21.3.19/416
ATTR.DMOD	Destination Address Modulo	0: Destination address modulo feature is disabled, Not 0: This value defines a specific address range specified to be the value after SADDR + SOFF calculation is performed or the original register value. The setting of this field provides the ability to implement a circular data queue easily. For data queues requiring power-of-2 size bytes, the queue should start at a 0-modulo-size address and the SMOD field should be set to the appropriate value for the queue, freezing the desired number of upper address bits. The value programmed into this field specifies the number of lower address bits allowed to change. For a circular queue application, the SOFF is typically set to the transfer size to implement post-increment addressing with the SMOD function constraining the addresses to a 0-modulo-size range.	21.3.19/416
ATTR.DSIZE	Destination data transfer size	000: 8-bit, 001: 16-bit, 010: 32-bit, 100: 16-byte	21.3.19/416
NBYTES_MLNO	Minor Byte Transfer Count	Number of bytes to be transferred in each service request of the channel. As a channel activates, the appropriate TCD contents load into the eDMA engine, and the appropriate reads and writes perform until the minor byte transfer count has transferred. This is an indivisible operation and cannot be halted. (Although, it may be stalled by using the bandwidth control field, or via preemption.) After the minor count is exhausted, the SADDR and DADDR values are written back into the TCD memory, the major iteration count is decremented and restored to the TCD memory. If the major iteration count is completed, additional processing is performed. NOTE: An NBYTES value of 0x0000_0000 is interpreted as a 4 GB transfer.	21.3.20/417
NBYTES_MLOFFNO.SMLOE	Source Minor Loop Offset Enable	Selects whether the minor loop offset is applied to the source address upon minor loop completion. 0: The minor loop offset is not applied to the SADDR, 1: The minor loop offset is applied to the SADDR	21.3.21/417
NBYTES_MLOFFNO.DMLOE	Destination Minor Loop Offset enable	Selects whether the minor loop offset is applied to the destination address upon minor loop completion. 0: The minor loop offset is not applied to the DADDR, 1: The minor loop offset is applied to the DADDR	21.3.21/417
NBYTES_MLOFFNO.NBYTES	Minor Byte Transfer Count	Number of bytes to be transferred in each service request of the channel. As a channel activates, the appropriate TCD contents load into the eDMA engine, and the appropriate reads and writes perform until the minor byte transfer count has transferred. This is an indivisible operation and cannot be halted; although, it may be stalled by using the bandwidth control field, or via preemption. After the minor count is exhausted, the SADDR and DADDR values are written back into the TCD memory, the major iteration count is decremented and restored to the TCD memory. If the major iteration count is completed, additional processing is performed.	21.3.21/417
NBYTES_MLOFFYES.SMLOE	Source Minor Loop Offset Enable	Selects whether the minor loop offset is applied to the source address upon minor loop completion. 0: The minor loop offset is not applied to the SADDR, 1: The minor loop offset is applied to the SADDR	21.3.22/418
NBYTES_MLOFFYES.DMLOE	Destination Minor Loop Offset enable	Selects whether the minor loop offset is applied to the destination address upon minor loop completion. 0: The minor loop offset is not applied to the DADDR, 1: The minor loop offset is applied to the DADDR	21.3.22/418
NBYTES_MLOFFYES.MLOFF	Minor Loop Offset	If SMLOE or DMLOE is set, this field represents a sign-extended offset applied to the source or destination address to form the next-state value after the minor loop completes.	21.3.22/418
NBYTES_MLOFFYES.NBYTES	Minor Byte Transfer Count	Number of bytes to be transferred in each service request of the channel. As a channel activates, the appropriate TCD contents load into the eDMA engine, and the appropriate reads and writes perform until the minor byte transfer count has transferred. This is an indivisible operation and cannot be halted; although, it may be stalled by using the bandwidth control field, or via preemption. After the minor count is exhausted, the SADDR and DADDR values are written back into the TCD memory, the major iteration count is decremented and restored to the TCD memory. If the major iteration count is completed, additional processing is performed.	21.3.22/418
SLAST	Last source Address Adjustment	Adjustment value added to the source address at the completion of the major iteration count. This value can be applied to restore the source address to the initial value, or adjust the address to reference the next data structure.	21.3.23/420
DADDR	Destination Address	Memory address pointing to the destination data.	21.3.24/420
DOFF	Destination Address Signed offset	Sign-extended offset applied to the current destination address to form the next-state value as each destination write is completed.	21.3.25/421
CITER_ELINKYES.ELINK	Enable channel-to-channel linking on minor-loop complete	As the channel completes the minor loop, this flag enables linking to another channel, defined by the LINKCH field. The link target channel initiates a channel service request via an internal mechanism that sets the TCDn_CSR[START] bit of the specified channel. If channel linking is disabled, the CITER value is extended to 15 bits in place of a link channel number. If the major loop is exhausted, this link mechanism is suppressed in favor of the MAJORELINK channel linking. NOTE: This bit must be equal to the BITER[ELINK] bit. Otherwise, a configuration error is reported. 0: The channel-to-channel linking is disabled, 1: The channel-to-channel linking is enabled	21.3.26/421
CITER_ELINKYES.LINKCH	Link Channel Number	If channel-to-channel linking is enabled (ELINK = 1), then after the minor loop is exhausted, the eDMA engine initiates a channel service request to the channel defined by these four bits by setting that channel’s TCDn_CSR[START] bit.	21.3.26/421
CITER_ELINKYES.ITER	Current Major Iteration Count	This 9-bit (ELINK = 1) or 15-bit (ELINK = 0) count represents the current major loop count for the channel. It is decremented each time the minor loop is completed and updated in the transfer control descriptor memory. After the major iteration count is exhausted, the channel performs a number of operations (e.g., final source and destination address calculations), optionally generating an interrupt to signal channel completion before reloading the CITER field from the beginning iteration count (BITER) field. NOTE: When the CITER field is initially loaded by software, it must be set to the same value as that contained in the BITER field. NOTE: If the channel is configured to execute a single service request, the initial values of BITER and CITER should be 0x0001.	21.3.26/421
CITER_ELINKNO.ELINK	Enable channel-to-channel linking on minor-loop complete	As the channel completes the minor loop, this flag enables linking to another channel, defined by the LINKCH field. The link target channel initiates a channel service request via an internal mechanism that sets the TCDn_CSR[START] bit of the specified channel. If channel linking is disabled, the CITER value is extended to 15 bits in place of a link channel number. If the major loop is exhausted, this link mechanism is suppressed in favor of the MAJORELINK channel linking. NOTE: This bit must be equal to the BITER[ELINK] bit. Otherwise, a configuration error is reported. 0: The channel-to-channel linking is disabled, 1: The channel-to-channel linking is enabled	21.3.27/422
CITER_ELINKNO.ITER	Current Major Iteration Count	This 9-bit (ELINK = 1) or 15-bit (ELINK = 0) count represents the current major loop count for the channel. It is decremented each time the minor loop is completed and updated in the transfer control descriptor memory. After the major iteration count is exhausted, the channel performs a number of operations (e.g., final source and destination address calculations), optionally generating an interrupt to signal channel completion before reloading the CITER field from the beginning iteration count (BITER) field. NOTE: When the CITER field is initially loaded by software, it must be set to the same value as that contained in the BITER field. NOTE: If the channel is configured to execute a single service request, the initial values of BITER and CITER should be 0x0001.E87	21.3.27/422
DLASTSGA	Destination last address adjustment or the memory address for the next transfer control descriptor to be loaded into this channel (scatter/gather).	If (TCDn_CSR[ESG] = 0) then adjustment value added to the destination address at the completion of the major iteration count. This value can apply to restore the destination address to the initial value or adjust the address to reference the next data structure. Otherwise, this address points to the beginning of a 0-modulo-32-byte region containing the next transfer control descriptor to be loaded into this channel. This channel reload is performed as the major iteration count completes. The scatter/gather address must be 0-modulo-32-byte, else a configuration error is reported.eference the next data structure.	21.3.28/423
CSR.BWC	Bandwidth Control	Throttles the amount of bus bandwidth consumed by the eDMA. In general, as the eDMA processes the minor loop, it continuously generates read/write sequences until the minor count is exhausted. This field forces the eDMA to stall after the completion of each read/write access to control the bus request bandwidth seen by the crossbar switch. NOTE: If the source and destination sizes are equal, this field is ignored between the first and second transfers and after the last write of each minor loop. This behavior is a side effect of reducing start-up latency. 00: No eDMA engine stalls, 01: Reserved, 10: eDMA engine stalls for 4 cycles after each r/w, 11: eDMA engine stalls for 8 cycles after each r/w	21.3.29/424
CSR.MAJORLINKCH	Link Channel Number	If (MAJORELINK = 0) then no channel-to-channel linking (or chaining) is performed after the major loop counter is exhausted. Otherwise, after the major loop counter is exhausted, the eDMA engine initiates a channel service request at the channel defined by these six bits by setting that channel’s TCDn_CSR[START] bit.	21.3.29/424
CSR.DONE	Channel Done	This flag indicates the eDMA has completed the major loop. The eDMA engine sets it as the CITER count reaches zero; The software clears it, or the hardware when the channel is activated. NOTE: This bit must be cleared to write the MAJORELINK or ESG bits.	21.3.29/424
CSR.ACTIVE	Channel Active	This flag signals the channel is currently in execution. It is set when channel service begins, and the eDMA clears it as the minor loop completes or if any error condition is detected. This bit resets to zero.	21.3.29/424
CSR.MAJORELINK	Enable channel-to-channel linking on major loop complete	As the channel completes the major loop, this flag enables the linking to another channel, defined by MAJORLINKCH. The link target channel initiates a channel service request via an internal mechanism that sets the TCDn_CSR[START] bit of the specified channel. NOTE: To support the dynamic linking coherency model, this field is forced to zero when written to while the TCDn_CSR[DONE] bit is set. 0: The channel-to-channel linking is disabled, 1: The channel-to-channel linking is enabled	21.3.29/424
CSR.ESG	Enable Scatter/Gather Processing	As the channel completes the major loop, this flag enables scatter/gather processing in the current channel. If enabled, the eDMA engine uses DLASTSGA as a memory pointer to a 0-modulo-32 address containing a 32-byte data structure loaded as the transfer control descriptor into the local memory. NOTE: To support the dynamic scatter/gather coherency model, this field is forced to zero when written to while the TCDn_CSR[DONE] bit is set. 0: The current channel’s TCD is normal format., 1: The current channel’s TCD specifies a scatter gather format. The DLASTSGA field provides a memory pointer to the next TCD to be loaded into this channel after the major loop completes its execution.	21.3.29/424
CSR.DREQ	Disable Request	If this flag is set, the eDMA hardware automatically clears the corresponding ERQ bit when the current major iteration count reaches zero. 0: The channel’s ERQ bit is not affected, 1: The channel’s ERQ bit is cleared when the major loop is complete	21.3.29/424
CSR.INTHALF	Enable an interrupt when major counter is half complete.	If this flag is set, the channel generates an interrupt request by setting the appropriate bit in the INT register when the current major iteration count reaches the halfway point. Specifically, the comparison performed by the eDMA engine is (CITER == (BITER >> 1)). This halfway point interrupt request is provided to support double-buffered (aka ping-pong) schemes or other types of data movement where the processor needs an early indication of the transfer’s progress. If BITER is set, do not use INTHALF. Use INTMAJOR instead. 0: The half-point interrupt is disabled, 1: The half-point interrupt is enabled	21.3.29/424
CSR.INTMAJOR	Enable an interrupt when major iteration count completes	If this flag is set, the channel generates an interrupt request by setting the appropriate bit in the INT when the current major iteration count reaches zero. 0: The end-of-major loop interrupt is disabled, 1: The end-of-major loop interrupt is enabled,	21.3.29/424
CSR.START	Channel Start	If this flag is set, the channel is requesting service. The eDMA hardware automatically clears this flag after the channel begins execution. 0: The channel is not explicitly started, 1: The channel is explicitly started via a software initiated service request,	21.3.29/424
BITER_ELINKYES.ELINK	Enable channel-to-channel linking on minor-loop complete	See CITER_ELINKYES[ELINK].	21.3.30/426
BITER_ELINKYES.LINKCH	Link Channel Number	See CITER_ELINKYES[LINKCH].	21.3.30/426
BITER_ELINKYES.ITER	Current Major Iteration Count	See CITER_ELINKYES[CITER].	21.3.30/426
BITER_ELINKNO.ELINK	Enable channel-to-channel linking on minor-loop complete	See CITER_ELINKNO[ELINK].	21.3.31/427
BITER_ELINKNO.ITER	Beginning Major Iteration Count	See CITER_ELINKNO[CITER].	21.3.31/427
'''.strip()

TCD_DESCRIPTIONS = pd.read_csv(io.BytesIO(TCD_DESCRIPTIONS_TSV.encode('utf8')),
                               sep='\t').set_index('full_name')
TCD_DESCRIPTIONS.loc[TCD_DESCRIPTIONS.description.isnull(), 'description'] = ''


# Description of DMA registers (21.3.1/391 - 21.3.15/411)
REGISTERS_DESCRIPTIONS_TSV = '''
full_name	short_description	description	page
CR.CX	Cancel Transfer	0: Normal operation, 1: Cancel the remaining data transfer. Stop the executing channel and force the minor loop to finish. The	21.3.1/391
CR.ECX	Error Cancel Transfer	0: Normal operation, 1: Cancel the remaining data transfer in the same fashion as the CX bit. Stop the executing channel and force the minor loop to finish. The cancel takes effect after the last write of the current read/write sequence. The ECX bit clears itself after the cancel is honored. In addition to cancelling the transfer, ECX treats the cancel as an error condition, thus updating the ES register and generating an optional error interrupt.	21.3.1/391
CR.EMLM	Enable Minor Loop Mapping	0: Disabled. TCDn.word2 is defined as a 32-bit NBYTES field, 1: Enabled. TCDn.word2 is redefined to include individual enable fields, an offset field, and the NBYTES field. The individual enable fields allow the minor loop offset to be applied to the source address, the destination address, or both. The NBYTES field is reduced when either offset is enabled.	21.3.1/391
CR.CLM	Continuous Link Mode	0: A minor loop channel link made to itself goes through channel arbitration before being activated again, 1: A minor loop channel link made to itself does not go through channel arbitration before being activated again. Upon minor loop completion, the channel activates again if that channel has a minor loop channel link enabled and the link channel is itself. This effectively applies the minor loop offsets and restarts the next minor loop.	21.3.1/391
CR.HALT	Halt DMA Operations	0: Normal operation, 1: Stall the start of any new channels. Executing channels are allowed to complete. Channel execution resumes when this bit is cleared.	21.3.1/391
CR.HOE	Halt On Error	0: Normal operation, 1: Any error causes the HALT bit to set. Subsequently, all service requests are ignored until the HALT bit	21.3.1/391
CR.ERCA	Enable Round Robin Channel Arbitration	0: Fixed priority arbitration is used for channel selection, 1: Round robin arbitration is used for channel selection .	21.3.1/391
CR.EDBG	Enable Debug	0: When in debug mode, the DMA continues to operate, 1: When in debug mode, the DMA stalls the start of a new channel. Executing channels are allowed to complete. Channel execution resumes when the system exits debug mode or the EDBG bit is cleared.	21.3.1/391
ES.VLD	Logical OR of all ERR status bits	0: No ERR bits are set, 1: At least one ERR bit is set indicating a valid error exists that has not been cleared	21.3.2/392
ES.ECX	Transfer Cancelled	0: No cancelled transfers, 1: The last recorded entry was a cancelled transfer by the error cancel transfer input	21.3.2/392
ES.CPE	Channel Priority Error	0: No channel priority error, 1: The last recorded error was a configuration error in the channel priorities . Channel priorities are not unique.	21.3.2/392
ES.ERRCHN	Error Channel Number or Cancelled Channel Number	The channel number of the last recorded error (excluding CPE errors) or last recorded error cancelled transfer .	21.3.2/392
ES.SAE	Source Address Error	0: No source address configuration error., 1: The last recorded error was a configuration error detected in the TCDn_SADDR field. TCDn_SADDR is inconsistent with TCDn_ATTR[SSIZE].	21.3.2/392
ES.SOE	Source Offset Error	0: No source offset configuration error, 1: The last recorded error was a configuration error detected in the TCDn_SOFF field. TCDn_SOFF is inconsistent with TCDn_ATTR[SSIZE].	21.3.2/392
ES.DAE	Destination Address Error	0: No destination address configuration error, 1: The last recorded error was a configuration error detected in the TCDn_DADDR field. TCDn_DADDR is inconsistent with TCDn_ATTR[DSIZE].	21.3.2/392
ES.DOE	Destination Offset Error	0: No destination offset configuration error, 1: The last recorded error was a configuration error detected in the TCDn_DOFF field. TCDn_DOFF is inconsistent with TCDn_ATTR[DSIZE].	21.3.2/392
ES.NCE	NBYTES/CITER Configuration Error	0: No NBYTES/CITER configuration error, 1: The last recorded error was a configuration error detected in the TCDn_NBYTES or TCDn_CITER fields.  One of: 1) TCDn_NBYTES is not a multiple of TCDn_ATTR[SSIZE] and TCDn_ATTR[DSIZE], or 2) TCDn_CITER[CITER] is equal to zero, or 3) TCDn_CITER[ELINK] is not equal to TCDn_BITER[ELINK]	21.3.2/392
ES.SGE	Scatter/Gather Configuration Error	0: No scatter/gather configuration error, 1: The last recorded error was a configuration error detected in the TCDn_DLASTSGA field. This field is checked at the beginning of a scatter/gather operation after major loop completion if TCDn_CSR[ESG] is enabled. TCDn_DLASTSGA is not on a 32 byte boundary.	21.3.2/392
ES.SBE	Source Bus Error	0: No source bus error, 1: The last recorded error was a bus error on a source read	21.3.2/392
ES.DBE	Destination Bus Error	0: No destination bus error, 1: The last recorded error was a bus error on a destination write	21.3.2/392
ERQ	Enable Request Register		21.3.3/394
EEI	Enable Error Interrupt Register		21.3.4/397
INT	Interrupt Request Register		21.3.13/406
ERR	Error Register		21.3.14/409
HRS	Hardware Request Status Register		21.3.15/411
'''.strip()

REGISTERS_DESCRIPTIONS = pd.read_csv(io.BytesIO(REGISTERS_DESCRIPTIONS_TSV
                                                .encode('utf8')),
                                     sep='\t').set_index('full_name')
REGISTERS_DESCRIPTIONS.loc[REGISTERS_DESCRIPTIONS.description.isnull(),
                           'description'] = ''


# Description of DMA channel priority register DCHPRI (21.3.16/414)
DCHPRI_DESCRIPTIONS_TSV = '''
full_name	short_description	description	page
ECP	Enable Channel Preemption	0: Channel n cannot be suspended by a higher priority channel’s service request, 1: Channel n can be temporarily suspended by the service request of a higher priority channel	21.3.16/414
DPA	Disable Preempt Ability	0: Channel n can suspend a lower priority channel, 1: Channel n cannot suspend any channel, regardless of channel priority	21.3.16/414
CHPRI	Channel n Arbitration Priority	Channel priority when fixed-priority arbitration is enabled.  NOTE: Reset value for the channel priority fields, CHPRI, is equal to the corresponding channel number for each priority register, i.e., DCHPRI15[CHPRI] equals 0b1111.	21.3.16/414
'''.strip()

DCHPRI_DESCRIPTIONS = pd.read_csv(io.BytesIO(DCHPRI_DESCRIPTIONS_TSV
                                             .encode('utf8')),
                                  sep='\t').set_index('full_name')
DCHPRI_DESCRIPTIONS.loc[DCHPRI_DESCRIPTIONS.description.isnull(),
                        'description'] = ''


# Description of DMA channel priority register DCHPRI (21.3.16/414)
MUX_CHCFG_DESCRIPTIONS_TSV = '''
full_name	short_description	description	page
ENBL	DMA Channel Enable	Enables the DMA channel. 0: DMA channel is disabled. This mode is primarily used during configuration of the DMA Mux. The DMA has separate channel enables/disables, which should be used to disable or re-configure a DMA channel. 1: DMA channel is enabled	20.3.1/366
TRIG	DMA Channel Trigger Enable	Enables the periodic trigger capability for the triggered DMA channel. 0: Triggering is disabled. If triggering is disabled, and the ENBL bit is set, the DMA Channel will simply route the specified source to the DMA channel. (Normal mode) 1: Triggering is enabled. If triggering is enabled, and the ENBL bit is set, the DMAMUX is in Periodic Trigger mode.	20.3.1/366
SOURCE	DMA Channel Source (Slot)	Specifies which DMA source, if any, is routed to a particular DMA channel. See your device's chip configuration details for further details about the peripherals and their slot numbers.	20.3.1/366
'''.strip()

MUX_CHCFG_DESCRIPTIONS = pd.read_csv(io.BytesIO(MUX_CHCFG_DESCRIPTIONS_TSV
                                                .encode('utf8')),
                                     sep='\t').set_index('full_name')
MUX_CHCFG_DESCRIPTIONS.loc[MUX_CHCFG_DESCRIPTIONS.description.isnull(),
                           'description'] = ''

DMAMUX_SOURCE_ADC0 = 40  # from `kinetis.h`
DMAMUX_SOURCE_ADC1 = 41  # from `kinetis.h`
DMAMUX_SOURCE_PDB = 48  # from `kinetis.h`
HW_TCDS_ADDR = 0x40009000
