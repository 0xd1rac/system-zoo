module tb_top;
    // Clock and reset
    reg clk;
    reg rst_n;
    
    // Memory interface
    wire [19:0] mem_addr;
    wire [31:0] mem_wdata;
    reg [31:0] mem_rdata;
    wire mem_we;
    wire mem_re;
    reg mem_ready;
    
    // SRAM interface
    wire [19:0] sram_addr;
    wire [31:0] sram_wdata;
    reg [31:0] sram_rdata;
    wire sram_we;
    wire sram_re;
    
    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    // Reset generation
    initial begin
        rst_n = 0;
        #100 rst_n = 1;
    end
    
    // Memory simulation
    reg [31:0] memory [0:262143];  // 1MB memory (20-bit address)
    
    // Initialize memory with test program
    initial begin
        // Simple test program
        memory[0] = 32'h12345678;  // ADD r1, r2, r3
        memory[1] = 32'h23456789;  // SUB r4, r5, r6
        memory[2] = 32'h34567890;  // AND r7, r8, r9
        memory[3] = 32'h45678901;  // OR r10, r11, r12
        memory[4] = 32'h56789012;  // XOR r13, r14, r15
    end
    
    // Memory read/write simulation
    always @(posedge clk) begin
        if (sram_re)
            sram_rdata <= memory[sram_addr];
        if (sram_we)
            memory[sram_addr] <= sram_wdata;
    end
    
    // Memory ready signal generation
    always @(posedge clk) begin
        if (rst_n) begin
            if (mem_re || mem_we)
                mem_ready <= 1;
            else
                mem_ready <= 0;
        end else begin
            mem_ready <= 0;
        end
    end
    
    // Instantiate CPU
    arm7_cpu cpu (
        .clk(clk),
        .rst_n(rst_n),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_rdata(mem_rdata),
        .mem_we(mem_we),
        .mem_re(mem_re),
        .mem_ready(mem_ready)
    );
    
    // Instantiate SRAM controller
    sram_ctrl sram (
        .clk(clk),
        .rst_n(rst_n),
        .addr(mem_addr),
        .wdata(mem_wdata),
        .rdata(mem_rdata),
        .we(mem_we),
        .re(mem_re),
        .ready(mem_ready),
        .sram_addr(sram_addr),
        .sram_wdata(sram_wdata),
        .sram_rdata(sram_rdata),
        .sram_we(sram_we),
        .sram_re(sram_re)
    );
    
    // Test monitoring
    initial begin
        $monitor("Time=%0t pc=%h instruction=%h", $time, cpu.pc, cpu.instruction);
        
        // Add waveform dumping
        $dumpfile("tb_top.vcd");
        $dumpvars(0, tb_top);
        
        // Run simulation
        #1000;
        $finish;
    end

endmodule 