---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
nav_exclude: true
---

# Mailbag
{: .fs-9 }

A Stable Package for Email in Multiple Formats
{: .fs-6 .fw-300 }

[Mailbag Specification]({{ site.baseurl }}/spec){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[Mailbagit Github](https://github.com/UAlbanyArchives/mailbagit){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

---

The Mailbag project is a [draft specification]({{ site.baseurl }}/spec) and `mailbagit` open source tool for preserving email archives using multiple formats, such as MBOX, PDF, and WARC.

Currently there is no single effective preservation format, so the Mailbag approach is to preserve multiple formats in a stable and computer-actionable package. MBOX or EML files provide structured access for computational use, PDF files preserve the document-like rendering of email well and provide easy dissemination, and web archives preserve the potential interactivity of email HTML and CSS, as well as embedded and linked Web content from external sources.

The [Mailbag specification]({{ site.baseurl }}/spec) is an extension  of the [Bagit specification](https://tools.ietf.org/html/rfc8493). A mailbag is a special type of "bag," with designated storage for common email exports like MBOX or PST, PDF files, and Web Archives. Mailbags also contain specific metadata about its contents to enable them to be computer actionable, as well as limited serialized email header data.

Many of the tools available for email processing are also challenging for many archivists to use. Email also must be processed near-to-capture, to ensure that content hosted on external servers is not lost. The [`mailbagit` tool]({{ site.baseurl }}/use)  enables archivists to rapidly process email archives and package them into Mailbags. A basic graphical user interface (GUI) lowers the barrier for this work.

![An overview diagram of a Mailbag and its use by the mailbag tool.](diagrams/mailbagOverview.png)


### Acknowledgments

This project was made possible by funding from the University of Illinois's [Email Archives: Building Capacity and Community Project](https://emailarchivesgrant.library.illinois.edu/).

We owe a lot to the hard work that goes towards developing and maintaining the libraries `mailbagit` uses to parse email formats and make bags. We'd like to thank these awesome projects, without which `mailbagit` wouldn't be possible:  

* [extractMsg](https://github.com/TeamMsgExtractor/msg-extractor)
* [libpff](https://github.com/libyal/libpff)
* [bagit-python](https://github.com/LibraryOfCongress/bagit-python)

We'd also like to thank the [RATOM project](https://ratom.web.unc.edu/) whose documentation was super helpful in guiding us though some roadblocks.


Hosted by the [M.E. Grenander Department of Special Collections & Archives](https://archives.albany.edu/), [University at Albany, SUNY](https://www.albany.edu)
