module arm7_cpu (
    input wire clk,
    input wire rst_n,
    
    // Memory interface
    output wire [19:0] mem_addr,    // 1MB address space
    output wire [31:0] mem_wdata,
    input wire [31:0] mem_rdata,
    output wire mem_we,
    output wire mem_re,
    input wire mem_ready
);

    // Internal signals
    wire [31:0] pc;
    wire [31:0] instruction;
    wire [31:0] alu_result;
    wire branch_taken;
    
    // Pipeline control signals
    wire stall;
    wire flush;
    
    // Fetch stage
    fetch_stage fetch (
        .clk(clk),
        .rst_n(rst_n),
        .stall(stall),
        .flush(flush),
        .branch_taken(branch_taken),
        .branch_target(alu_result),
        .pc(pc),
        .instruction(instruction),
        .mem_addr(mem_addr),
        .mem_rdata(mem_rdata),
        .mem_re(mem_re),
        .mem_ready(mem_ready)
    );
    
    // Decode stage
    wire [3:0] rd_addr;
    wire [3:0] rs1_addr;
    wire [3:0] rs2_addr;
    wire [31:0] rs1_data;
    wire [31:0] rs2_data;
    wire [31:0] imm;
    wire [3:0] alu_op;
    wire mem_read;
    wire mem_write;
    wire reg_write;
    
    decode_stage decode (
        .clk(clk),
        .rst_n(rst_n),
        .instruction(instruction),
        .rd_addr(rd_addr),
        .rs1_addr(rs1_addr),
        .rs2_addr(rs2_addr),
        .rs1_data(rs1_data),
        .rs2_data(rs2_data),
        .imm(imm),
        .alu_op(alu_op),
        .mem_read(mem_read),
        .mem_write(mem_write),
        .reg_write(reg_write)
    );
    
    // Execute stage
    execute_stage execute (
        .clk(clk),
        .rst_n(rst_n),
        .alu_op(alu_op),
        .rs1_data(rs1_data),
        .rs2_data(rs2_data),
        .imm(imm),
        .alu_result(alu_result),
        .branch_taken(branch_taken),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_we(mem_we)
    );

endmodule 