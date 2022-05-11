---
layout: page
title: Installing with Python
permalink: /python/
parent: Installing mailbagit
nav_order: 1
---

# Installing with Python


To install `mailbagit` using Python, you just need Python version 3.7 or higher with pip.

If you're installing Python on Windows, during the install make sure to select the option to **"Add Python to PATH"**. 

Pip should come installed with Python on Windows. On Mac or Linux, you should already have Python installed, but you may have to run `python3 -m ensurepip` if you don't already have pip.

When you have Python >3.7 and pip, to install `mailbagit`, just run:

```
pip install mailbag
```

## Working with PST files

Packaging mailbags from PST files requires additional dependencies. To install these, in addition to `pip install mailbag`, you need to run:

```
pip install mailbag[pst]
```

Installing this on Windows requires Visual Studio C++ Build Tools. Without this you will get an error. To rectify this:

1. Install [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/) (Community Edition works fine.)
2. Using the Visual Studio installer, in the Workloads tab make sure to check at least **"Desktop development with C++"** and the **VS 2019 C++ x64/x86 build tools** in the Installation details optional settings on the right side.

![Screenshot of checking the correct options using the Visual Studio Installer.]({{ site.baseurl }}/img/windows_install.png)

Once the VS 2019 C++ x64/x86 build tools are installed, you can exit the Visual Studio installer. You won't need to use it directly to run `mailbagit`, it is just required to install the PST dependencies.

You should now be able install the PST dependencies with:

```
pip install mailbag[pst]
```

## Using the Mailbagit Graphical User Interface (GUI)

To install the mailbagit GUI, in addition to `pip install mailbag`, you need to run:

```
pip install mailbag[gui]
```

If it is installed correctly, the GUI will run using the `mailbagit-gui` command.

### Mailbagit GUI on Windows

There is a [known issue](https://github.com/UAlbanyArchives/mailbag/issues/155) where the GUI does not run with the `mailbagit-gui` command on Windows. It will boot and lets you enter options but then fails to run when you click "start."

Instead, try creating a file called `mailbagit-gui.py` with the contents:

```
from mailbag import gui
gui()
```

You should then be able to run the GUI with `python3 mailbagit-gui.py`.

### Mailbagit GUI on Ubuntu

The GUI dependency wxPython does not install well on some environments, including Ubuntu. If `pip install mailbag[gui]` fails, you may want to try a [specific version for your distro](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/).

For example, on Ubuntu 20.04, this seems to work well.

```
pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
```

After wxPython is installed, try running `pip install mailbag[gui]` again.