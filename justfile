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

# Legacy compatibility
alias rebuild-expected := bless

# Regenerate expected tests results by running tests and moving them to the expected dir
bless: clean run-tests
    rm -rf "{{EXPECTED_DIR}}"
    mkdir -p "{{EXPECTED_DIR}}"
    mv "test/build"/* "{{EXPECTED_DIR}}/"

# Perform all tests, storing results in the build dir
run-tests:
    #!/usr/bin/env bash
    echo "Running tests..."
    echo "The 'Destination has a .json extension, ...' warning is expected"
    set -euxo pipefail

    mkdir -p test/build/blueprints
    mkdir -p test/build/books
    mkdir -p test/build/deconstruct

    {{DECODE}} test/build/blueprints/power__decoded.json test/raw/blueprints/power.txt
    {{DUMP}} -p test/build/blueprints/power.json test/raw/blueprints/power.txt
    {{ENCODE}} test/build/blueprints/power__decoded.json test/build/blueprints/power__decoded_enc.txt
    {{DUMP}} -p test/build/blueprints/power__dec_enc_dec.json test/build/blueprints/power__decoded_enc.txt
    {{DECODE}} -p --ids keep --sort none test/build/blueprints/power__ids=keep.json test/raw/blueprints/power.txt
    {{ENCODE}} test/build/blueprints/power__ids=keep.json test/build/blueprints/power__ids=keep__encoded.txt
    {{DECODE}} -p --ids refs --sort none test/build/blueprints/power__ids=refs.json test/raw/blueprints/power.txt
    {{ENCODE}} test/build/blueprints/power__ids=refs.json test/build/blueprints/power__ids=refs__encoded.txt
    {{DECODE}} -p --ids mixed --sort none test/build/blueprints/power__ids=mixed.json test/raw/blueprints/power.txt
    {{ENCODE}} test/build/blueprints/power__ids=mixed.json test/build/blueprints/power__ids=mixed__encoded.txt
    {{DECODE}} -p --ids keep --sort entities test/build/blueprints/power__sort=entities.json test/raw/blueprints/power.txt
    {{DECODE}} -p --ids keep --sort keys test/build/blueprints/power__sort=keys.json test/raw/blueprints/power.txt
    {{DECODE}} -p --ids keep --sort all test/build/blueprints/power__sort=all.json test/raw/blueprints/power.txt

    {{DECODE}} test/build/blueprints/logic__decoded.json test/raw/blueprints/logic.txt
    {{DUMP}} -p test/build/blueprints/logic.json test/raw/blueprints/logic.txt
    {{ENCODE}} test/build/blueprints/logic__decoded.json test/build/blueprints/logic__decoded_enc.txt
    {{DUMP}} -p test/build/blueprints/logic__dec_enc_dec.json test/build/blueprints/logic__decoded_enc.txt
    {{DECODE}} -p --ids keep --sort none test/build/blueprints/logic__ids=keep.json test/raw/blueprints/logic.txt
    {{ENCODE}} test/build/blueprints/logic__ids=keep.json test/build/blueprints/logic__ids=keep__encoded.txt
    {{DECODE}} -p --ids refs --sort none test/build/blueprints/logic__ids=refs.json test/raw/blueprints/logic.txt
    {{ENCODE}} test/build/blueprints/logic__ids=refs.json test/build/blueprints/logic__ids=refs__encoded.txt
    {{DECODE}} -p --ids mixed --sort none test/build/blueprints/logic__ids=mixed.json test/raw/blueprints/logic.txt
    {{ENCODE}} test/build/blueprints/logic__ids=mixed.json test/build/blueprints/logic__ids=mixed__encoded.txt
    {{DECODE}} -p --ids keep --sort entities test/build/blueprints/logic__sort=entities.json test/raw/blueprints/logic.txt
    {{DECODE}} -p --ids keep --sort keys test/build/blueprints/logic__sort=keys.json test/raw/blueprints/logic.txt
    {{DECODE}} -p --ids keep --sort all test/build/blueprints/logic__sort=all.json test/raw/blueprints/logic.txt

    {{DECODE}} test/build/blueprints/schedule__decoded.json test/raw/blueprints/schedule.txt
    {{DUMP}} -p test/build/blueprints/schedule.json test/raw/blueprints/schedule.txt
    {{ENCODE}} test/build/blueprints/schedule__decoded.json test/build/blueprints/schedule__decoded_enc.txt
    {{DUMP}} -p test/build/blueprints/schedule__dec_enc_dec.json test/build/blueprints/schedule__decoded_enc.txt
    {{DECODE}} -p --ids keep --sort none test/build/blueprints/schedule__ids=keep.json test/raw/blueprints/schedule.txt
    {{ENCODE}} test/build/blueprints/schedule__ids=keep.json test/build/blueprints/schedule__ids=keep__encoded.txt
    {{DECODE}} -p --ids refs --sort none test/build/blueprints/schedule__ids=refs.json test/raw/blueprints/schedule.txt
    {{ENCODE}} test/build/blueprints/schedule__ids=refs.json test/build/blueprints/schedule__ids=refs__encoded.txt
    {{DECODE}} -p --ids mixed --sort none test/build/blueprints/schedule__ids=mixed.json test/raw/blueprints/schedule.txt
    {{ENCODE}} test/build/blueprints/schedule__ids=mixed.json test/build/blueprints/schedule__ids=mixed__encoded.txt
    {{DECODE}} -p --ids keep --sort entities test/build/blueprints/schedule__sort=entities.json test/raw/blueprints/schedule.txt
    {{DECODE}} -p --ids keep --sort keys test/build/blueprints/schedule__sort=keys.json test/raw/blueprints/schedule.txt
    {{DECODE}} -p --ids keep --sort all test/build/blueprints/schedule__sort=all.json test/raw/blueprints/schedule.txt

    {{DECODE}} test/build/blueprints/dup__decoded.json test/raw/blueprints/dup.txt
    {{DUMP}} -p test/build/blueprints/dup.json test/raw/blueprints/dup.txt
    {{ENCODE}} test/build/blueprints/dup__decoded.json test/build/blueprints/dup__decoded_enc.txt
    {{DUMP}} -p test/build/blueprints/dup__dec_enc_dec.json test/build/blueprints/dup__decoded_enc.txt
    {{DECODE}} -p --ids keep --sort none test/build/blueprints/dup__ids=keep.json test/raw/blueprints/dup.txt
    {{ENCODE}} test/build/blueprints/dup__ids=keep.json test/build/blueprints/dup__ids=keep__encoded.txt
    {{DECODE}} -p --ids refs --sort none test/build/blueprints/dup__ids=refs.json test/raw/blueprints/dup.txt
    {{ENCODE}} test/build/blueprints/dup__ids=refs.json test/build/blueprints/dup__ids=refs__encoded.txt
    {{DECODE}} -p --ids mixed --sort none test/build/blueprints/dup__ids=mixed.json test/raw/blueprints/dup.txt
    {{ENCODE}} test/build/blueprints/dup__ids=mixed.json test/build/blueprints/dup__ids=mixed__encoded.txt
    {{DECODE}} -p --ids keep --sort entities test/build/blueprints/dup__sort=entities.json test/raw/blueprints/dup.txt
    {{DECODE}} -p --ids keep --sort keys test/build/blueprints/dup__sort=keys.json test/raw/blueprints/dup.txt
    {{DECODE}} -p --ids keep --sort all test/build/blueprints/dup__sort=all.json test/raw/blueprints/dup.txt

    {{DUMP}} -p test/build/deconstruct/empty       test/raw/deconstruct/empty.txt
    {{ENCODE}} test/build/deconstruct/empty.json    test/build/deconstruct/empty2.txt

    {{DUMP}} -p test/build/books/empty    test/raw/books/empty.txt
    {{DUMP}} -p test/build/books/empty_bp test/raw/books/empty_bp.txt
    {{DUMP}} -p test/build/books/nested   test/raw/books/nested.txt

    {{ENCODE}} test/build/books/empty      test/build/books/empty.txt
    {{ENCODE}} test/build/books/empty_bp   test/build/books/empty_bp.txt
    {{ENCODE}} test/build/books/nested     test/build/books/nested.txt

    {{ENCODE}} test/build/books/nested/blueprint.json test/build/books/nested-bp.txt
    {{ENCODE}} test/build/books/nested/blueprint.json - | {{DECODE}} -p test/build/books/nested/blueprint.json -

    {{DUMP}} test/build/blueprints/edit1_dump.json test/raw/blueprints/edit1.txt
    {{DUMP}} test/build/blueprints/edit2_dump.json test/raw/blueprints/edit2.txt
    {{DUMP}} test/build/blueprints/edit3_dump.json test/raw/blueprints/edit3.txt

    {{DECODE}} test/build/blueprints/edit1.json test/raw/blueprints/edit1.txt
    {{DECODE}} test/build/blueprints/edit2.json test/raw/blueprints/edit2.txt
    {{DECODE}} test/build/blueprints/edit3.json test/raw/blueprints/edit3.txt
    cp test/build/blueprints/edit1.json test/build/blueprints/edit_tmp.json
    {{DECODE}} test/build/blueprints/edit_tmp.json test/raw/blueprints/edit2.txt
    cp test/build/blueprints/edit_tmp.json test/build/blueprints/edit_merge2.json
    {{DECODE}} test/build/blueprints/edit_tmp.json test/raw/blueprints/edit3.txt
    mv test/build/blueprints/edit_tmp.json test/build/blueprints/edit_merge3.json
