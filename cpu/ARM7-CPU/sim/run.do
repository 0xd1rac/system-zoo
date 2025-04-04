# Create work library
vlib work
vmap work work

# Compile Verilog files
vlog ../rtl/top.v
vlog ../rtl/core/fetch.v
vlog ../rtl/core/decode.v
vlog ../rtl/core/execute.v
vlog ../rtl/memory/sram_ctrl.v
vlog ../tb/tb_top.v

# Start simulation
vsim -novopt work.tb_top

# Add waves
add wave -noupdate -divider {Clock and Reset}
add wave -noupdate /tb_top/clk
add wave -noupdate /tb_top/rst_n

add wave -noupdate -divider {CPU Interface}
add wave -noupdate /tb_top/cpu/pc
add wave -noupdate /tb_top/cpu/instruction
add wave -noupdate /tb_top/mem_addr
add wave -noupdate /tb_top/mem_wdata
add wave -noupdate /tb_top/mem_rdata
add wave -noupdate /tb_top/mem_we
add wave -noupdate /tb_top/mem_re
add wave -noupdate /tb_top/mem_ready

add wave -noupdate -divider {SRAM Interface}
add wave -noupdate /tb_top/sram/sram_addr
add wave -noupdate /tb_top/sram/sram_wdata
add wave -noupdate /tb_top/sram/sram_rdata
add wave -noupdate /tb_top/sram/sram_we
add wave -noupdate /tb_top/sram/sram_re

# Run simulation
run -all

# Save wave file
write wave wave.do 