# RSS reader
RSS 2.0 reader is a command-line utility which receives RSS URL and prints results in human-readable
format.

[The source for this project is available here](https://github.com/iBotMan/rss_reader).


### Installation
$ pip install rss_reader_BotMan

### Usage
$ rss_reader (-h | --help)

    Show help message and exit

$ rss_reader <RSS-SOURCE-LINK>

    Print rss feeds in human-readable format

$ rss_reader --version

    Print version info

$ rss_reader --json

    Print result as JSON in stdout

$ rss_reader.py --verbose

    Outputs verbose status messages
    
$ rss_reader.py --limit LIMIT

    Limit news topics, if this parameter provided
    
$ rss_reader.py --date DATE

    Gets a date in %Y%m%d format. Print news from the specified date
    and source (<RSS-SOURCE-LINK>), if it specified

$ rss_reader.py --to-pdf PATH_TO_PDF

    Gets file path. Convert news to pdf and save them to pdf file on the specified path

$ rss_reader.py --to-html PATH_TO_HTML

    Gets file path. Convert news to html and save them to html file on the specified path

### Storage
All the pieces of news received from the source are saved to the SQLite database.
DBConnector module is used for this. It saves object Item to SQLite database.