---
layout: page
title: Lossiness in Derivatives
permalink: /lossiness/
parent: Using mailbagit
nav_order: 5
---

# Lossiness in Derivatives

`mailbagit` is committed to maintaining as many of the meaningful characteristics of each email message across derivatives as feasible. However, practical limitations can cause some derivative formats to be lossy:

* Some derivative formats, such as PDF, do not have the structure to appropriately store all parts of a message.
* In other cases, such as PST and MSG, dependency libraries do not provide complete access to all the technical characteristics of a message.
	* `mailbagit` maintains what we feel are the meaningful characteristics of each message as defined by the `mailbagit` [email model](https://github.com/UAlbanyArchives/mailbag/blob/develop/mailbag/models.py).
	* Derivative EML or MBOX files created from PST or MSG source messages will contain all message headers, correctly encoded HTML and plain text bodies if present, and attachments.
	* The part structure of a message will not be maintained.
* Generating EMLs from an MBOX or the reverse writes the full Python email message object, so this should be lossless and contain the full part structure of a message.

Mailbag's approach to keep messages in multiple formats is designed to mitigate these issues by maintaining the original source format alongside all derivatives.

However, if this does not fit you're use case, please let us know by [submitting an issue](https://github.com/UAlbanyArchives/mailbag/issues)!
