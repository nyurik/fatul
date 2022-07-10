# Factorio Blueprint GIT Tools

Time to treat Factorio blueprints for what they really are -- software programs. And as such, they deserve to be version controlled, stored in git, and tested with CI, without making version diffs difficult to read.

* Work directly with clipboard - no need to `CTRL+C` and `CTRL+V`
* Minimize text changes between blueprint versions
  * Uses human-readable but compact JSON format
  * Sort entities by their x,y coordinates
  * Do not store `entity_number` (IDs) in the text files
  * Use relative entity position instead of `entity_id`
* Stores blueprint books as directories

## Why?
A [commit](https://github.com/bcwhite-code/brians-blueprints/commit/4f4e5c6cdd2218bc0978be2885eb4884ee0f0d02) to [brians-blueprints](https://github.com/bcwhite-code/brians-blueprints) has 23 changed files with 736,839 insertions and 119,118 deletions.

One of the modified files, `basic science.json`, had 25,875 additions, 25,843 deletions.  Fatul makes that 17 insertions, 13 deletions.  That's 1,724 **times** smaller, and can be read by a human!

## Installation

```bash
# Clone/download tools
git clone https://github.com/nyurik/fatul.git
cd fatul

# [Optional] It is usually a good idea to use Python virtualenv
virtualenv -p python3 venv
activate venv/bin/activate

# [Optional] Install pyperclip for clipboard support
# If not installed, you can still encode/decode files
pip3 install -r requirements.txt
```

## Usage

```bash
# [Optional] Activate the virtualenv if you created one
activate venv/bin/activate

# Decode clipboard to a file/directory
./decode my_blueprint

# Same, but without the helper script
python3 fatul.py decode my_blueprint

# Decode clipboard to console
./decode -

# Decode a file to another file
./decode output.json encoded_string.txt

# Encode a file/directory to clipboard
./encode my_blueprint

# Encode a file/directory to a file
./encode my_blueprint output.txt

# See help for more commands
python3 fatul.py --help
python3 fatul.py decode --help
```

## Development

Run `make test` in the `test/` dir to run all sample tests and compares the output with the files in the `expected/` dir.  To update expected results, run `make rebuild-expected`.
