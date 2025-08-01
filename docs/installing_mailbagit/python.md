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
pip install mailbagit
```

## Working with PST files

Packaging mailbags from PST files requires additional dependencies, notably `libpff-python`. To install these, in addition to `pip install mailbagit`, you need to run:

```
pip install 'mailbagit[pst]'
```

### Working with PST files on Windows

Building `libpff-python` on Windows requires Visual Studio C++ Build Tools. Without this you will get an error. To rectify this:

1. Install [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/) (Community Edition works fine.)
2. Using the Visual Studio installer, in the Workloads tab make sure to check at least **"Desktop development with C++"** the **VS 2019 C++ x64/x86 build tools**, and **Windows 10/11 SDK** in the Installation details optional settings on the right side.

![Screenshot of checking the correct options using the Visual Studio Installer.]({{ site.baseurl }}/img/windows_install.png)

Once the VS 2019/2022 C++ x64/x86 build tools and the Windows 10/11 SDK are installed, you can exit the Visual Studio installer. You won't need to use it directly to run `mailbagit`, it is just required to install the PST dependencies.

You can now try installing the PST dependencies with:

```
pip install 'mailbagit[pst]'
```

### Common Windows troubleshooting

Once you've installed the C++ Build tools, environment issues can still cause building `libpff-python` on Windows to fail. Here are some common issues.

1. `fatal error C1083: Cannot open include file: 'windows.h': No such file or directory`

Check if you have a `Windows.h` file in `C:\Program Files (x86)\Windows Kits\10\Include\10.0.*\um\Windows.h`. If this file is present, this can be fixed by adding these paths in Powershell:
```
$env:INCLUDE = "C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\um;C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\shared;C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\ucrt;$env:INCLUDE"
$env:LIB = "C:\Program Files (x86)\Windows Kits\10\Lib\10.0.26100.0\um\x64;C:\Program Files (x86)\Windows Kits\10\Lib\10.0.26100.0\ucrt\x64;$env:LIB"
```
Then retry:
```
pip install mailbagit[pst]
```

2. `fatal error C1083: Cannot open include file: 'ctype.h': No such file or directory`

Check if you have a `ctype.h` file in `C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\ucrt\ctype.h`. If this file is present, this can be fixed by adding this path in Powershell:
```
$env:INCLUDE = "C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\ucrt;$env:INCLUDE"
```
Then retry:
```
pip install mailbagit[pst]
```

3. `LINK : fatal error LNK1158: cannot run 'rc.exe'`

Check if you have a `rc.exe` file in `C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\rc.exe`. If this file is present, this can be fixed by adding this path in Powershell:
```
$env:PATH = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64;$env:PATH"
```
Then retry:
```
pip install mailbagit[pst]
```

If you still have trouble installing the PST dependencies on Windows, try using the [Docker install]({{ site.baseurl }}/docker) or [Windows executables]({{ site.baseurl }}/exe).

## Using the Mailbagit Graphical User Interface (GUI)

To install the mailbagit GUI, in addition to `pip install mailbagit`, you need to run:

```
pip install 'mailbagit[gui]'
```

If it is installed correctly, the GUI will run using the `mailbagit-gui` command.

### Mailbagit GUI on Windows

There is a [known issue](https://github.com/UAlbanyArchives/mailbagit/issues/155) where the GUI does not run with the `mailbagit-gui` command on Windows. It will boot and lets you enter options but then fails to run when you click "start."

Instead, try creating a file called `mailbagit-gui.py` with the contents:

```
from mailbagit import gui
gui()
```

You should then be able to run the GUI with `python3 mailbagit-gui.py`.

### Mailbagit GUI on Ubuntu

The GUI dependency wxPython does not install well on some environments, including Ubuntu. If `pip install mailbagit[gui]` fails, you may want to try a [specific version for your distro](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/).

For example, on Ubuntu 20.04, this seems to work well.

```
pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
```

After wxPython is installed, try running `pip install mailbagit[gui]` again.