DIFF_CMD 	 := "diff --brief --recursive --new-file"
EXPECTED_DIR := "test/expected"

FATUL  := "python3 fatul.py"
DECODE := FATUL + " decode -v"
ENCODE := FATUL + " encode -v"
DUMP   := FATUL + " dump -v"

# Run tests and compare results with expected results
test: clean run-tests
    @echo "Comparing built results with the expected ones..."
    {{DIFF_CMD}} "test/build" "{{EXPECTED_DIR}}"
    @echo "all tests passed"

# Remove temporary build files
clean:
    rm -rf "test/build"
    mkdir -p "test/build"

# Regenerate expected tests results by running tests and moving them to the expected dir
rebuild-expected: clean run-tests
    rm -rf "{{EXPECTED_DIR}}"
    mkdir -p "{{EXPECTED_DIR}}"
    mv "test/build"/* "{{EXPECTED_DIR}}/"

# Perform all tests, storing results in the build dir
run-tests:
    #!/usr/bin/env bash
    echo "Running tests..."
    echo "The 'Destination has a .json extension, ...' warning is expected"
    set -euxo pipefail

    {{DECODE}} test/build/bp_power__decoded.json test/raw/bp_power.txt
    {{DUMP}} -p test/build/bp_power.json test/raw/bp_power.txt
    {{DECODE}} -p --ids keep --sort none test/build/bp_power__ids=keep.json test/raw/bp_power.txt

    {{ENCODE}} test/build/bp_power__ids=keep.json - | {{DUMP}} -p test/build/bp_power__ids=keep__encoded.json -
    {{DECODE}} -p --ids refs --sort none test/build/bp_power__ids=refs.json test/raw/bp_power.txt
    {{ENCODE}} test/build/bp_power__ids=refs.json - | {{DUMP}} -p test/build/bp_power__ids=refs__encoded.json -
    {{DECODE}} -p --ids mixed --sort none test/build/bp_power__ids=mixed.json test/raw/bp_power.txt
    {{ENCODE}} test/build/bp_power__ids=mixed.json - | {{DUMP}} -p test/build/bp_power__ids=mixed__encoded.json -
    {{DECODE}} -p --ids keep --sort entities test/build/bp_power__sort=entities.json test/raw/bp_power.txt
    {{DECODE}} -p --ids keep --sort keys test/build/bp_power__sort=keys.json test/raw/bp_power.txt
    {{DECODE}} -p --ids keep --sort all test/build/bp_power__sort=all.json test/raw/bp_power.txt

    {{DECODE}} test/build/bp_logic__decoded.json test/raw/bp_logic.txt
    {{DUMP}} -p test/build/bp_logic.json test/raw/bp_logic.txt
    {{DECODE}} -p --ids keep --sort none test/build/bp_logic__ids=keep.json test/raw/bp_logic.txt
    {{ENCODE}} test/build/bp_logic__ids=keep.json - | {{DUMP}} -p test/build/bp_logic__ids=keep__encoded.json -
    {{DECODE}} -p --ids refs --sort none test/build/bp_logic__ids=refs.json test/raw/bp_logic.txt
    {{ENCODE}} test/build/bp_logic__ids=refs.json - | {{DUMP}} -p test/build/bp_logic__ids=refs__encoded.json -
    {{DECODE}} -p --ids mixed --sort none test/build/bp_logic__ids=mixed.json test/raw/bp_logic.txt
    {{ENCODE}} test/build/bp_logic__ids=mixed.json - | {{DUMP}} -p test/build/bp_logic__ids=mixed__encoded.json -
    {{DECODE}} -p --ids keep --sort entities test/build/bp_logic__sort=entities.json test/raw/bp_logic.txt
    {{DECODE}} -p --ids keep --sort keys test/build/bp_logic__sort=keys.json test/raw/bp_logic.txt
    {{DECODE}} -p --ids keep --sort all test/build/bp_logic__sort=all.json test/raw/bp_logic.txt

    {{DUMP}} -p test/build/rm_empty    test/raw/rm_empty.txt
    {{DUMP}} -p test/build/bk_empty    test/raw/bk_empty.txt
    {{DUMP}} -p test/build/bk_empty_bp test/raw/bk_empty_bp.txt
    {{DUMP}} -p test/build/bk_nested   test/raw/bk_nested.txt

    {{ENCODE}} test/build/rm_empty.json - | {{DUMP}} -p test/build/rm_empty2.json -
    {{ENCODE}} test/build/bk_empty      - | {{DUMP}} -p test/build/bk_empty.json -
    {{ENCODE}} test/build/bk_empty_bp   - | {{DUMP}} -p test/build/bk_empty_bp.json -
    {{ENCODE}} test/build/bk_nested     - | {{DUMP}} -p test/build/bk_nested.json -

    {{ENCODE}} test/build/bk_nested/blueprint.json - | {{DUMP}} -p test/build/bk_nested-bp.json -
    {{ENCODE}} test/build/bk_nested/blueprint.json - | {{DECODE}} -p test/build/bk_nested/blueprint.json -

    {{DUMP}} test/build/bp_edit1_dump.json test/raw/bp_edit1.txt
    {{DUMP}} test/build/bp_edit2_dump.json test/raw/bp_edit2.txt
    {{DUMP}} test/build/bp_edit3_dump.json test/raw/bp_edit3.txt

    {{DECODE}} test/build/bp_edit1.json test/raw/bp_edit1.txt
    {{DECODE}} test/build/bp_edit2.json test/raw/bp_edit2.txt
    {{DECODE}} test/build/bp_edit3.json test/raw/bp_edit3.txt
    cp test/build/bp_edit1.json test/build/bp_edit_tmp.json
    {{DECODE}} test/build/bp_edit_tmp.json test/raw/bp_edit2.txt
    cp test/build/bp_edit_tmp.json test/build/bp_edit_merge2.json
    {{DECODE}} test/build/bp_edit_tmp.json test/raw/bp_edit3.txt
    mv test/build/bp_edit_tmp.json test/build/bp_edit_merge3.json
