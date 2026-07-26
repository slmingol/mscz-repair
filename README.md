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
curl -o mscz_repair https://raw.githubusercontent.com/slmingol/mscz-repair/main/mscz_repair.py && chmod +x mscz_repair
./mscz_repair <file>.mscz
```

## Usage

**If installed via pip** (`mscz-repair`):

```sh
mscz-repair broken.mscz                  # writes broken_fixed.mscz alongside the original
mscz-repair broken.mscz -o repaired.mscz # custom output path
mscz-repair broken.mscz --in-place       # overwrite in place
```

**If run directly** (`./mscz_repair`): same flags, just substitute `./mscz_repair` for `mscz-repair`.

## Example (direct download)

```
# start with just the broken file
$ ls -l
total 6124
-rw-r--r-- 1 user staff 6270602 Jul 26 19:01 'symphony_no5_corrupt.mscz'

# download and make executable
$ curl https://raw.githubusercontent.com/slmingol/mscz-repair/main/mscz_repair.py -o mscz_repair && chmod +x mscz_repair
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                   Dload  Upload   Total   Spent    Left  Speed
100  4234  100  4234    0     0  47802      0 --:--:-- --:--:-- --:--:-- 48113

# fix the corrupted file
$ ./mscz_repair symphony_no5_corrupt.mscz
Removed 128 stale excerpt entries.
Written: symphony_no5_corrupt_fixed.mscz

# both files present alongside the script
$ ls -l
total 8020
-rw-r--r-- 1 user staff 1932322 Jul 26 19:06 'symphony_no5_corrupt_fixed.mscz'
-rw-r--r-- 1 user staff 6270602 Jul 26 19:01 'symphony_no5_corrupt.mscz'
-rwxr-xr-x 1 user staff    4234 Jul 26 19:04  mscz_repair
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
