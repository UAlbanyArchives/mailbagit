---
layout: page
title: Lossiness in Derivatives
permalink: /lossiness/
parent: Using mailbagit
nav_order: 5
---

# Lossiness in Derivatives

`mailbagit` is committed to maintaining as many of the meaningful characteristics of each email message across derivatives as feasible. However, practical limitations can cause some derivative formats to be lossy:

* Some derivative formats, such as PDFs, do not have the structure to appropriately store all parts of a message.
* In other cases, such as PSTs and MSGs, dependency libraries do not provide complete access to all the technical characteristics of a message.
	* `mailbagit` maintains what we feel are the meaningful characteristics of each message as defined by the `mailbagit` [email model](https://github.com/UAlbanyArchives/mailbag/blob/develop/mailbag/models.py).
	* Derivative EML or MBOX files created from PST or MSG source messages will contain all message headers, correctly encoded HTML and plain text bodies if present, and attachments.
	* The part structure of a message is not maintained.
* Generating EMLs from an MBOX or the reverse writes the full Python email message object if possible, so this should be lossless and contain the full part structure of a message.
	* For some MBOXs or EMLs with missing or inconsistently documented encoding, `mailbagit` tries to write the full message object. If it cannot, it writes a warning and falls back to writing derivatives from the [model](https://github.com/UAlbanyArchives/mailbag/blob/develop/mailbag/models.py).

Mailbag's approach to keep messages in multiple formats is designed to mitigate these issues by maintaining the original source format alongside all derivatives.

However, if this does not fit your use case, please let us know by [submitting an issue](https://github.com/UAlbanyArchives/mailbag/issues)!
