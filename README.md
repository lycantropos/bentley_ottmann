bentley_ottmann
===============

[![](https://dev.azure.com/lycantropos/bentley_ottmann/_apis/build/status/lycantropos.bentley_ottmann?branchName=master)](https://dev.azure.com/lycantropos/bentley_ottmann/_build/latest?definitionId=20&branchName=master "Azure Pipelines")
[![](https://readthedocs.org/projects/bentley_ottmann/badge/?version=latest)](https://bentley-ottmann.readthedocs.io/en/latest "Documentation")
[![](https://codecov.io/gh/lycantropos/bentley_ottmann/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/bentley_ottmann "Codecov")
[![](https://img.shields.io/github/license/lycantropos/bentley_ottmann.svg)](https://github.com/lycantropos/bentley_ottmann/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/bentley-ottmann.svg)](https://badge.fury.io/py/bentley-ottmann "PyPI")

In what follows `python` is an alias for `python3.5` or `pypy3.5`
or any later version (`python3.6`, `pypy3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions
```bash
python -m pip install --upgrade pip setuptools
```

### User

Download and install the latest stable version from `PyPI` repository:
```bash
python -m pip install --upgrade bentley_ottmann
```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/bentley_ottmann.git
cd bentley_ottmann
```

Install dependencies
```bash
python -m pip install --force-reinstall -r requirements.txt
```

Install
```bash
python setup.py install
```

Usage
-----

With segments
```python
>>> from ground.base import get_context
>>> context = get_context()
>>> Point, Segment = context.point_cls, context.segment_cls
>>> unit_segments = [Segment(Point(0, 0), Point(1, 0)), 
...                  Segment(Point(0, 0), Point(0, 1))]

```
we can check if they intersect
```python
>>> from bentley_ottmann.planar import segments_intersect
>>> segments_intersect(unit_segments)
True

```
we can also find in which points segments intersect
```python
>>> from bentley_ottmann.planar import segments_intersections
>>> segments_intersections(unit_segments) == {Point(0, 0): {(0, 1)}}
True

```
here we can see that `0`th and `1`st segments intersect at point `(0, 0)`.

With contours
```python
>>> Contour = context.contour_cls
>>> triangle = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
>>> degenerate_triangle = Contour([Point(0, 0), Point(2, 0), Point(1, 0)])

```
we can check if they are self-intersecting or not
```python
>>> from bentley_ottmann.planar import edges_intersect
>>> edges_intersect(triangle)
False
>>> edges_intersect(degenerate_triangle)
True

```

Development
-----------

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version
```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version
```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version
```bash
bump2version --dry-run --verbose release
```

Bump version
```bash
bump2version --verbose release
```

This will set version to `major.minor.patch`.

### Running tests

Install dependencies
```bash
python -m pip install --force-reinstall -r requirements-tests.txt
```

Plain
```bash
pytest
```

Inside `Docker` container:
- with `CPython`
  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```
- with `PyPy`
  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

`Bash` script (e.g. can be used in `Git` hooks):
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

`PowerShell` script (e.g. can be used in `Git` hooks):
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
