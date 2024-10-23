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
    set -euo pipefail

    echo "Running tests..."
    echo "The 'Destination has a .json extension, ...' warning is expected"

    echo "------------------------ Blueprints ------------------------"

    mkdir -p test/build/blueprints
    for file in test/raw/blueprints/*.txt; do
        base=$(basename "$file" .txt)
        echo "Testing $file ($base)"
        set -x
        {{DECODE}} "test/build/blueprints/${base}__decoded.json" "$file"
        {{DUMP}} -p "test/build/blueprints/${base}.json" "$file"
        {{ENCODE}} "test/build/blueprints/${base}__decoded.json" "test/build/blueprints/${base}__decoded_enc.txt"
        {{DUMP}} -p "test/build/blueprints/${base}__dec_enc_dec.json" "test/build/blueprints/${base}__decoded_enc.txt"
        {{DECODE}} -p --ids keep --sort none "test/build/blueprints/${base}__ids=keep.json" "$file"
        {{ENCODE}} "test/build/blueprints/${base}__ids=keep.json" "test/build/blueprints/${base}__ids=keep__encoded.txt"
        {{DECODE}} -p --ids refs --sort none "test/build/blueprints/${base}__ids=refs.json" "$file"
        {{ENCODE}} "test/build/blueprints/${base}__ids=refs.json" "test/build/blueprints/${base}__ids=refs__encoded.txt"
        {{DECODE}} -p --ids mixed --sort none "test/build/blueprints/${base}__ids=mixed.json" "$file"
        {{ENCODE}} "test/build/blueprints/${base}__ids=mixed.json" "test/build/blueprints/${base}__ids=mixed__encoded.txt"
        {{DECODE}} -p --ids keep --sort entities "test/build/blueprints/${base}__sort=entities.json" "$file"
        {{DECODE}} -p --ids keep --sort keys "test/build/blueprints/${base}__sort=keys.json" "$file"
        {{DECODE}} -p --ids keep --sort all "test/build/blueprints/${base}__sort=all.json" "$file"
        { set +x; } 2>/dev/null
    done

    echo "------------------------ Deconstruct ------------------------"

    mkdir -p test/build/deconstruct
    set -x
    {{DUMP}} -p test/build/deconstruct/empty       test/raw/deconstruct/empty.txt
    {{ENCODE}} test/build/deconstruct/empty.json    test/build/deconstruct/empty2.txt
    { set +x; } 2>/dev/null

    echo "------------------------ Books ------------------------"

    mkdir -p test/build/books
    set -x
    {{DUMP}} -p test/build/books/empty    test/raw/books/empty.txt
    {{DUMP}} -p test/build/books/empty_bp test/raw/books/empty_bp.txt
    {{DUMP}} -p test/build/books/nested   test/raw/books/nested.txt

    {{ENCODE}} test/build/books/empty      test/build/books/empty.txt
    {{ENCODE}} test/build/books/empty_bp   test/build/books/empty_bp.txt
    {{ENCODE}} test/build/books/nested     test/build/books/nested.txt

    {{ENCODE}} test/build/books/nested/blueprint.json test/build/books/nested-bp.txt
    {{ENCODE}} test/build/books/nested/blueprint.json - | {{DECODE}} -p test/build/books/nested/blueprint.json -
    { set +x; } 2>/dev/null

    echo "------------------------ Sequence ------------------------"

    mkdir -p test/build/sequence
    set -x
    {{DUMP}} test/build/sequence/edit1_dump.json test/raw/sequence/edit1.txt
    {{DUMP}} test/build/sequence/edit2_dump.json test/raw/sequence/edit2.txt
    {{DUMP}} test/build/sequence/edit3_dump.json test/raw/sequence/edit3.txt

    {{DECODE}} test/build/sequence/edit1.json test/raw/sequence/edit1.txt
    {{DECODE}} test/build/sequence/edit2.json test/raw/sequence/edit2.txt
    {{DECODE}} test/build/sequence/edit3.json test/raw/sequence/edit3.txt

    cp test/build/sequence/edit1.json test/build/sequence/edit_tmp.json
    {{DECODE}} test/build/sequence/edit_tmp.json test/raw/sequence/edit2.txt
    cp test/build/sequence/edit_tmp.json test/build/sequence/edit_merge2.json
    {{DECODE}} test/build/sequence/edit_tmp.json test/raw/sequence/edit3.txt
    mv test/build/sequence/edit_tmp.json test/build/sequence/edit_merge3.json
    { set +x; } 2>/dev/null
