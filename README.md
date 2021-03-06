# Factorio Blueprint GIT Tool (FaTul)

Treat Factorio blueprints for what they really are -- software programs: version control, git stored, and CI-tested. This tool makes it possible, and keeps version diffs easy to read.

* Work directly with clipboard - FaTul can use copied strings or place new strings into clipboard.
* Minimize text changes between blueprint versions
  * Uses human-readable but compact JSON format
  * Sort entities by their x,y coordinates
  * Do not store `entity_number` (IDs) in the text files
  * Use relative entity position instead of `entity_id`
  * Minimize entity position changes between blueprint versions by attempting to detect entity x,y changes, and storing a global x,y shift instead of changing individual entity positions.
* Stores blueprint books as directories
* Edit individual blueprint even if it is part of a book. Decoding to the same location will restore the book index from the prior version.

Copy `fatul.py` to your project and run `pip3 install pyperclip` if clipboard is needed for easiest usage. See [usage](#usage) below.

## Why?
A [commit](https://github.com/bcwhite-code/brians-blueprints/commit/4f4e5c6cdd2218bc0978be2885eb4884ee0f0d02) to [brians-blueprints](https://github.com/bcwhite-code/brians-blueprints) has 23 changed files with 736,839 insertions and 119,118 deletions.

One of the modified files, `basic science.json`, had 25,875 additions, 25,843 deletions.  FaTul makes that 17 insertions, 13 deletions.  That's 1,724 **times** smaller, and can be read by a human!

## How?
Factorio JSON is not good to store in GIT because the entity IDs and their order can change on every export, creating a lot of useless text changes.  Every entity in a blueprint has an x,y position, so FaTul can create a relative link to the entity:

* Entity 1 is at `{x: 2, y: 5}`
* Entity 2 is at `{x: 3, y: -1}`
* If entity 2 references entity 1, the relative link from 2 to 1 would be `-1,6` (`2-3, 5-(-1)`). FaTul will replace all `"entity_id": 1` inside entity 2 with `"entity_rel": "-1,6"`.
* The same value is used for the `neighbours` field (an array of entity IDs)
* If anything else uses a list of entity IDs (rather than `entity_id` field), please create an issue.

When saving a new blueprint, entities positions are normalized by shifting them to near-zero values, and storing a global x,y shift. When the blueprint is updated, FaTul attempts to match the old blueprint to the new one, and shift the entities of the new version to match the old one. This way the x,y position of most entities will remain intact between revisions, and only the blueprint main shift values might change.

Sorting is another reason for large diffs. Factorio could order entities in any order on every export, so to minimize that, FaTul re-sorts entities by their names following by the x,y position using [Z-order curve](https://en.wikipedia.org/wiki/Z-order_curve). This way entities that are close together on a blueprint are more likely to stay together in a list.

## Installation

#### Simple Installation
The simple method is to download `fatul.py` into your project and optionally run `pip3 install pyperclip` for clipboard support.

#### Advanced Installation

Alternatively, you can clone the repository to get some additional shortcuts and an easier way to update the code.

```bash
# Clone/download tools
git clone https://github.com/nyurik/fatul.git
cd fatul

# [Optional] It is usually a good idea to use Python virtualenv.
# If created, make sure to activate it before using fatul.py
virtualenv -p python3 venv
activate venv/bin/activate

# [Optional] Install pyperclip for clipboard support
# If not installed, you can still encode/decode files
pip3 install pyperclip
```

## Usage

```bash
# Convert a factorio string in clipboard to a file my_data.json,
# or if it's a blueprint, directory my_data/.
python3 fatul.py decode my_data
# same, but decode clipboard to console
python3 fatul.py decode -

# Same as `decode`, but does not make any changes to JSON
python3 fatul.py dump -

# Convert a file (or dir) to a Factorio string and copy to clipboard.
python3 fatul.py encode my_data.json

# See help for more commands
python3 fatul.py --help
python3 fatul.py decode --help
```

The repository also contains a few shortcut scripts: `decode`, `encode`, and `dump`:

```bash
# this short command
./decode my_data
# is identical to the full command
python3 fatul.py decode my_data
```

## Upgrading between versions
* Use the old version of fatul to convert a file/dir to a string
* Use the new version of fatul to convert a string back to a file/dir

## Development

Install [just](https://github.com/casey/just#installation).  Run `just` to run all sample tests and compares the output with the files in the `test/expected` dir.  To update expected results, run `just rebuild-expected`.
