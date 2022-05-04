---
layout: page
title: Windows Executables
permalink: /exe/
parent: Installing mailbagit
nav_order: 2
---

# Windows Executables

Executables are available for Windows that contain all dependencies except the PDF dependencies. Download the latest `mailbagit.exe` and `mailbagit-gui.exe` files from the [Github releases](https://github.com/UAlbanyArchives/mailbag/releases).

You can just double-click on `mailbagit-gui.exe` to load the GUI, or use `mailbagit.exe` in the command line as you would for a [native python install]({{ site.baseurl }}/use/#using-the-mailbagit-command-line-utility):

`mailbagit.exe path/to/files -i pst -d pdf warc -m my_mailbag`

These executables are unsigned, so Windows will likely give you as "Windows protected your PC" warning from Microsoft Defender SmartScreen. You will need sufficient permissions to allow unsigned executables on you machine.


![Screenshot of Microsoft Defender SmartScreen preventing mailbagit.exe from running.]({{ site.baseurl }}/smart_screen.png)
