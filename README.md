# mailbag
A tool for creating and managing Mailbags, a package for preserving email with multiple masters

## Plugins

New formats (and eventually, other components) may be provided to mailbag to extend its functionality.  By default, mailbag will look for formats in the following places:

1. formats built into mailbag
2. a `.mailbag/formats` subdirectory in the user's home directory.
3. a `formats` subdirectory within a directory specified in the `MAILBAG_PLUGIN_DIR` environment variable.
