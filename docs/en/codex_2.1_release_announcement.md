It's taken a bit longer than expected, but today I'm really happy to be announcing the release of Codex version 2.1.  It brings with it a whole host of new features and improvements to make eBooks even more accessible and available, but before I tell you more about that a thank you is most definitely in order.

The response to the first public release of Codex was absolutely phenomenal.  More people than I could have ever hoped for helped out by retweeting, sharing on social media, recommending the software to their friends, talking about it on their podcasts or blogs, and generally spreading the word in whatever way they could think of.  As some of you may know, Codex is my first real software project, so to see people enjoying and getting so much from it is the best reward I could've asked for.  The feelings were pretty indescribable so I will just say, thank you.  Whether you wrote or spoke about Codex, or you just sent it to a friend or colleague, I really appreciate it and I hope that this version will make a difference to even more people.

I also need to thank everybody who provided feedback in the form of bug reports, feature suggestions and encouragement when they were able to read Kindle books for the first time or after they'd successfully converted hundreds of books in one go.  Receiving feedback is great, so whether it's good, bad or somewhere inbetween, feel free to share.

Finally, if you donated to the project, or helped out as a beta tester, you're a big part of the reason this version is being exposed to the public today and I hope that its improvements inspire you to do the same again.

Now, onto the new features!

## Finding your Kindle books: Now much less of a headache
One of my primary goals for this release was to make it much easier for people to find their Kindle files once they'd purchased and downloaded them.  I'm really glad to say that with version 2.1, sorting a bunch of obscurely-named files by their last modified date is now a thing of the past.

In the main window, you'll now find a Tools menu housing two new options.

### Find Kindle file from Amazon URL
This dialog lets you provide the URL to an eBook product page on Amazon and have the corresponding file, if it exists on your computer and Codex can find it, automatically added to the Files list for conversion or DRM removal.  This is useful if, for example, you bought a Kindle book a long time ago and don't want to go hunting through your library to find it.  Just search for it on the Amazon website, copy the URL, paste it into this dialog and hit OK.

Note: If you bought the book a very long time ago, or on a different computer, Kindle for PC may not have downloaded it and you might have to do so manually.

### Browse downloaded Kindle books
This is, to my mind, the best new addition to Codex and I hope you'll agree.  This dialog retrieves the title and author from all of your downloaded Kindle files, presenting them to you in an easy-to-navigate list.  You can:

* use first letter navigation to jump through books whose author starts with a certain letter;
* Select multiple books using Shift plus the Arrow keys; and
* Press Enter when you're finished to add your selected book(s) to the Files list for conversion or DRM removal.

In addition, the list of books is sorted by the last modified time of the underlying files, so a book you've just purchased will be right at the top.

It's my hope that these two new features will make your experience of buying and reading Kindle books easier than ever before.  If you have feedback about how they're working for you, or suggestions on how you think they could be improved, don't hesitate to get in touch!

Note: If you've told Kindle for PC to store downloaded books in a folder other than the default, you'll need to also tell Codex about this change.  You can use the new "Kindle content directory" setting in the Options dialog to do so.

## Other changes
### Clipboard: Copy and paste
You can now copy supported eBooks from Windows Explorer and other applications directly into the Codex Files list.  Likewise, after a successful conversion or DRM removal, you may select one or multiple files and press Ctrl+C to copy them directly from the conversion complete dialog.

### New options
The Options dialog has a few additions:

* Kindle content directory: Use this setting to tell Codex where to find your downloaded Kindle files.
* Show conversion complete dialog: Uncheck this option to avoid showing the Conversion complete dialog when all files were converted successfully.
* Remove smart punctuation from converted files: Many commercial eBooks contain curly quotes and other so-called smart punctuation.  If you use a braille display, these symbols can be a distraction or take up multiple cells.  Uncheck this box to have smart punctuation replaced with more standard characters.
* Replace unicode characters with their ASCII equivalents (not recommended for most users).
* Extra options to pass to calibre ebook-convert command: Use this field to pass any extra command line arguments, such as custom search/replace data, to calibre's ebook-convert tool.  A full list of such options is available on [this page](http://manual.calibre-ebook.com/generated/en/ebook-convert.html).  Options shouldn't be enclosed in quotes, but you are responsible for quoting any data within an argument (e.g. strings containing spaces).

### User interface changes
* Pressing Enter in most dialogs will now perform an appropriate default action, speeding up some operations and offering a more intuitive user experience.  For example, in the Options dialog, press Enter to activate the OK button or in the Conversion complete dialog, press Enter on any file to open it.
* The Conversion complete dialog now offers the option to open a book's containing folder.
* Two new items have been added to the Help menu to allow you to easily open the Codex project web page or your configuration directory.

## Downloading and donations
The latest version can always be retrieved from the [project page](http://jscholes.net/project/codex).  Since releasing version 2.0, I've updated the donation form to allow selection  of your local currency, and all donations are very greatfully received and come with access to new beta releases as an added bonus.

I hope you enjoy this new version of Codex and please, do share it with anybody who you think would benefit from the increased access to books that it provides.