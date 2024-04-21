# Changelog

## [Unreleased]

### To be Added
- Save image files directly.

## [0.2.0b] - 2024-04-21

### Added
- Generate 3D network charts. ([#4](https://github.com/jlnetosci/astra/issues/4)).
- Second example file: ASOIAF.ged. 
- Selection of several color palettes (Classic, Pastel, Nightly, Grayscale, Colorblind-friendly (Tol light)).
- Choice of highlighting one individual besides root.
- Frequently asked questions section.
- Contact form.
- Social media links.

### Changed
- App redesigned (logo, colors, etc).
- Instructions moved to their own section and divided between quickstart and in-depth.
- Selection of root individual and ancestors is now optional.
- Change network physics and relative initial positions in 2D network generation.([#2](https://github.com/jlnetosci/astra/issues/2)) 

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

