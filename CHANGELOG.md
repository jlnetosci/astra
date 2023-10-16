# Changelog

## [Unreleased]

### To be Added
- Generate moving-threshold elasticgraph.
- Generate tree of descendants from root.
- Generate 3D network charts. ([#4](https://github.com/jlnetosci/astra/issues/4))

### To be Changed
- Change network physics for large numbers of individuals.([#2](https://github.com/jlnetosci/astra/issues/2)) 

### To be Fixed
- Log button pushes.

## [0.1.2b] - 2023-10-15

### Added
- Processing data loader.

### Changed
- Example file link changed from RomanGods.ged to TolkienFamily.ged for simplicity and speed.

### Fixed
- Bug in absence of root individual selection. ([#1](https://github.com/jlnetosci/astra/issues/1)) 
- First individual is identified regardless of leading zeros in ID.
- Problems in GEDCOM formatting for parser raises clearer error message, and guides toward solution. ([#3](https://github.com/jlnetosci/astra/issues/3)) 
- Duplicate IDs in file are searched for and error is raised if any are found.
- Unexpected end of files is fixed by adding newline to the data read.

## [0.1.1b] - 2023-10-11

### Fixed
- Non-UTF-8 load error correction. 

## [0.1.0b] - 2023-10-08

### Added
- Initial release

