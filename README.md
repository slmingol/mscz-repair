<p align="center">
  <img src="banner.svg" alt="mscz-repair" width="100%" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-4584b6?style=flat-square&logo=python&logoColor=white" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/MuseScore-4.x-7059aa?style=flat-square" alt="MuseScore 4.x" />
  <img src="https://img.shields.io/badge/dependencies-zero-3fb950?style=flat-square" alt="Zero dependencies" />
  <img src="https://img.shields.io/badge/license-MIT-22c55e?style=flat-square" alt="MIT License" />
</p>

<br />

A single-file CLI that fixes `.mscz` files crashing on load with MuseScore's `setTrack ASSERT FAILED` — the result of stale part excerpts that no longer match the main score's structure.

## The problem

When a score's time signatures or measure layout changes after parts are generated, the excerpt files diverge from the main score's tick map. On load, MuseScore tries to reconnect excerpt elements by tick position, hits a mismatch, and aborts:

```
Score::tick2segment   | no measure for tick 123360
EngravingItem::setTrack | ASSERT FAILED:
    val < m_score->ntracks() || val == 0 || ...
```

The fix is to strip the stale excerpts so MuseScore loads the score clean, then regenerate fresh ones.

## Install

**From GitHub (installs the `mscz-repair` command globally):**

```sh
pip install git+https://github.com/slmingol/mscz-repair.git
```

**Or run directly without installing:**

```sh
curl -O https://raw.githubusercontent.com/slmingol/mscz-repair/main/mscz_repair.py
python3 mscz_repair.py <file>.mscz
```

## Usage

```sh
# Writes <name>_fixed.mscz alongside the original
mscz-repair broken.mscz

# Custom output path
mscz-repair broken.mscz -o repaired.mscz

# Overwrite in place
mscz-repair broken.mscz --in-place
```

```
usage: mscz-repair [-h] [-o OUTPUT] [-i] input

positional arguments:
  input                 path to the broken .mscz file

options:
  -o, --output OUTPUT   output path (default: <input>_fixed.mscz)
  -i, --in-place        overwrite the input file instead of writing a new one
```

## How it works

A `.mscz` file is a zip archive. Inside, `META-INF/container.xml` lists every file MuseScore should load — including `Excerpts/` part files. `mscz-repair`:

1. Unpacks the archive to a temp directory.
2. Removes all `<rootfile full-path="Excerpts/..."/>` entries from `container.xml`.
3. Repacks the archive without the `Excerpts/` directory.

The main score data is never touched.

## After repair

1. Open the repaired file in MuseScore — it should load without crashing.
2. Regenerate parts: **Parts** panel in the left sidebar.
3. Save (`Cmd+S` / `Ctrl+S`) — MuseScore rewrites the archive with fresh, correctly-linked excerpts.

## License

MIT
