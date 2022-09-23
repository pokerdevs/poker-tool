# poker-tool

## Running the `poker-tool`

### Install Python 3
Make sure you have [Python3 installed](https://www.python.org/downloads/). You should be able to open up a terminal (or Command Prompt) and run the following:

```
python --version
```
- Ensure that it shows that Python 3.8 or later has been installed.

### Download and run the .pyz

Download the `.pyz` from the [release page](https://github.com/pokerdevs/poker-tool/releases/latest)

From the terminal or command prompt, run the following command:

```
python PATH-TO-THE-PYZ-FILE --version
```
- Ensure that it says "Pokertool version X.Y.Z"

## Available tools

### monker-to-pio

This tool will convert MonkerSolver `.rng` ranges into a format usable by PioSolver.

```
usage: poker-tool.pyz monker-to-pio [-h] -i INPUT_PATH -o OUTPUT_PATH [-f]
```

For example:
```
python c:\poker-tool.pyz --monker-to-pio -i c:\temp\monker-ranges\ -o c:\temp\pio-ranges
```

## Development

### Push a new version

After commits, make sure to tag a new version

```
git tag vX.Y.Z
git push origin master vX.Y.Z
```

### Create a release

```
RELEASE_TAG=$(git describe --tags)
python -m zipapp ./ -m "scripts.pokerdevs.poker_tool.poker_tool:main" -o poker-tool-${RELEASE_TAG}.pyz
```
