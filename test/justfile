# Ensure that errors don't hide inside pipes
SHELL         = /bin/bash
.SHELLFLAGS   = -o pipefail -c

DIFF_CMD 	 := diff --brief --recursive --new-file
EXPECTED_DIR := expected
BUILD_DIR    ?= build

FATUL  ?= python3 ../fatul.py
DECODE ?= $(FATUL) decode -v
ENCODE ?= $(FATUL) encode -v
DUMP   ?= $(FATUL) dump -v

# Run tests and compare results with expected results
.PHONY: test
test: clean run-tests
	@echo "Comparing built results with the expected ones..."
	$(DIFF_CMD) "$(BUILD_DIR)" "$(EXPECTED_DIR)"
	@echo "all tests passed"

.PHONY: clean
clean:
	rm -rf "$(BUILD_DIR)"
	mkdir -p "$(BUILD_DIR)"

# Regenerate expected tests results by running tests and moving them to the expected dir
.PHONY: rebuild-expected
rebuild-expected: clean run-tests
	rm -rf "$(EXPECTED_DIR)"
	mkdir -p "$(EXPECTED_DIR)"
	mv "$(BUILD_DIR)"/* "$(EXPECTED_DIR)/"

# Perform all tests, storing results in the build dir
.PHONY: run-tests
run-tests:
	@echo "Running tests..."
	@echo "The 'Destination has a .json extension, ...' warning is expected"

	$(DECODE) $(BUILD_DIR)/bp_power__decoded.json raw/bp_power.txt
	$(DUMP) -p $(BUILD_DIR)/bp_power.json raw/bp_power.txt
	$(DECODE) -p --ids keep --sort none $(BUILD_DIR)/bp_power__ids=keep.json raw/bp_power.txt
	$(ENCODE) $(BUILD_DIR)/bp_power__ids=keep.json - | $(DUMP) -p $(BUILD_DIR)/bp_power__ids=keep__encoded.json -
	$(DECODE) -p --ids refs --sort none $(BUILD_DIR)/bp_power__ids=refs.json raw/bp_power.txt
	$(ENCODE) $(BUILD_DIR)/bp_power__ids=refs.json - | $(DUMP) -p $(BUILD_DIR)/bp_power__ids=refs__encoded.json -
	$(DECODE) -p --ids mixed --sort none $(BUILD_DIR)/bp_power__ids=mixed.json raw/bp_power.txt
	$(ENCODE) $(BUILD_DIR)/bp_power__ids=mixed.json - | $(DUMP) -p $(BUILD_DIR)/bp_power__ids=mixed__encoded.json -
	$(DECODE) -p --ids keep --sort entities $(BUILD_DIR)/bp_power__sort=entities.json raw/bp_power.txt
	$(DECODE) -p --ids keep --sort keys $(BUILD_DIR)/bp_power__sort=keys.json raw/bp_power.txt
	$(DECODE) -p --ids keep --sort all $(BUILD_DIR)/bp_power__sort=all.json raw/bp_power.txt

	$(DECODE) $(BUILD_DIR)/bp_logic__decoded.json raw/bp_logic.txt
	$(DUMP) -p $(BUILD_DIR)/bp_logic.json raw/bp_logic.txt
	$(DECODE) -p --ids keep --sort none $(BUILD_DIR)/bp_logic__ids=keep.json raw/bp_logic.txt
	$(ENCODE) $(BUILD_DIR)/bp_logic__ids=keep.json - | $(DUMP) -p $(BUILD_DIR)/bp_logic__ids=keep__encoded.json -
	$(DECODE) -p --ids refs --sort none $(BUILD_DIR)/bp_logic__ids=refs.json raw/bp_logic.txt
	$(ENCODE) $(BUILD_DIR)/bp_logic__ids=refs.json - | $(DUMP) -p $(BUILD_DIR)/bp_logic__ids=refs__encoded.json -
	$(DECODE) -p --ids mixed --sort none $(BUILD_DIR)/bp_logic__ids=mixed.json raw/bp_logic.txt
	$(ENCODE) $(BUILD_DIR)/bp_logic__ids=mixed.json - | $(DUMP) -p $(BUILD_DIR)/bp_logic__ids=mixed__encoded.json -
	$(DECODE) -p --ids keep --sort entities $(BUILD_DIR)/bp_logic__sort=entities.json raw/bp_logic.txt
	$(DECODE) -p --ids keep --sort keys $(BUILD_DIR)/bp_logic__sort=keys.json raw/bp_logic.txt
	$(DECODE) -p --ids keep --sort all $(BUILD_DIR)/bp_logic__sort=all.json raw/bp_logic.txt

	$(DUMP) -p $(BUILD_DIR)/rm_empty    raw/rm_empty.txt
	$(DUMP) -p $(BUILD_DIR)/bk_empty    raw/bk_empty.txt
	$(DUMP) -p $(BUILD_DIR)/bk_empty_bp raw/bk_empty_bp.txt
	$(DUMP) -p $(BUILD_DIR)/bk_nested   raw/bk_nested.txt

	$(ENCODE) $(BUILD_DIR)/rm_empty.json - | $(DUMP) -p $(BUILD_DIR)/rm_empty2.json -
	$(ENCODE) $(BUILD_DIR)/bk_empty      - | $(DUMP) -p $(BUILD_DIR)/bk_empty.json -
	$(ENCODE) $(BUILD_DIR)/bk_empty_bp   - | $(DUMP) -p $(BUILD_DIR)/bk_empty_bp.json -
	$(ENCODE) $(BUILD_DIR)/bk_nested     - | $(DUMP) -p $(BUILD_DIR)/bk_nested.json -
