# Gaphor on macOS

The latest release of Gaphor can be downloaded from the [Gaphor download page](https://gaphor.org/download.html#macos).

Older releases are available from [GitHub](https://github.com/gaphor/gaphor/releases).

[CI builds](https://github.com/gaphor/gaphor/actions/workflows/full-build.yml) are also available.


## Development Environment

To setup a development environment with macOS:
1. Install [homebrew](https://brew.sh)
1. Open a terminal and execute:
```bash
$ brew install python3 gobject-introspection gtk+3 gtksourceview4 adwaita-icon-theme gtk-mac-integration
```
Install Poetry (you may want to consider installing poetry via [pipx](https://pypi.org/project/pipx/), instead of pip):
```bash
pip install --user poetry
```
[Clone the
repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository).
```
$ cd gaphor
$ poetry config virtualenvs.in-project true
$ poetry install
$ poetry run gaphor
```

## Packaging for macOS

In order to create an exe installation package for macOS, we utilize
[PyInstaller](https://pyinstaller.org) which analyzes Gaphor to find all the
dependencies and bundle them in to a single folder.

1. Follow the instructions for settings up a development environment above
1. Open a terminal and execute the following from the repository directory:
```bash
$ poetry run poe package
```
