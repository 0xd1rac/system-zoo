# Toolchain
CROSS_COMPILE ?= arm-none-eabi-
AS = $(CROSS_COMPILE)as
LD = $(CROSS_COMPILE)ld
OBJCOPY = $(CROSS_COMPILE)objcopy

# Directories
BUILD_DIR = build
SRC_DIR = .

# Files
BOOTROM_SRC = $(SRC_DIR)/bootrom.S
TEST_SRC = $(SRC_DIR)/test_program.S
BOOTROM_ELF = $(BUILD_DIR)/bootrom.elf
TEST_ELF = $(BUILD_DIR)/test_program.elf
BOOTROM_BIN = $(BUILD_DIR)/bootrom.bin
TEST_BIN = $(BUILD_DIR)/test_program.bin

# Flags
ASFLAGS = -march=armv4t -mthumb
LDFLAGS = -T $(SRC_DIR)/bootrom.ld

# Targets
all: $(BUILD_DIR) $(BOOTROM_BIN) $(TEST_BIN)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BOOTROM_ELF): $(BOOTROM_SRC)
	$(AS) $(ASFLAGS) -o $@ $<
	$(LD) $(LDFLAGS) -o $@ $@

$(TEST_ELF): $(TEST_SRC)
	$(AS) $(ASFLAGS) -o $@ $<
	$(LD) $(LDFLAGS) -o $@ $@

$(BOOTROM_BIN): $(BOOTROM_ELF)
	$(OBJCOPY) -O binary $< $@

$(TEST_BIN): $(TEST_ELF)
	$(OBJCOPY) -O binary $< $@

clean:
	rm -rf $(BUILD_DIR)

.PHONY: all clean 