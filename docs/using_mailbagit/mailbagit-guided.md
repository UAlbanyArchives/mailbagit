---
layout: page
title: Mailbagit Guided interface
permalink: /mailbagit-guided/
parent: Using mailbagit
nav_order: 3
---

# mailbagit "guided" interface

If you are not familiar with the traditional [command-line interface]({{ site.baseurl }}/mailbagit), you can try the `mailbagit-guided` interface. This still uses the command line, but asks you detailed questions and runs `mailbagit` based on your responses.

* [Download and install mailbagit]({{ site.baseurl }}/install).
* [Download a sample MBOX file]({{ site.baseurl }}/data/account.mbox) for training and testing.

![Screenshot of running the mailbagit-guided interface running on Windows.]({{ site.baseurl }}/img/mailbagit-guided.png)

To use this interface, once mailbagit is [installed]({{ site.baseurl }}/install), you can enter the `mailbagit-guided` command in Terminal on macOS or Linux, or CMD.exe or Powershell on Windows.

If you are using the [Windows executables]({{ site.baseurl }}/exe), you can just double-click on the `mailbagit-guided.exe` file.

Type answers into the prompt and hit "enter". At any prompt you can enter "exit" to stop.

## `mailbagit-guided` workflow

The command line will walk users through a series of prompts to process the emails into archival packages.

1. **Enter the file format you wish to package ([eml](https://www.loc.gov/preservation/digital/formats/fdd/fdd000388.shtml), [mbox](https://www.loc.gov/preservation/digital/formats/fdd/fdd000383.shtml), [msg](https://www.loc.gov/preservation/digital/formats/fdd/fdd000379.shtml), [pst](https://www.loc.gov/preservation/digital/formats/fdd/fdd000378.shtml)):**

    This is the existing email export format that you wish to package into a mailbag.

2. **Enter a path to the MBOX or PST file or a directory containing MBOX, PST, MSG, or EML files:**

    This might look similar to `C:\Users\[username]\Downloads\account.mbox` or `C:\Users\[username]\Documents\emailexports` on Windows, or `/home/[username]/export.pst` or `/home/[username]/path/to/email` on MacOS or Linux. 

    Note that the file path needs to be transcribed exactly. You can also use a path relative to your current working directory.

3. **Enter the derivatives formats to create separated by spaces ([eml](https://www.loc.gov/preservation/digital/formats/fdd/fdd000388.shtml), [html](https://www.loc.gov/preservation/digital/formats/fdd/fdd000475.shtml), [mbox](https://www.loc.gov/preservation/digital/formats/fdd/fdd000383.shtml), pdf-chrome, [pdf](https://www.loc.gov/preservation/digital/formats/fdd/fdd000030.shtml), txt, [warc](https://www.loc.gov/preservation/digital/formats/fdd/fdd000236.shtml)):**

    These are the derivative formats that `mailbagit`will create an include in the mailbag. `pdf-chrome` creates a PDF just like `pdf`, but uses a different dependency too. `chrome --headless` instead of `wkhtmltopdf`. PDF options will not display unless [PDF dependencies are installed]({{ site.baseurl }}/pdf).

4. **Enter a name for the mailbag:**

    This will be the folder or .zip file name for the mailbag.

5. **Would you like to try a dry run? This is a test run that will report errors but not alter your files. (yes, y, no, n):**

    A dry run means that it will attempt to parse the email and begins to generate derivatives, but does not actually save them or do anything to the input data. A dry run does create error and warnings reports. The dry run may take less time to process and can be useful to identify any problems or issues before actually creating a mailbag.

6. **Would you like more options? If no, we will package the mailbag. (yes, y, no, n):**

    Enter yes to answer questions 7-12. No will skip these options and proceed to step 8.

7. **Would you like to include companion files (such as metadata files) that are present in the provided directory?**

    If you entered a directory instead of a single file as a path, using this option will package all files and folders in that directory into the mailbag. If you select no, only the files you selected in option 1 will be included.

8. **Would you like to compress the mailbag? (no, n, zip, tar, tar.gz):**

    A [zip](https://www.loc.gov/preservation/digital/formats/fdd/fdd000354.shtml), [tar](https://www.loc.gov/preservation/digital/formats/fdd/fdd000531.shtml), or tar.gz (compressed tar) makes the mailbag into a single file and zip and tar.gz will make it smaller. If no is selected, `mailbagit` will keep the mailbag as a directory that you can browse.

9. **Would you like to log to a file? ({path/to/file.log}, no, n):**

    If you provide a path to a log file, `mailbagit` will log updates to this file in addition to the command line, so they will be available after you close the prompt. The file provided will be created if it does not already exist.

10. **Would you like to apply custom CSS to HTML and PDF derivatives? ({path/to/file.css}, no, n):**

    Add the path to a `.css` file to customize the styling for HTML and PDF derivatives, or select no.

11. **Mailbagit uses sha256 and sha512 by default to develop preservation manifests. Would you like to customize the checksums used? (yes, y, no, n):**

    [If yes,] **Enter the checksum algorithms to use separated by spaces (sha512, blake2s, md5, sha224, sha256, shake_128, shake_256, sha3_224, sha3_512, sha3_384, sha3_256, sha1, blake2b, sha384)**

    Different checksum algorithms have different strengths and weaknesses.

12. **Do you want to add custom metadata in bag-info.txt? (yes, y, no, n):**

    [If “yes] **Optional Metadata Fields:**
        
    **capture-date**
       
    **capture-agent**
        
    **capture-agent-version**

    **source-organization**

    **organization-address**

    **contact-name**

    **contact-phone**

    **contact-email**

    **external-description**

    **external-identifier**

    **bag-group-identifier**

    **bag-count**

    **internal-sender-identifier**

    **internal-sender-description**

    **bagit-profile-identifier**

    **Enter a field and value separated by colon (:), or enter "done" when complete:**

    To add any of the listed fields to `bag-info.txt`, enter the field, then a colon (:), then the value.

    For example: `source-organization: University at Albany, SUNY`

    You can keep entering fields, and enter `done` when you are finished.

13. After finishing these prompts, it will commence with parsing the emails and creating derivatives. It will show progress for every 1% of messages processed.

        INFO: Reading: .\path\to\account.mbox
        INFO: Found 331 messages.
        39.0% [Processed 129 of 331 messages] 7.45s remaining
        100.0% [Processed 331 of 331 messages] 0.0s remaining
        INFO: Writing CSV reports...
        INFO: Finished packaging mailbag.
        Mailbag finished packaging at .\path\to\mailbag. Press any key to finish.

Pressing a key closes the window, so be sure not the path to the mailbag first. Your mailbag is now complete!

* [What `mailbagit` creates]({{ site.baseurl }}/mailbagit#what-mailbagit-creates)
