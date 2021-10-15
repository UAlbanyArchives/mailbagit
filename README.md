#Sample File
#mailbag arguments
Used to provide information to mailbag.

##Mandatory Arguments

Mandatory Arguments to be provided at runtime/usage:

1. **-i (input)**: To give the type of file as input to mailbag.
2. **-d (derivatives)**: To specify a single or list of formats required as results from mailbag.
e.g. ![img.png](img.png)


Optional arguments:
1. **--imap_host**:
>Hostname for IMAP connection for mailbag.
>Argument takes single input.

2. **--imap_password**:
>Password for IMAP connection for mailbag.
>Argument takes single input.

3. **--exclude_folder**:
>Email folders that need to be excluded from mailbag.
>Argument takes list or single folder input.

4. **--exclude_messages**:
>Email folders that need to be excluded from mailbag.
>Argument takes list or single input.

5. **-e --exclude_input**:
>Email folders will be excluded email folders or messaes before including in mailbag.
>Argument takes list or single input.
>Applicable for PST and MBOX files.

6. **-l --crawl_links**:
>Capture links in messages and include them in WARC derivative.



