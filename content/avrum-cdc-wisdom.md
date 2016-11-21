Title: Avrum's Clock Domain Crossing Widsom
Date: 2016-08-22
Modified: 2016-09-20
Category: Hardware
Tags: VHDL, Vivado

[Avrum](https://forums.xilinx.com/t5/user/viewprofilepage/user-id/7227) is an
active fellow on the Xilinx forums whenever clock domain crossing (CDC) issues
crop up. By default, and in contrast to ISE, Vivado assumes all clocks are
related. Thus, even with a proper synchronization circuit, Vivado needs to be
explicitly told not to try and time these paths. Avrum does an excellent job of
explaining the correct constraint relaxation to use and why not use what I call
the  "ostrich method" of just setting the clocks as asynchronous using
`set_clock_groups -asynchronous` or `set_false_path` between all path between
the clocks. This certainly is the easy way out but means you'll clobber all
other more delicate constraints and could mask a real clock crossing problem
where you've forgotten to synchronize.  I've tried to collect his posts here for
reference:

* [post](https://forums.xilinx.com/t5/Timing-Analysis/set-false-path/m-p/638630/highlight/true#M8189) - constraints on a reset synchronizer and the one of the few places I've seen mentioned using a `set_max_delay` on a single-bit synchronizer chain
* [post](https://forums.xilinx.com/t5/Timing-Analysis/Setting-ASYNC-REG-in-VHDL-for-Two-Flop-Synchronizer/m-p/701415/highlight/true#M9905) and [post](https://forums.xilinx.com/t5/Timing-Analysis/Setting-ASYNC-REG-in-VHDL-for-Two-Flop-Synchronizer/m-p/701603/highlight/true#M9917) - clever tcl commands to use to find module and register instances
* [post](https://forums.xilinx.com/t5/Timing-Analysis/What-does-quot-set-false-path-through-quot-do/m-p/397541/highlight/true#M5250) - more reset syncrhonization with a nice slide attached
* [post](https://forums.xilinx.com/t5/Vivado-TCL-Community/How-to-set-timing-constraint-in-this-case/m-p/510771/highlight/true#M2049) - long discussion about the difference between single bit and bus synchronization
* [post](https://forums.xilinx.com/t5/Timing-Analysis/Timing-Failure-MCMM-with-multiple-outputs/m-p/563460/highlight/true#M7580) -  long discussion of different types of CDC exceptions and why `set_max_delay` is almost always preferred
* [post](https://forums.xilinx.com/t5/Virtex-Family-FPGAs/idelayctrl-with-iodelay-group-example/m-p/320797/highlight/true#M16569) - not quite clock domain crossing but a clear explanation of IODELAYCTRL instantiation
* [post](https://forums.xilinx.com/t5/Virtex-Family-FPGAs/MTBF-equation-factors-for-Metastability-synchronizers-slack/m-p/536955/highlight/true#M20024) - discussion of mean time before failure (MTBF) for synchronizer chain and references new Vivado tcl command `report_synchronizer_mtbf` for Ultrascale parts
* [post](https://forums.xilinx.com/t5/Timing-Analysis/distributed-RAM-timing-errror-on-read/m-p/474298/highlight/true#M6206) - subtleties of distributed RAM which "is an odd beast - it is partly a synchronous element (the write) and partly a combinatorial element (the read)."
