# Miolingo Admin Dashboard Changelog

All notable changes to the Miolingo Admin Dashboard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2025-11-26

### Changed

- Version bump



## [1.6.0] - 2025-11-26

### Changed

- Version bump



## [1.6.0] - 2025-11-26

### Added

- Email monitoring feature with read-only IMAP access
- Email tab with recent messages display
- Unread email count
- Email connection test button
- Connection retry functionality in sidebar
- TTL (5 minutes) on cached database connections
- Better error handling for SSH tunnel timeouts
- Retry buttons in error messages

### Changed

- Swapped Email and Settings tabs (Email is now tab 4)
- Improved database connection management
- Added fresh connection helper function
- Better user feedback for connection issues

### Fixed

- SSH tunnel timeout causing persistent connection errors
- Database connection caching issues
- Error recovery workflow

## [1.5.1] - 2025-11-20

### Fixed

- Selective user logout functionality
- Session management improvements

## [1.5.0] - 2025-11-18

### Added

- Selective force logout for specific users
- Multi-select dropdown for user selection
- Enhanced session management controls

## [1.4.0] - 2025-11-15

### Added

- User activity statistics with 30-day chart
- Recent users display
- Expired sessions tracking

### Changed

- Improved Users tab layout
- Better metrics display

## [1.3.0] - 2025-11-10

### Added

- Clean up expired sessions button
- Force logout all users functionality
- Session expiration warnings

## [1.2.0] - 2025-11-05

### Added

- Resource usage monitoring
- TTS usage tracking
- Whisper model status

## [1.1.0] - 2025-11-01

### Added

- Basic user management
- Active sessions display
- Database connection status

## [1.0.0] - 2025-10-28

### Added

- Initial admin dashboard release
- Basic monitoring interface
- Settings and configuration tab
- Local log viewer
