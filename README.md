# Factorio Blueprint GIT Tools

Time to treat Factorio blueprints for what they really are -- software programs. And as such, they deserve to be version controlled, stored in git, and tested with CI, without making version diffs difficult to read.

* Work directly with clipboard - no need to `CTRL+C` and `CTRL+V`
* Minimize text changes between blueprint versions
  * Uses human readable but compact JSON format
  * Sort entities by their x,y coordinates
  * Do not store `entity_number` (IDs) in the text files
  * Use relative entity position instead of `entity_id`
* Stores blueprint books as directories

## Installation

```bash
# Clone/download tools
git clone https://github.com/nyurik/fatul.git
cd factorio-tools

# With Python, it is usually a good idea to use Python virtualenv,
# but it will work without it too.
virtualenv -p python3 venv
activate venv/bin/activate

# Install a few simple dependencies
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

# Encode a file/directory to clipboard
./encode my_blueprint

# See help for more commands
python3 fatul.py --help
python3 fatul.py decode --help
```

## Development

Run `make test` in the `test/` dir to run all sample tests and compares the output with the files in the `expected/` dir.  To update expected results, run `make rebuild-expected`.
