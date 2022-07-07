---
layout: page
title: Mailbagit Guided interface
permalink: /mailbagit-guided/
parent: Using mailbagit
nav_order: 3
---

# `mailbagit` "guided" interface

If you are not familiar with the traditonal [command-line interface]({{ site.baseurl }}/mailbagit), you can try the `mailbagit-guided` interface. This still uses the command line, but asks you detailed questions and runs `mailbagit` based on your responses.

[Download and install mailbagit]({{ site.baseurl }}/install).
[Download a sample MBOX file]({{ site.baseurl }}/data/account.mbox) for training and testing.

To use this interface, once mailbagit is [installed]({{ site.baseurl }}/install), you can enter the `mailbagit-guided` command in Terminal on macOS or Linux, or CMD.exe or Powershell on Windows.

If you are using the [Windows executables]({{ site.baseurl }}/exe), you can just double-click on the `mailbagit-guided.exe` file.

## `mailbagit-guided` workflow

The command line will walk users through a series of prompts to process the emails into archival packages.

1. Enter the file format you wish to package ([eml](https://www.loc.gov/preservation/digital/formats/fdd/fdd000388.shtml), [mbox](https://www.loc.gov/preservation/digital/formats/fdd/fdd000383.shtml), [msg](https://www.loc.gov/preservation/digital/formats/fdd/fdd000379.shtml), [pst](https://www.loc.gov/preservation/digital/formats/fdd/fdd000378.shtml)).

This is the exiting email export format that you have and wish to package into a mailbag.

2. Enter a path to a MBOX file or a directory containing MBOX files.

To find this file path, right-click on the item>properties>and copy the folder path, which might look similar to this: C:\Users\[username]\Downloads\filename.mbox. Note that the file path needs to be transcribed exactly.

3. Enter the derivatives formats to create separated by spaces (html, mbox, txt, warc):

4. Enter a name for the mailbag: - name the folder you wish to create

5. Would you like to try a dry run? (yes, y, no, n):

A dry run means that it will attempt to parse the email and begins to generate derivatives, but does not actually save them or do anything to the input data. A dry run does create error and warnings reports. The dry run may take less time to process and can be useful to identify any problems or issues before actually creating a mailbag.

6. Would you like more options? (yes, y, no, n):

7. [if “yes”] Would you like to compress the mailbag? (no, n, zip, tar, tar.gz): [Add text about why someone would want to do this or not]

8. Would you like to apply custom CSS to HTML and PDF derivatives? ({path/to/file.css}, no, n): If you have a specific CSS to control the appearance of the exported emails, add the file path. If you don’t have this CSS file, indicate no or n.
Mailbagit uses sha256 and sha512 by default to develop preservation manifests. Would you like to customize the checksums used? (yes, y, no, n): Depending on your institutional practices or additional preservation tools you may use, you may wish to customize it to other checksum values or keep with the default settings.
Do you want to add custom metadata in bag-info.txt? (yes, y, no, n):
[If “yes] Optional Metadata Fields:
        capture-date
        capture-agent
        capture-agent-version
        source-organization
        organization-address
        contact-name
        contact-phone
        contact-email
        external-description
        external-identifier
        bag-group-identifier
        bag-count
        internal-sender-identifier
        internal-sender-description
        bagit-profile-identifier
Enter a field and value separated by colon (:), or enter "done" when complete:
