A few years ago, I wrote a tutorial which guided people through the installation and configuration of software for the purposes of gaining access to books purchased from the Amazon Kindle Store.  The guide proved popular, but it required heavy use of the command line, making it unsuitable and daunting for quite a lot of people, not to mention that it was an absolute nightmare to troubleshoot if anything went wrong.  Which it frequently did.

Subsequently, in 2014, I started to develop a small prototype application to make the process easier and more intuitive, not only for people wanting to read Kindle eBooks, but also for me when people needed help.  I named it Codex, a word used from the 16th century onwards to denote, now ancient, manuscripts in book form.  In the last couple of months, I've finally rewritten that prototype to include the functionality I wanted it to have from the start, and the first release of Codex 2.0 is ready for download.

In this guide, I'll show you just how easy it is to gain access to your purchased Kindle eBooks in any software application or on any device of your choice, using Codex.  The application can process eBooks from many other sources, both DRM-protected and not, but access to the Kindle Store, a marvellous resource for blind readers, was my primary goal back in 2012 and that is what it remains to this day.

## What you'll need
To get started, you'll need three things.  First, an Amazon account, which you probably already have.  Next you'll need to download and install both Codex, which you can get from its [project page](http://jscholes.net/project/codex) and Amazon's Kindle for PC software.  After downloading Codex, run the installer and follow the instructions, making sure to run the program at least once after installation to initialise its settings.  Keep reading for instructions on how to handle Kindle for PC.

### Installing and registering Kindle for PC
Kindle for PC isn't very accessible and even less usable.  I'd love to say that that was changing for the better, but unfortunately things seem to be going in the opposite direction and it is less accessible now than it was this time last year.  However, you'll only need to use it to download your eBooks from Amazon's website which requires almost no user interaction.

Before that, though, it needs to be installed and registered to your Amazon account.  If you've previously used Codex version 1 or followed my older DRM removal guide, you should be able to skip this step.

I recommend downloading the version from [this accessibility page](https://www.amazon.com/gp/help/customer/display.html?nodeId=200596280).  At the moment, it's no more accessible than the standard release of Kindle for PC, but it's my hope that in the future, if Amazon do make accessibility improvements, they'll land in this version first.

After grabbing the installer, run it as normal and wait for the Kindle software to start.  At this point, if you haven't used Kindle on your computer before, you'll see the Registration dialog.  This is where you enter your Amazon account details to authorise your computer to access any books that you buy.  It is also one of the least accessible parts of the application.  To register, do the following:

- Press Tab until you find a drop-down combo box allowing you to choose your regional Amazon site, for example amazon.co.uk.
- Select the appropriate choice in the drop-down, and then press Tab, once.  Your screen reader will probably not say anything other than "pane".
- Type the email address associated with your Amazon account, the same one you use to log in on the Amazon website.
- Press Enter, at which point the software will try to log in, realise you haven't typed a password, and by a happy coincidence will also move your cursor to the right place to type one.  Your screen reader won't give you any speech feedback at all during this process.
- Type your Amazon password and press Enter.

I recommend enabling your screen reader's character echo during this process to avoid making mistakes.  If you do, the Backspace key will delete characters in the dialog's text fields, but you won't hear any speech feedback to indicate which character has been deleted.  If you really get stuck, just close and reopen Kindle for PC.

If your details are correct, you're connected to the Internet and nothing else has gone wrong, your copy of Kindle for PC should now be registered.  If you read the title of the window, it should say something like:

> James's Kindle for PC

That's it.  You're ready to go shopping.  Feel free to close the software at this point.

## Purchasing Kindle books
This process is very similar to buying other types of products on Amazon.  Open up the Amazon website, set the "Search in" combo box to "Kindle Store," and type a search query.  Alternatively you can browse the Kindle Store by genre, find bestsellers or recommendations for you and choose one of those instead.  Once you've found the book you want and opened its product page, locate a combo box labelled "Deliver to:" and ensure that it's set to your newly-registered Kindle for PC.  Then press the "Buy now with 1-Click" button.

You'll be taken to a "Thank you" page, on which is a link to open the Kindle software and download the book automatically.  This is usually a graphic on most Amazon sites, so you can use your screen reader's quick navigation key for locating images (usually G) to locate it. Or just search for the word "refresh".  On Amazon UK, the graphic is labelled:

> home action=refresh

Activate this link, and if you're asked about opening a software application, press OK in any of the dialogs that come up.  Kindle for PC will open and download your book.  You'll receive no audible or spoken feedback that the download process has completed, but for most books it shouldn't take longer than a few minutes at most, and usually a lot shorter than that.  The table showing your downloaded books is relatively accessible, so if you wish, you can check to see whether the book appears there.  You can then close Kindle for PC.

Next, open up your Documents folder and find the "My Kindle Content" subdirectory.  This folder contains all of your Kindle downloads, as well as bookmark files and other information that the Kindle software needs.  The files we're interested in have a .azw extension, but unfortunately they're named using their associated Amazon product ID rather than by title.  The best thing to do is to open up the View menu by pressing Alt+V, expanding the Sort by sub menu and choosing Date modified.  The first .azw file in the folder should then be the most recent book downloaded.

Make sure that you always choose the most recent file with a .azw extension, as Codex can't do anything with any of the other ones.  One of the most important targets on my to-do list is to make this part of the process simpler in a future release.

Once you've found the file you want to convert, press your Applications key or Shift+F10 to open the file's context menu, followed by the letter X to expand the Codex sub menu.  Here, you have three options:

- Convert: Will convert the file to the default format specified in the Codex Options dialog
- Convert to: Offers a menu of supported output formats to choose from
- Remove DRM: Will strip the protection from the book, but leave the original format in tact

Regardless of which option you choose, the processed file will be placed in your Codex output directory, which by default is Documents\eBooks with books organised into author name-based subfolders.  You'll also have the option of opening the file right from within Codex once it's worked its magic.

> ### Tip
> You can also find the Codex sub menu in the context menu of folders, meaning you can convert multiple files at once.  Give it a try!

### Note
If you're using a version of Windows older than Windows 7, Codex will still work, but unfortunately, Windows Explorer integration won't be available.  This is due to changes made by Microsoft in Windows 7 and later.  Until I've implemented a work-around for this, you'll need to use the Codex user interface instead:

- Use the Add files and Add folder buttons in Codex to load the files you want to convert
- Select your desired output format from the combo box
- Press either the Convert or Remove DRM button to start the process

You can use the same steps as above to find the appropriate file for conversion.  Once you've pressed the Convert or Remove DRM button, the process is identical from that point forward to that available through Windows Explorer.

## All done!
If nothing went wrong during the conversion process, you should have an unprotected eBook in the format of your choice which you can open in any software application or copy to any device.  If you have questions that this guide didn't answer, have a read of the Codex documentation which is included with the program and available through the Help menu.  If you still don't have the information you're looking for, or something did go wrong, feel free to get in touch using the contact details available on my home page.

Enjoy your reading!