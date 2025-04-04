module fetch_stage (
    input wire clk,
    input wire rst_n,
    input wire stall,
    input wire flush,
    input wire branch_taken,
    input wire [31:0] branch_target,
    output reg [31:0] pc,
    output reg [31:0] instruction,
    output reg [19:0] mem_addr,
    input wire [31:0] mem_rdata,
    output reg mem_re,
    input wire mem_ready
);

    // Program counter register
    reg [31:0] next_pc;
    
    // Fetch state machine
    localparam IDLE = 2'b00;
    localparam WAIT = 2'b01;
    localparam DONE = 2'b10;
    
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
                if (!stall)
                    next_state = WAIT;
            end
            WAIT: begin
                if (mem_ready)
                    next_state = DONE;
            end
            DONE: begin
                next_state = IDLE;
            end
            default: next_state = IDLE;
        endcase
    end
    
    // Program counter logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pc <= 32'h0;
            next_pc <= 32'h4;
        end else if (!stall) begin
            if (branch_taken) begin
                pc <= branch_target;
                next_pc <= branch_target + 32'h4;
            end else if (state == DONE) begin
                pc <= next_pc;
                next_pc <= next_pc + 32'h4;
            end
        end
    end
    
    // Memory interface logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mem_addr <= 20'h0;
            mem_re <= 1'b0;
            instruction <= 32'h0;
        end else begin
            case (state)
                IDLE: begin
                    if (!stall) begin
                        mem_addr <= pc[19:0];  // Only use 20 bits for 1MB address space
                        mem_re <= 1'b1;
                    end
                end
                WAIT: begin
                    mem_re <= 1'b0;
                end
                DONE: begin
                    instruction <= mem_rdata;
                end
            endcase
        end
    end

endmodule 