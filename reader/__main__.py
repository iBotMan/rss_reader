""" Module = entry_points """

from reader.functions import Parser
from datetime import datetime
import time
import argparse


def init_arguments():
    """ Function to get command line arguments. """

    ap = argparse.ArgumentParser(description="Pure Python command-line RSS reader.", add_help=True)
    ap.add_argument("--date", type=lambda str_date: datetime.strptime(str_date, '%Y%m%d').date(),
                    help="Gets a date in %%Y%%m%%d format. Print news from the specified date.")
    ap.add_argument("--to-html", type=str,
                    help="Gets file path. Convert news to html and save them to html file.")
    ap.add_argument("--to-pdf", type=str,
                    help="Gets file path. Convert news to pdf and save them to pdf file.")
    ap.add_argument("--version", action="store_true", help="Print version info")
    ap.add_argument("--json", action="store_true", help="Print result as JSON in stdout")
    ap.add_argument("--colorize", action="store_true", help="Print the result in colorized mode in stdout.")
    ap.add_argument("--verbose", action="store_true", help="Outputs verbose status messages")
    ap.add_argument("--limit", type=int, help="Limit news topics if this parameter provided")
    ap.add_argument("source", type=str, nargs="?", help="RSS URL")
    return ap.parse_args()


def main():
    """Receives the elements passed by the user and runs them for execution."""

    start = time.time()
    arguments = init_arguments()
    parser = Parser(arguments.source, arguments.date, arguments.limit, arguments.verbose)
    parser.logger.info(f'Start program with: {arguments}')

    if arguments.version:
        print(parser.version)
    else:
        items_list = parser.get_items()
        if len(items_list) == 0:
            print('The news list is empty')
        else:
            if arguments.to_pdf:
                pdf_file = parser.create_and_fill_pdf_file(arguments.to_pdf, items_list)
                print(f'PDF file was saved: {pdf_file}')

            if arguments.to_html:
                html_file = parser.create_and_fill_html_file(arguments.to_html, items_list)
                print(f'HTML file was saved: {html_file}')

            for item in items_list:
                if arguments.colorize:
                    item.colorized(arguments.json)
                else:
                    item.print_news(arguments.json)

    parser.logger.info(f'Took time : {time.time() - start}')
    parser.logger.info(2 * '\n')


if __name__ == "__main__":
    main()
