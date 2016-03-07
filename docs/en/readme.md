tagline: Accessible eBook conversion and DRM removal
author_field: Author
version_field: Version
home_page_link_text: Project Home Page

[TOC]

##Introduction
Codex is a software application which aims to make the process of eBook conversion and DRM removal as easy, customisable and, of course, screen reader accessible as possible.  It offers a simple interface as well as integration with Windows Explorer (and other third party shells should you use one) and uses the excellent [calibre eBook management software](http://calibre-ebook.com/) behind the scenes to make most of the magic happen.

Codex would probably not exist without calibre, but calibre's user interface is not at all screen reader friendly.  Thus, you can think of Codex as some particularly fancy glue to stick everything together.  Having said that, you don't need to obtain, install or even know anything about calibre in order to use Codex.  It is only mentioned here to give credit where credit is due.  Codex also uses DRM removal plug-ins from [Apprentice Alf’s Blog](https://apprenticealf.wordpress.com/), but again, the installation and configuration of these is handled automatically for you.

Important note: Throughout this readme file, you will see references to Windows Explorer integration.  This is a convenience feature provided by Codex, but unfortunately, it is not available on Windows versions earlier than Windows 7 at this time.

##Installation
Codex is distributed inside a standard software installer, the sort you will already be familiar with.  You can always obtain the latest version from [the project's home page](http://jscholes.net/project/codex).  After downloading the setup file, just launch it and follow the instructions.  You can run the application from within the installer once installation is complete.

Important note: If installing Codex for the first time, be sure to run it at least once so that it can set up the default options for you, as well as integrate itself with Windows Explorer.  This is also a good time to become familiar with the main window and Options dialog where you can set the preferences to your liking.

##eBook conversion
Converting eBooks with Codex is incredibly straight forward.  There are two ways to do it: Through the application's main window, or via the Windows Explorer integration.  Regardless of which method you choose, by default your converted files will be stored in Documents\eBooks\author name\title`.  You can change the output directory and filename template in the Options dialog.

Codex is unable to convert eBooks that still have DRM, so the conversion process will also attempt to strip any protection from them.  In other words, you don't need to remove the DRM and then convert, you can do both in one step.

First, let's talk about the formats it can handle.

###Input formats
Codex can convert eBooks in any of the following formats:

* Kindle and Mobipocket eBooks (files with a .azw, .azw3, .azw4 or .mobi file extension)
* ePub (.epub)
* Microsoft Word 2007 (.docx)
* Rich text format (.rtf)
* Plain text (.txt) and compressed plain text (.txtz)
* PDF (.pdf)
* HTML (.html) and compressed HTML (.htmlz)
* Microsoft Reader (.lit)
* FictionBook (.fb2)
* Microsoft Compiled HTML Help files (.chm)
* Broad Band eBook (.lrf)
* Palm eBook (.pdb, .pml and .prc)
* OpenDocument (.odt)
* EPOC (.tcr)
* Rocket eBook (.rb)
* Shanda Bambook (.snb)
* DjVu (.djvu)
* Various comic book archives (.cbc, .cbr, .cbz)

Note: Not all eBooks or eBook formats are created equal.  The support for or existance of various features, such as title and author metadata, is not present in all formats and cannot be guaranteed.

###Output formats
Any file in one of the supported input formats listed above can be converted to any of these formats:

* Kindle (.azw3)
* ePub (.epub)
* Microsoft Word 2007 (.docx)
* Compressed HTML (.htmlz)
* Mobipocket (.mobi)
* PDF (.pdf)
* Rich text format (.rtf)
* Plain text (.txt)

Note: Compressed HTML (.htmlz) files can be opened or extracted using any tool which supports ZIP archives.  The file index.html can then be loaded into a web browser or other application which supports HTML documents.

###Converting using the Codex main window
When you open Codex, the first thing you'll notice is the files list.  To convert one or multiple files, simply:

1. Use the Add files and Add folders buttons to locate your eBook files and/or folders
2. Select the desired output format from the combo box
3. Click Convert

A dialog box will open, givign you information on the current file being converted and overall progress, as well as allowing you to skip the current file or cancel the conversion process altogether.  Once conversion is complete, the conversion complete dialog will display your converted files, allow you to open them straight from Codex, and let you know about any files that could not be converted for whatever reason.

###Converting straight from Windows Explorer
One of the most convenient options provided by Codex is the integration with the right-click context menu for files and folders in Windows Explorer and other shells.  This saves you time, as you don't need to open Codex explicitly to convert a book.  Just do the following:

1. In Windows Explorer or your file manager of choice, locate your eBook file or folder as you usually would
2. Right-click the file or press the Applications key to bring up the context menu
3. Scrol down to the Codex sub menu and expand it, or press the shortcut key X
4. Choose one of the following options:
    * Convert: Will convert the selected file, or supported files within the selected folder, to the default output format which can be set in the Codex Options dialog
    * Convert to: As above, but allows you to select a different output format other than the default
    * Remove DRM: Attempt to strip any DRM protection from the eBook(s), leaving the original format intact

The rest of the process is the same as when converting from the Codex main window.  Please note that currently, you can't select multiple files in Explorer to convert them all at once.  You'll either need to place them in their own folder, add them using the Add files dialog within Codex which does support the selection of multiple files, or convert them one by one.

##DRM Removal
If you wish to remove the DRM from a book, but leave the original file intact, this option is for you.  This is useful if you have an Adobe Digital Editions book that's already in ePub, for example.  Converting it from ePub to ePub again would be a waste of time, and would probably result in a book with degraded quality.

The DRM removal process is very similar to that of conversion.  If using the Codex main window, add your files and folders, but use the Remove DRM button instead of Convert.  The value of the output format combo box is ignored.  From a file's shell context menu, choose the Remove DRM option from the Codex submenu.  All other details are the same as for the conversion process, documented above.

##Finding Kindle books for conversion
One of the primary reasons Codex exists, and indeed the main reason why I created it, is its ability to convert eBooks purchased from Amazon's Kindle Store to any of the output formats listed above.  You can then read the resulting files on any device or in any software of your choice.  To that end, Codex includes two very easy ways to locate your Kindle eBook files once you've downloaded them using the Kindle for PC software.  You can find both of these in the Tools menu, accessible from Codex's main window.

###Find Kindle file from Amazon URL
If you have the URL to an eBook's product page on the Amazon website, and the corresponding eBook file is on your computer, type or paste in that URL and Codex will quickly find the file and add it to the Files list for conversion.  This is useful if, for instance, you purchased a book a long time ago and don't want to hunt through your entire library for it.  Instead, you can simply search in the Kindle Store and copy the URL.

###Browse downloaded Kindle books
This option is great for quickly locating the most recent books you've downloaded, as well as for looking through your collection.  A dialog box will pop up, showing a list of books in your Kindle content directory.  For each one, its author, title and filename will be shown.  The books are sorted by last modified date.  Select one or more titles and press Enter to add them to the Files list.

Note: In order to avoid slowing down the Codex user interface, this dialog loads book information in the background.  Therefore, if you find that not all of your books have appeared in the list, it should only take a couple of seconds at most to see them.  Likewise, if you're only interested in a file at or near the top of the list, but you have a large Kindle library, you don't have to wait for information for every book to be retrieved before making your selection.

##Options
The Codex Options dialog, accessible from the main window, offers the following settings:

###Output
* Output directory: A setting to control where your processed eBooks are stored, plus a Browse button.
* Output filename template: An option to control how your output files are named.  The default is $author\$title, which tells Codex to store your files in author subdirectories, with their titles as their filenames.  Currently this is rather limited and these are the only available tags.
* Default output format: This setting is used when converting from the Codex->Convert option in a Windows Explorer context menu.

###Kindle
* Kindle content directory: If you've told Kindle for PC to store downloaded books somewhere other than the default, you can set a different location here by typing in the path or using the Browse button.  Codex uses this directory to find your Kindle books.

###Conversion
* Show conversion complete dialog: If this box is checked, the "Conversion complete" dialog will be shown at the end of all conversion or DRM removal operations.  Otherwise, it will only be shown if errors occur.  The box is checked by default.
* Remove smart punctuation from converted files: Many commercial eBooks contain curly quotes and other so-called smart punctuation.  If you use a braille display, these symbols can be a distraction or take up multiple cells.  Uncheck this box to have smart punctuation replaced with more standard characters.  This option isn't enabled by default.
* Replace unicode characters with their ASCII equivalents: This option isn't recommended for most users.
* Extra options to pass to calibre ebook-convert command: Use this field to pass any extra command line arguments, such as custom search/replace data, to calibre's ebook-convert tool.  A full list of such options is available on [this page](http://manual.calibre-ebook.com/generated/en/ebook-convert.html).  Options shouldn't be enclosed in quotes, but you are responsible for quoting any data within an argument (e.g. strings containing spaces).

##Help and feedback
If you have questions, feature suggestions or are experiencing a problem, feel free to get in touch.  There are email and Twitter details on my [home page](http://jscholes.net).  If using Twitter, you will be able to send me direct messages even if I'm not following you, but unless you have the same feature enabled in your Twitter settings, you'll need to follow me if you want a reply.

If you happen to have a GitHub account, filing issue reports there would be most welcome.  The project's URL is [jscholes/codex](http://github.com/jscholes/codex).

When reporting problems, whether it be via Twitter, email or on GitHub, it would be really helpful if you included your Codex log file.  You can find this by selecting "Open Codex configuration directory" from Codex's Help menu.  In the folder that opens, find the file codex2.log and either attach it to an email, include it with your GitHub issue report, or place it in a publically-accessible location and provide a link (e.g. your Dropbox Public folder).