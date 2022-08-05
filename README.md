# Lifelike fix modified_date

[![PyPI - Version](https://img.shields.io/pypi/v/lifelike-fix-modified-date.svg)](https://pypi.org/SBRG/lifelike-fix-modified-date)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lifelike-fix-modified-date.svg)](https://pypi.org/SBRG/lifelike-fix-modified-date)

Fixes modified_date columns in PostgreSQL database by copying the original value from a backup instance.
Useful when Alembic data migration unexpectedly changes the modified_date column.

---

**Table of Contents**

- [Lifelike fix modified_date](#lifelike-fix-modified_date)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Examples](#examples)
    - [Get `date_modified` field statistics](#get-date_modified-field-statistics)
    - [Fix `modified_date` column](#fix-modified_date-column)
  - [License](#license)

## Installation

```console
pip install lifelike-fix-modified-date
```

Or from source:

```console
pip install git+https://github.com/SBRG/lifelike-fix-modified-date.git
```

## Usage

```console
$ lifelike-fix-modified-date --help

lifelike-fix-modified-date

Fixes all modified_date columns in a database to match the values in a backup database.
This is useful when a database migration updates modified_date column in a table unintentionally.

Usage:
  lifelike-fix-modified-date (-h | --help | --version)
  lifelike-fix-modified-date stats --database=<uri>
  lifelike-fix-modified-date fix <bad_modified_date> --database=<uri> --backup-database=<uri>
                                                     [--table=<table>] [--ignore-count-mismatch]

Generic options:
  -h --help                 Show this screen.
  --version                 Show version.
  --database=<uri>          Postgres URI of the target database.

Fix options:
  --backup-database=<uri>   Postgres URI of the backup (source) database.
  --table=<table>           Table name to fix. [default: files]
  --ignore-coount-mismatch  Ignore row count mismatch between backup source and target databases
                            (e.g. if there are deleted rows since the backup was taken).

Examples:
  lifelike-fix-modified-date stats --database=postgres://user:pass@localhost:5432/db
  lifelike-fix-modified-date fix "2022-08-03 18:21:49.498104" --database=postgres://user:pass@host:5432/db --backup-database=postgres://user:pass@backup-host:5432/db
```

---

## Examples

### Get `date_modified` field statistics

Get modified_date column stats for all tables

```console
$ python -m lifelike_fix_modified_date stats --database postgresql://user:pass@host:port/db
```

### Fix `modified_date` column

Fix the modified_date column in the `files` table to match the backup database.

```console
$ python -m lifelike_fix_modified_date \
    fix "2022-08-03 18:21:49.498104" --table files \
    --database postgresql://user:pass@database-host:port/db \
    --backup-database postgresql://user:pass@backup-host:port/db
```

## License

`lifelike-fix-modified-date` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
