module sram_ctrl (
    input wire clk,
    input wire rst_n,
    
    // CPU interface
    input wire [19:0] addr,      // 1MB address space
    input wire [31:0] wdata,
    output reg [31:0] rdata,
    input wire we,
    input wire re,
    output reg ready,
    
    // SRAM interface
    output reg [19:0] sram_addr,
    output reg [31:0] sram_wdata,
    input wire [31:0] sram_rdata,
    output reg sram_we,
    output reg sram_re
);

    // Memory access states
    localparam IDLE = 2'b00;
    localparam READ = 2'b01;
    localparam WRITE = 2'b10;
    localparam DONE = 2'b11;
    
    reg [1:0] state;
    reg [1:0] next_state;
    
    // State machine
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end
    
    // Next state logic
    always @(*) begin
        next_state = state;
        case (state)
            IDLE: begin
                if (we)
                    next_state = WRITE;
                else if (re)
                    next_state = READ;
            end
            READ: begin
                next_state = DONE;
            end
            WRITE: begin
                next_state = DONE;
            end
            DONE: begin
                next_state = IDLE;
            end
            default: next_state = IDLE;
        endcase
    end
    
    // Memory control logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sram_addr <= 20'h0;
            sram_wdata <= 32'h0;
            sram_we <= 1'b0;
            sram_re <= 1'b0;
            rdata <= 32'h0;
            ready <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    sram_we <= 1'b0;
                    sram_re <= 1'b0;
                    ready <= 1'b0;
                    if (we || re) begin
                        sram_addr <= addr;
                        sram_wdata <= wdata;
                    end
                end
                READ: begin
                    sram_re <= 1'b1;
                    ready <= 1'b0;
                end
                WRITE: begin
                    sram_we <= 1'b1;
                    ready <= 1'b0;
                end
                DONE: begin
                    sram_we <= 1'b0;
                    sram_re <= 1'b0;
                    ready <= 1'b1;
                    if (state == READ)
                        rdata <= sram_rdata;
                end
            endcase
        end
    end

endmodule 