module decode_stage (
    input wire clk,
    input wire rst_n,
    input wire [31:0] instruction,
    output reg [3:0] rd_addr,
    output reg [3:0] rs1_addr,
    output reg [3:0] rs2_addr,
    output wire [31:0] rs1_data,
    output wire [31:0] rs2_data,
    output reg [31:0] imm,
    output reg [3:0] alu_op,
    output reg mem_read,
    output reg mem_write,
    output reg reg_write
);

    // Register file
    reg [31:0] registers [15:0];
    
    // Instruction fields
    wire [3:0] opcode = instruction[31:28];
    wire [3:0] cond = instruction[27:24];
    wire [3:0] rd = instruction[23:20];
    wire [3:0] rs1 = instruction[19:16];
    wire [3:0] rs2 = instruction[15:12];
    wire [11:0] immediate = instruction[11:0];
    
    // ALU operation codes
    localparam ALU_ADD = 4'b0000;
    localparam ALU_SUB = 4'b0001;
    localparam ALU_AND = 4'b0010;
    localparam ALU_OR  = 4'b0011;
    localparam ALU_XOR = 4'b0100;
    localparam ALU_SHL = 4'b0101;
    localparam ALU_SHR = 4'b0110;
    localparam ALU_SLT = 4'b0111;
    
    // Instruction decode
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_addr <= 4'h0;
            rs1_addr <= 4'h0;
            rs2_addr <= 4'h0;
            imm <= 32'h0;
            alu_op <= ALU_ADD;
            mem_read <= 1'b0;
            mem_write <= 1'b0;
            reg_write <= 1'b0;
        end else begin
            // Default values
            mem_read <= 1'b0;
            mem_write <= 1'b0;
            reg_write <= 1'b0;
            
            case (opcode)
                4'b0000: begin // ADD
                    rd_addr <= rd;
                    rs1_addr <= rs1;
                    rs2_addr <= rs2;
                    alu_op <= ALU_ADD;
                    reg_write <= 1'b1;
                end
                4'b0001: begin // SUB
                    rd_addr <= rd;
                    rs1_addr <= rs1;
                    rs2_addr <= rs2;
                    alu_op <= ALU_SUB;
                    reg_write <= 1'b1;
                end
                4'b0010: begin // AND
                    rd_addr <= rd;
                    rs1_addr <= rs1;
                    rs2_addr <= rs2;
                    alu_op <= ALU_AND;
                    reg_write <= 1'b1;
                end
                4'b0011: begin // OR
                    rd_addr <= rd;
                    rs1_addr <= rs1;
                    rs2_addr <= rs2;
                    alu_op <= ALU_OR;
                    reg_write <= 1'b1;
                end
                4'b0100: begin // XOR
                    rd_addr <= rd;
                    rs1_addr <= rs1;
                    rs2_addr <= rs2;
                    alu_op <= ALU_XOR;
                    reg_write <= 1'b1;
                end
                4'b0101: begin // SHL
                    rd_addr <= rd;
                    rs1_addr <= rs1;
                    rs2_addr <= rs2;
                    alu_op <= ALU_SHL;
                    reg_write <= 1'b1;
                end
                4'b0110: begin // SHR
                    rd_addr <= rd;
                    rs1_addr <= rs1;
                    rs2_addr <= rs2;
                    alu_op <= ALU_SHR;
                    reg_write <= 1'b1;
                end
                4'b0111: begin // SLT
                    rd_addr <= rd;
                    rs1_addr <= rs1;
                    rs2_addr <= rs2;
                    alu_op <= ALU_SLT;
                    reg_write <= 1'b1;
                end
                4'b1000: begin // LOAD
                    rd_addr <= rd;
                    rs1_addr <= rs1;
                    imm <= {20{immediate[11]}, immediate};
                    mem_read <= 1'b1;
                    reg_write <= 1'b1;
                end
                4'b1001: begin // STORE
                    rs1_addr <= rs1;
                    rs2_addr <= rs2;
                    imm <= {20{immediate[11]}, immediate};
                    mem_write <= 1'b1;
                end
                default: begin
                    rd_addr <= 4'h0;
                    rs1_addr <= 4'h0;
                    rs2_addr <= 4'h0;
                    imm <= 32'h0;
                    alu_op <= ALU_ADD;
                end
            endcase
        end
    end
    
    // Register file read
    assign rs1_data = registers[rs1_addr];
    assign rs2_data = registers[rs2_addr];
    
    // Register file write
    always @(posedge clk) begin
        if (reg_write && rd_addr != 4'h0) begin
            registers[rd_addr] <= rs1_data; // Write back value will be connected here
        end
    end

endmodule 