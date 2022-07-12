---
layout: page
title: Changelog
permalink: /spec/changelog/
parent: Mailbag Specification
nav_order: 1
---

# Mailbag Specification Changelog

## [Mailbag Specification 1.0.0](https://github.com/UAlbanyArchives/mailbag-specification/tree/v1.0.0)

### Release Notes

* Old `original_filenames.txt` for attachments renamed as `attachments.csv` and now required to better handle missing filenames and filename normalization.
* CSV rules clarified and moved to Section 5.5 as they now impact both `mailbag.csv` and `attachments.csv`.
* Added explicit support for "companion" metadata files in mailbags.
* Added PREMIS XML examples provided by [@asciim0](https://github.com/asciim0).
* Reworded sections based on comments on [0.3 release](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.7l1mpm88wrx5). 

## [Mailbag Specification 0.3 (Release Candidate)](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s)

The Mailbag Project Team is seeking another round of feedback on a release candidate for the the Mailbag Specification.

Please comment directly in the [Google Doc](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s) or [open an issue on the Mailbag Github repo](https://github.com/UAlbanyArchives/mailbag/issues?q=is%3Aopen+is%3Aissue+label%3ASpecification). We hope to release a 1.0 version of the specification after addressing any feedback over the next few weeks.

We are very thankful for any time you contribute to providing feedback!

### Supporting multiple email accounts

Originally, the specification was designed to package a single email account export, as preserving the folder structure of an account was a major priority for the project. We received a lot of feedback that this was a significant limitation, but we were originally not very confident that we could preserve the intellectual arrangement of email while also supporting multiple email accounts. But after some real-world testing in developing the Mailbagit tool, we think we have found a reasonable solution.

In version 0.3, a mailbag is not opinionated on whether it contains a single or multiple email accounts or even whether the directory structure that it packages is a meaningful arrangement at all. It only attempts to fully document the directory structure it is provided as well as any email folder structure it can extract in the mailbag.csv tag file. It uses three fields to do this:

* **Original-File** contains the directory path to the source file for each message.
* **Message-Path** contains any account structure extracted from PST files or headers like X-Folder or X-Gmail-Labels.
* **Derivatives-Path** is a join of Original-File (with the file extension removed) and Message-Path. This is the path used to reference all derivative files in a mailbag. This field must be normalized for use as a valid path for the filesystem where a mailbag was packaged. A mailbag is not opinionated on which normalization method is used.

We this is the simplest implementation we could come up with that sufficiently documents everything. Let us know if there is something we’ve overlooked!

### Release Notes

* Section [4.2](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.t4w0fhjwrsqd) was edited to reflect the importance of Derivatives-Path

* Section [5.3.1](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.9jushxrdueo0) and [5.3.2](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.70gu3alwulyk) were updated to include Original-File, Message-Path, and Derivatives-Path with definitions and examples.

* Section [5.3.1](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.9jushxrdueo0) and [5.3.2](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.70gu3alwulyk) were updated to include an Error field in mailbag.csv which is useful to denote any parser or derivatives errors found while packaging a mailbag. Implementations are also recommended to provide a more comprehensive error report outside of a mailbag.

* Mailbag.csv columns reordered in Section [5.3.1](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.9jushxrdueo0) and [5.3.2](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.70gu3alwulyk).

* In section [5.2.3](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.rqrp1fpyl84z), Mailbag-Source-Filename removed as an optional field. Including multiple PST or MBOX files in a mailbag makes this less useful and source files are documented in the Original-File field in mailbag.csv. As all bag-info fields are extensible, implementations are still welcome to document this in bag-info if they would like.

* In sections [4.4.1](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.kg9oibl5xplj) and [4.4.1.2](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.3giekbx1xbqw) the specification no longer recommends maintaining original folder names for derivative files. Instead, it now requires the use of Mailbag-Message-ID. The example in section [4.4.5](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.hvsz4is8wa2o) was updated to reflect this.

* In creating the mailbagit tool, we discovered that email folder names, when extracted from PST files or X-Folder or X-Gmail-Labels email headers pose an additional risk of filesystem incompatibility issues due to the potential for special characters. Section [4.2.2](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.77cboovq697l) was added to address this and the existing section [4.4.3](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.jho5sd2cx0rt) was edited to maintain consistency.

* [Section 1.4](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.i2ggtr8urws8) was updated to allow v0.97 bags, as Bagit-Python has yet to be tested with v1.0 and still creates bags labeled as v0.97 compliant.

* [Section 1.5](https://docs.google.com/document/d/1BZHklc6MKktXJBPcvFvlxLRoX8lCidFemflppqpUQ7s/edit#heading=h.inl77t9vizrb) was updated to add more information in the Email folder definition



## [Mailbag Specification 0.2 (Call for Comments)](https://docs.google.com/document/d/1X7pOHxxzZl6PyMAJWd7bIR11rE4FlKty3J7oI6ghAKo)

The Mailbag Project Team is interested in any feedback on this version of the Mailbag Specification!

We received some really wonderful feedback from both the earlier call for comments on the design documents and the specification working meeting! We truly appreciate the thoughtfulness and energy we’ve received from the community so far. Much of the feedback was either positive or easy to fix or incorporate, but there were also a number of thoughts that generated some interesting discussions among the advisory board. We wrote up these decision points as Github issues to document our thinking and hopefully to open up these conversations to the community.

For this round of feedback, we would love to hear what you think about these issues in particular:

* [Can/should a mailbag contain multiple email accounts?](https://github.com/UAlbanyArchives/mailbag/issues/2)
* [Can a mailbag be used to package multiple versions of email, such as for weeding or redactions?](https://github.com/UAlbanyArchives/mailbag/issues/3)
* [Will a mailbag include descriptive metadata?](https://github.com/UAlbanyArchives/mailbag/issues/4)
* [Will a Mailbag include PREMIS events?](https://github.com/UAlbanyArchives/mailbag/issues/5)
* [Use of mailbag.csv](https://github.com/UAlbanyArchives/mailbag/issues/6)
* [Use of original filenames](https://github.com/UAlbanyArchives/mailbag/issues/7)
* [Will mailbag use EA-PDF?](https://github.com/UAlbanyArchives/mailbag/issues/8)
* [Use of personas](https://github.com/UAlbanyArchives/mailbag/issues/9)
* [Line endings and encoding for tag files](https://github.com/UAlbanyArchives/mailbag/issues/10)

You are also welcome to comment generally on the specification! We particularly welcome comments that can foster a public discussion, such as a [Github issues](https://github.com/UAlbanyArchives/mailbag/issues) or comment directly in the [Google Doc]((https://docs.google.com/document/d/1X7pOHxxzZl6PyMAJWd7bIR11rE4FlKty3J7oI6ghAKo)). You can also email comments directly to gwiedeman [at] albany [dot] edu.

Any feedback is great, and it’s even more actionable for us if you offer specific user stories or make connections to the [project personas](https://archives.albany.edu/mailbag/personas/)!


## [Mailbag Specification 0.1 (Working Meeting Pre-Release)](https://docs.google.com/document/d/1XHSbmHsL-VW2IJzoJVTNjVh-E3RKnUpmvrZygJ8ls0A)

* [Static PDF](Mailbag_Specification_prerelease.pdf)

The project is currently incorporating feedback from the [Working Meeting](/mailbag/cfp). Since this process is taking a bit longer than expected, we decided to publicly  link the Pre-Release for anyone interested. We do expect this document to substantially change, and we hope to soon publish an updated version along with a public call for comments in the coming weeks.