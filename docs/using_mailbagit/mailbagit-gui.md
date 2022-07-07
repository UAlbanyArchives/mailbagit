---
layout: page
title: Mailbagit GUI
permalink: /mailbagit-gui/
parent: Using mailbagit
nav_order: 2
---

# mailbagit-gui

Mailbagit includes a very basic graphical user interface (GUI)

If `mailbagit` is [installed]({{ site.baseurl }}/python/) you should be able to run the GUI by entering the `mailbagit-gui` command. The mailbagit GUI is currently not supported while running in a docker container.

[Download and install mailbagit]({{ site.baseurl }}/install).
[Download a sample MBOX file]({{ site.baseurl }}/data/account.mbox) for training and testing.

## Accessibility

The mailbagit GUI currently has severe accessibility limitations. Most notably, when using a screen reader with `mailbagit-gui` the tab key does not change the focus to the input fields. Once you click into the scrollable window, the tab key does work. The multi-option derivatives field is also not accessible using a keyboard and requires clicking with a mouse.

This is due to [accessibility issues](https://github.com/chriskiehl/Gooey/issues/747) with underlying dependencies wxPython and wxWidgets, and unfortunately, we don't have the capacity to do much about it.

Instead, we suggest using the ["guided" command line option]({{ site.baseurl }}/mailbagit-guided/), which should provide accessible access and may be easier for users without command line experience.

## Mailbagit GUI on Windows 

There is a [known issue](https://github.com/UAlbanyArchives/mailbagit/issues/155) where the GUI does not fully run on Windows using the `mailbagit-gui` command. It will boot and lets you enter options but then fails to run when you click "Start."

The GUI will run on Windows without this issue using the `mailbagit-gui.exe` [executables]({{ site.baseurl }}/exe).

If you are running it natively with python, you can also try creating a file called `mailbagit-gui.py` with the contents:

```
from mailbagit import gui
gui()
```

You should then be able to run the GUI with `python3 mailbagit-gui.py`.

## Using mailbagit-gui 

![Screenshot of the mailbagit GUI.]({{ site.baseurl }}/img/mailbagit-gui.png)


### Path

Enter the path to email to be packaged into a mailbag. This can be a single file or a directory containing a number of email exports.

Relative paths from where `maibagit-gui` was launched are supported, but you may want to use the complete path, such as:

`C:\Users\[my_username]\email_account`

`/home/[my_username]/export.pst`


Descriptions for [additional arguments]({{ site.baseurl }}/mailbagit/#arguments).
