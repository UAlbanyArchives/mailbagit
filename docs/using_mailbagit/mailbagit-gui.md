---
layout: page
title: Mailbagit GUI
permalink: /mailbagit-gui/
parent: Using mailbagit
nav_order: 2
---

# mailbagit-gui

Mailbag-it includes a very basic graphical user interface (GUI)

You should be able to run the GUI by entering the `mailbagit-gui` command or by double clicking the `mailbag-gui.exe` file if you are using the [Windows executables]({{ site.baseurl }}/exe). The mailbagit GUI is currently not supported while using a docker image.

## Accessibility

The mailbagit GUI currently has severe accessibility limitations. Most notably, when using a screen reader with `mailbagit-gui` the tab key does not change the focus to the input fields. Once you click into the scrollable window, the tab key does work. The multi-option derivatives field is also not accessible using a keyboard and requires clicking with a mouse.

This is due to [accessibility issues](https://github.com/chriskiehl/Gooey/issues/747) with underlying dependancies wxPython and wxWidgets, and unfortunately, we don't have he capacity to do much about it.

Instead, we plan to implement a "guided" command line option, which we hope may provide accessible access to users without command line experience.

## Mailbagit GUI on Windows 

There is a [known issue](https://github.com/UAlbanyArchives/mailbag/issues/155) where the GUI does not fully run on Windows using the `mailbagit-gui` command. It will boot and lets you enter options but then fails to run when you click "Start."

The GUI will run on Windows using the `mailbagit-gui.exe` [executable]({{ site.baseurl }}/exe).

If you are runnig it natively with python, you can also try creating a file called `mailbagit-gui.py` with the contents:

```
from mailbag import gui
gui()
```

You should then be able to run the GUI with `python3 mailbagit-gui.py`.

## Using mailbagit-gui 

![Screenshot of the mailbagit GUI.]({{ site.baseurl }}/mailbagit-gui.png)


### Path

Enter the path to email to be packaged into a mailbag. This can be a single file or a directory containing a number of email exports.

Relative paths from where `maibagit-gui` was launched are supported, but you may want to use the complete path, such as:

`C:\Users\[my_username]\email_account`

`/home/[my_username]/export.pst`


Descriptions for [additional arguments]({{ site.baseurl }}/mailbagit/#arguments).
