---
layout: page
title: Plugins
permalink: /plugins/
parent: Using mailbagit
nav_order: 4
---

# Plugins

You can make plugins for both the mailbagit format parsers and derivatives classes. This allows you to easily override the behaviour for how mailbagit reads email exports or creates derivative formats. New input and derivative formats may also be provided to mailbagit to extend its functionality.

The files that can be overridden can be found in the [Github repo](https://github.com/UAlbanyArchives/mailbag) in the [mailbag/formats](https://github.com/UAlbanyArchives/mailbag/tree/main/mailbag/formats) and [mailbag/derivatives](https://github.com/UAlbanyArchives/mailbag/tree/main/mailbag/derivatives) subdirectories.

By default, mailbagit will look for formats in the following places:

1. a `formats` or `derivatives` subdirectory within a directory specified in the `MAILBAG_PLUGIN_DIR` environment variable.
	
	Unix Example:
	```
		mkdir ~/myplugindir
		mkdir ~/myplugindir/formats
		touch ~/myplugindir/formats/pst.py
		export MAILBAG_PLUGIN_DIR=$HOME/myplugindir
	```
2. `.mailbag/formats` and `.mailbag/derivatives` subdirectories in the user's home directory.
	
	Unix Example:
	```
		mkdir ~/.mailbag/derivatives
		touch ~/.mailbag/derivatives/pdf.py
	```

	Example Windows path:
	```
	C:\Users\[my_username]\.mailbag\formats\imap.py
	```
3. The formats and derivatives built into mailbag.
