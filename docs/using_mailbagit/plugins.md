---
layout: page
title: Plugins
permalink: /plugins/
parent: Using mailbagit
nav_order: 5
---

# Plugins

You can make plugins for both the mailbagit format parsers and derivatives classes. This allows you to easily override the behavior for how mailbagit reads email exports or creates derivative formats. New input and derivative formats may also be provided to mailbagit to extend its functionality.

The files that can be overridden can be found in the [Github repo](https://github.com/UAlbanyArchives/mailbagit) in the [mailbagit/formats](https://github.com/UAlbanyArchives/mailbagit/tree/main/mailbagit/formats) and [mailbagit/derivatives](https://github.com/UAlbanyArchives/mailbagit/tree/main/mailbagit/derivatives) subdirectories.

By default, mailbagit will look for formats in the following places:

1. a `formats` or `derivatives` subdirectory within a directory specified in the `MAILBAG_PLUGIN_DIR` environment variable.
	
	Unix Example:
	```
		mkdir ~/myplugindir
		mkdir ~/myplugindir/formats
		touch ~/myplugindir/formats/pst.py
		export MAILBAGIT_PLUGIN_DIR=$HOME/myplugindir
	```
2. `.mailbagit/formats` and `.mailbagit/derivatives` subdirectories in the user's home directory.
	
	Unix Example:
	```
		mkdir ~/.mailbagit/derivatives
		touch ~/.mailbagit/derivatives/pdf.py
	```

	Example Windows path:
	```
	C:\Users\[my_username]\.mailbagit\formats\imap.py
	```
3. The formats and derivatives built into mailbagit.
