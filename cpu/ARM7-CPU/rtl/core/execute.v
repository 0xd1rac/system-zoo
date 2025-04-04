module execute_stage (
    input wire clk,
    input wire rst_n,
    input wire [3:0] alu_op,
    input wire [31:0] rs1_data,
    input wire [31:0] rs2_data,
    input wire [31:0] imm,
    output reg [31:0] alu_result,
    output reg branch_taken,
    output reg [19:0] mem_addr,
    output reg [31:0] mem_wdata,
    output reg mem_we
);

    // ALU operation codes (matching decode stage)
    localparam ALU_ADD = 4'b0000;
    localparam ALU_SUB = 4'b0001;
    localparam ALU_AND = 4'b0010;
    localparam ALU_OR  = 4'b0011;
    localparam ALU_XOR = 4'b0100;
    localparam ALU_SHL = 4'b0101;
    localparam ALU_SHR = 4'b0110;
    localparam ALU_SLT = 4'b0111;
    
    // ALU operation
    always @(*) begin
        case (alu_op)
            ALU_ADD: alu_result = rs1_data + rs2_data;
            ALU_SUB: alu_result = rs1_data - rs2_data;
            ALU_AND: alu_result = rs1_data & rs2_data;
            ALU_OR:  alu_result = rs1_data | rs2_data;
            ALU_XOR: alu_result = rs1_data ^ rs2_data;
            ALU_SHL: alu_result = rs1_data << rs2_data[4:0];
            ALU_SHR: alu_result = rs1_data >> rs2_data[4:0];
            ALU_SLT: alu_result = {31'b0, ($signed(rs1_data) < $signed(rs2_data))};
            default: alu_result = 32'h0;
        endcase
    end
    
    // Branch logic
    always @(*) begin
        branch_taken = 1'b0;
        case (alu_op)
            ALU_SUB: begin
                // Branch if equal
                branch_taken = (alu_result == 32'h0);
            end
            ALU_SLT: begin
                // Branch if less than
                branch_taken = alu_result[0];
            end
            default: branch_taken = 1'b0;
        endcase
    end
    
    // Memory access logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mem_addr <= 20'h0;
            mem_wdata <= 32'h0;
            mem_we <= 1'b0;
        end else begin
            // Memory address calculation
            mem_addr <= (rs1_data + imm)[19:0];  // Only use 20 bits for 1MB address space
            mem_wdata <= rs2_data;
            mem_we <= (alu_op == 4'b1001);  // STORE instruction
        end
    end

endmodule 