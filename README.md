# bentley_ottmann

[![Github Actions](https://github.com/lycantropos/bentley_ottmann/workflows/CI/badge.svg)](https://github.com/lycantropos/bentley_ottmann/actions/workflows/ci.yml "Github Actions")
[![Codecov](https://codecov.io/gh/lycantropos/bentley_ottmann/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/bentley_ottmann "Codecov")
[![Documentation](https://readthedocs.org/projects/bentley_ottmann/badge/?version=latest)](https://bentley-ottmann.readthedocs.io/en/latest "Documentation")
[![License](https://img.shields.io/github/license/lycantropos/bentley_ottmann.svg)](https://github.com/lycantropos/bentley_ottmann/blob/master/LICENSE "License")
[![PyPI](https://badge.fury.io/py/bentley-ottmann.svg)](https://badge.fury.io/py/bentley-ottmann "PyPI")

In what follows `python` is an alias for `python3.10` or `pypy3.10`
or any later version (`python3.11`, `pypy3.11` and so on).

## Installation

### Prerequisites

Install the latest `pip` & `setuptools` packages versions

```bash
python -m pip install --upgrade pip setuptools
```

### User

Download and install the latest stable version from `PyPI` repository

```bash
python -m pip install --upgrade bentley_ottmann
```

### Developer

Download the latest version from `GitHub` repository

```bash
git clone https://github.com/lycantropos/bentley_ottmann.git
cd bentley_ottmann
```

Install

```bash
python -m pip install -e '.'
```

## Usage

With segments

```python
>>> import math
>>> from fractions import Fraction
>>> from ground.context import Context
>>> context = Context(coordinate_factory=Fraction, sqrt=math.sqrt)
>>> Point, Segment = context.point_cls, context.segment_cls
>>> unit_segments = [
...     Segment(Point(0, 0), Point(1, 0)),
...     Segment(Point(0, 0), Point(0, 1))
... ]

```

we can check if they intersect

```python
>>> from bentley_ottmann.planar import segments_intersect
>>> segments_intersect(unit_segments, context=context)
True

```

With contours

```python
>>> Contour = context.contour_cls
>>> triangle = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
>>> degenerate_triangle = Contour([Point(0, 0), Point(2, 0), Point(1, 0)])

```

we can check if they are self-intersecting or not

```python
>>> from bentley_ottmann.planar import contour_self_intersects
>>> contour_self_intersects(triangle, context=context)
False
>>> contour_self_intersects(degenerate_triangle, context=context)
True

```

## Development

### Bumping version

#### Prerequisites

Install [bump-my-version](https://github.com/callowayproject/bump-my-version#installation).

#### Release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version

```bash
bump-my-version bump --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version

```bash
bump-my-version bump --verbose $CATEGORY
```

This will set version to `major.minor.patch`.

### Running tests

#### Plain

Install with dependencies

```bash
python -m pip install -e '.[tests]'
```

Run

```bash
pytest
```

#### `Docker` container

Run

- with `CPython`

  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```

- with `PyPy`

  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

#### `Bash` script

Run

- with `CPython`

  ```bash
  ./run-tests.sh
  ```

  or

  ```bash
  ./run-tests.sh cpython
  ```

- with `PyPy`

  ```bash
  ./run-tests.sh pypy
  ```

#### `PowerShell` script

Run

- with `CPython`

  ```powershell
  .\run-tests.ps1
  ```

  or

  ```powershell
  .\run-tests.ps1 cpython
  ```

- with `PyPy`

  ```powershell
  .\run-tests.ps1 pypy
  ```
