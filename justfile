DIFF_CMD 	 := "diff --brief --recursive --new-file"
RAW_DIR      := "test/raw"
EXPECTED_DIR := "test/expected"
BUILD_DIR    := "test/build"

FATUL  := "python3 fatul.py"
DECODE := FATUL + " decode -v"
ENCODE := FATUL + " encode -v"
DUMP   := FATUL + " dump -v"

# Run tests and compare results with expected results
test: clean run-tests
    @echo "Comparing built results with the expected ones..."
    {{DIFF_CMD}} "{{BUILD_DIR}}" "{{EXPECTED_DIR}}"
    @echo "all tests passed"

# Remove temporary build files
clean:
    rm -rf "{{BUILD_DIR}}"
    mkdir -p "{{BUILD_DIR}}"

# Regenerate expected tests results by running tests and moving them to the expected dir
rebuild-expected: clean run-tests
    rm -rf "{{EXPECTED_DIR}}"
    mkdir -p "{{EXPECTED_DIR}}"
    mv "{{BUILD_DIR}}"/* "{{EXPECTED_DIR}}/"

# Perform all tests, storing results in the build dir
run-tests:
    #!/usr/bin/env bash
    echo "Running tests..."
    echo "The 'Destination has a .json extension, ...' warning is expected"
    set -euxo pipefail

    {{DECODE}} {{BUILD_DIR}}/bp_power__decoded.json {{RAW_DIR}}/bp_power.txt
    {{DUMP}} -p {{BUILD_DIR}}/bp_power.json {{RAW_DIR}}/bp_power.txt
    {{DECODE}} -p --ids keep --sort none {{BUILD_DIR}}/bp_power__ids=keep.json {{RAW_DIR}}/bp_power.txt
    {{ENCODE}} {{BUILD_DIR}}/bp_power__ids=keep.json - | {{DUMP}} -p {{BUILD_DIR}}/bp_power__ids=keep__encoded.json -
    {{DECODE}} -p --ids refs --sort none {{BUILD_DIR}}/bp_power__ids=refs.json {{RAW_DIR}}/bp_power.txt
    {{ENCODE}} {{BUILD_DIR}}/bp_power__ids=refs.json - | {{DUMP}} -p {{BUILD_DIR}}/bp_power__ids=refs__encoded.json -
    {{DECODE}} -p --ids mixed --sort none {{BUILD_DIR}}/bp_power__ids=mixed.json {{RAW_DIR}}/bp_power.txt
    {{ENCODE}} {{BUILD_DIR}}/bp_power__ids=mixed.json - | {{DUMP}} -p {{BUILD_DIR}}/bp_power__ids=mixed__encoded.json -
    {{DECODE}} -p --ids keep --sort entities {{BUILD_DIR}}/bp_power__sort=entities.json {{RAW_DIR}}/bp_power.txt
    {{DECODE}} -p --ids keep --sort keys {{BUILD_DIR}}/bp_power__sort=keys.json {{RAW_DIR}}/bp_power.txt
    {{DECODE}} -p --ids keep --sort all {{BUILD_DIR}}/bp_power__sort=all.json {{RAW_DIR}}/bp_power.txt

    {{DECODE}} {{BUILD_DIR}}/bp_logic__decoded.json {{RAW_DIR}}/bp_logic.txt
    {{DUMP}} -p {{BUILD_DIR}}/bp_logic.json {{RAW_DIR}}/bp_logic.txt
    {{DECODE}} -p --ids keep --sort none {{BUILD_DIR}}/bp_logic__ids=keep.json {{RAW_DIR}}/bp_logic.txt
    {{ENCODE}} {{BUILD_DIR}}/bp_logic__ids=keep.json - | {{DUMP}} -p {{BUILD_DIR}}/bp_logic__ids=keep__encoded.json -
    {{DECODE}} -p --ids refs --sort none {{BUILD_DIR}}/bp_logic__ids=refs.json {{RAW_DIR}}/bp_logic.txt
    {{ENCODE}} {{BUILD_DIR}}/bp_logic__ids=refs.json - | {{DUMP}} -p {{BUILD_DIR}}/bp_logic__ids=refs__encoded.json -
    {{DECODE}} -p --ids mixed --sort none {{BUILD_DIR}}/bp_logic__ids=mixed.json {{RAW_DIR}}/bp_logic.txt
    {{ENCODE}} {{BUILD_DIR}}/bp_logic__ids=mixed.json - | {{DUMP}} -p {{BUILD_DIR}}/bp_logic__ids=mixed__encoded.json -
    {{DECODE}} -p --ids keep --sort entities {{BUILD_DIR}}/bp_logic__sort=entities.json {{RAW_DIR}}/bp_logic.txt
    {{DECODE}} -p --ids keep --sort keys {{BUILD_DIR}}/bp_logic__sort=keys.json {{RAW_DIR}}/bp_logic.txt
    {{DECODE}} -p --ids keep --sort all {{BUILD_DIR}}/bp_logic__sort=all.json {{RAW_DIR}}/bp_logic.txt

    {{DUMP}} -p {{BUILD_DIR}}/rm_empty    {{RAW_DIR}}/rm_empty.txt
    {{DUMP}} -p {{BUILD_DIR}}/bk_empty    {{RAW_DIR}}/bk_empty.txt
    {{DUMP}} -p {{BUILD_DIR}}/bk_empty_bp {{RAW_DIR}}/bk_empty_bp.txt
    {{DUMP}} -p {{BUILD_DIR}}/bk_nested   {{RAW_DIR}}/bk_nested.txt

    {{ENCODE}} {{BUILD_DIR}}/rm_empty.json - | {{DUMP}} -p {{BUILD_DIR}}/rm_empty2.json -
    {{ENCODE}} {{BUILD_DIR}}/bk_empty      - | {{DUMP}} -p {{BUILD_DIR}}/bk_empty.json -
    {{ENCODE}} {{BUILD_DIR}}/bk_empty_bp   - | {{DUMP}} -p {{BUILD_DIR}}/bk_empty_bp.json -
    {{ENCODE}} {{BUILD_DIR}}/bk_nested     - | {{DUMP}} -p {{BUILD_DIR}}/bk_nested.json -

    {{ENCODE}} {{BUILD_DIR}}/bk_nested/blueprint.json - | {{DUMP}} -p {{BUILD_DIR}}/bk_nested-bp.json -
    {{ENCODE}} {{BUILD_DIR}}/bk_nested/blueprint.json - | {{DECODE}} -p {{BUILD_DIR}}/bk_nested/blueprint.json -
