# README

I use Xcode and LLDB to debug my Qt programs, and got tired with there being no visualisation for all the built-in types. Here I endeavour to make all of these types visible through the debugger. 
Works with Qt 5.x. Tested with Qt 5.9.8, 5.13.2 and XCode 11.

## Supported Qt Objects:
**Types added via QtFormatters.py**
* QMap
* QString
* QUrl
* QList
* QVector
* QPointer

**Types added via QtFormatters.lldb (summary-strings)**
* QMap
* QSize
* QSizeF
* QPoint
* QPointF
* QRect
* QRectF
* QUuid


## XCode Versions
XCode changed from Python 2.x to Python 3.x at Version 11.
If you need XCode 10 or earlier, check out or download the 1.0 Release tag

# Installation

git clone this repo somewhere, e.g. ~/qtlldb. Then add the following lines to your ~/.lldbinit:

```
command script import ~/qtlldb/QtFormatters.py
command source ~/qtlldb/QtFormatters.lldb
```

# Running Tests
Two testprojects exist, one for QtCreator and one for XCode:
Since the point of this project is to provide Qt Debugging info in XCode, running the XCode project in the debugger verifies that it is working.
I guess you could use the QtCreator project to compare and contrast debugger info between XCode and QtCreator

## General Notes:
Test project does not produce any output when run.

* lldbtests/lldbtests.pro
    * Open in Qt Creator and build.
    * Step throug main.cpp to see debug info

* lldbtests/XCodeTests.xcodeproj
    * Set path to your Qt Version in XCodeQtConfig.xcconfig
    * Open XCodeTests.xcodeproj in XCode and Build
    * Set a breakpoint on QString Ctor in main.cpp, step over remainder of project to see debug info in XCode.
    * Seems to sometimes do odd things when broken on a line constructing a Qt Object, like show a long list of undefined values. 

# Testing and Modifying QtFormatters.py

**Performance Note** I added the exception printing stuff in the printException() method near the top. This required some imports, and I am unsure if this has any performance implications. If you have performance issues, I would suggest commenting out most of printException() and the associated imports.

1.  When testing changes to QtFormatters.py you can see compile time errors by manually reloading the file in the XCode Debugger. To do this enter `command script import ~/qtlldb/QtFormatters.py` in the debugger
output window
1. I am not aware of any realtime debugging facilities for this python code, simply use the Python print statement. `print("Hello World")` in the Python code
1. XCode uses Python3 independent of OSX, see the [XCode 11 Release Notes](https://developer.apple.com/documentation/xcode_release_notes/xcode_11_release_notes)

# Modifying the .lldb file
Documentation for adding summary-strings is found at: https://lldb.llvm.org/varformats.html


# Origin and Credits
A number of variants of this project exist on bitbucket and Github. As far as I can tell, the earliest is LukeWorth.
Notable projects are shown below, with the earliest project last.


| Fork | First Commit | Last Commit | Notes |
| --------------- | --------------------- | ------------ | ----------------------- |
| [https://github.com/SteveSchilz/lldb-qt-formatters] | 2019-12-10 | 2019-12-11 | Updated for XCode 11/Python 3 |
| [https://github.com/pavolmarkovic-serato/lldb-qt-formatters] | 2016-12-12 | 2016-12-12 | Direct fork of LukeWorth, including commit history | 
| [https://github.com/ivany4/lldb-qt] | 2016-02-25 | 2016-02-25 | Works with Qt4, same code, different attribution | 
| [https://bitbucket.org/lukeworth/lldb-qt-formatters/src/default/] | 2015-10-16 | 2015-10-16 | Apears to be earliest version of this code | 

QMap provider implementation: https://github.com/sdonegan/Qt5DataFormatters
