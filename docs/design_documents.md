---
layout: page
title: Design Documents
permalink: /design_docs/
nav_order: 4
has_children: true
---


## Design Documents

The Project Team and Advisory Board developed these design documents to help define the Mailbag tool and communicate its features and limits. We welcome your feedback, particularly during the community comment period that ends after April 25th, 2021.

* [Comment on Personas](https://docs.google.com/forms/d/e/1FAIpQLSeZ3WLjaPdJWjPMYSc4BjTVIIv_fnHm7D1vKk1pqsx9tnNQsQ/viewform?usp=sf_link)
* [Suggest a User Story](https://docs.google.com/forms/d/e/1FAIpQLSf68TbV5mbZ48pm_lrGB_SK4oxZO0FtGeUqOfoK6gEQ5iq2WA/viewform?usp=sf_link)
* [Suggest or Prioritize a Requirement](https://docs.google.com/forms/d/e/1FAIpQLScg34b0NJhuDWaUUvyWJxyK5bBGf9Hh9N0n76XElsoBJd7S1Q/viewform?usp=sf_link)

## Project Outcomes

### [Mailbag Specification](https://archives.albany.edu/mailbag/spec/)

* A functional specification to package email exports using multiple formats in a [Bagit "bag"](https://tools.ietf.org/html/rfc8493).
* Ensures a structure where email messages will remain actionable among multiple formats.

### Command line Mailbag tool and Python library

* Will accept common email export formats and create valid "mailbags" according to the Mailbag Specification.
* Will optionally convert email exports to derivative formats and include them in a mailbag.
* Will include basic reporting functionality to list included messages.
* Will allow easy pathways to other email appraisal and processing tools.

### Basic graphical user interface (GUI) wrapper for command line Mailbag tool.

* Will include at least the basic functionality of the command line Mailbag tool.
* Will be accessible to users using assistive technology.