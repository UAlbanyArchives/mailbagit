---
layout: page
title: Windows Executables
permalink: /exe/
parent: Installing mailbagit
nav_order: 3
---

# Windows Executables

Executables are available for Windows that contain all dependencies except the [PDF dependencies]({{ site.baseurl }}/pdf). Download the latest `mailbagit.exe` and `mailbagit-gui.exe` files from the [Github releases](https://github.com/UAlbanyArchives/mailbag/releases).

You can run `mailbagit.exe` in the command line [just as you would use the `mailbagit` command]({{ site.baseurl }}/mailbagit):

```
mailbagit.exe path/to/export.pst -i pst -d eml warc -m my_mailbag -r`
```

`mailbagit-gui.exe` will run just by double-clicking it.

These executables are unsigned, so Windows will likely give you as "Windows protected your PC" warning from Microsoft Defender SmartScreen. You will need sufficient permissions to allow unsigned executables on you machine.

![Screenshot Microsoft Defender SmartScreen preventing mailbagit-gui.exe from running due to an unsigned executable.]({{ site.baseurl }}/img/smart_screen.png)
