import os
import sys
import sqlite3
import operator
from collections import OrderedDict
import matplotlib.pyplot as plt
import shutil


def get_chrome_history_path():
    """Return the path to Chrome's default profile History file for the current OS."""
    home = os.path.expanduser('~')
    if sys.platform.startswith('win'):
        return os.path.join(home, 'AppData', 'Local', 'Google', 'Chrome',
                             'User Data', 'Default', 'History')
    elif sys.platform == 'darwin':
        return os.path.join(home, 'Library', 'Application Support', 'Google',
                             'Chrome', 'Default', 'History')
    else:  # assume Linux
        return os.path.join(home, '.config', 'google-chrome', 'Default', 'History')


def get_temp_dir():
    """Return a writable temp directory for the current OS."""
    if sys.platform.startswith('win'):
        return os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp')
    else:
        import tempfile
        return tempfile.gettempdir()


def parse(url):
    """Extract the bare domain from a URL."""
    try:
        parsed_url_components = url.split('//')
        sublevel_split = parsed_url_components[1].split('/', 1)
        domain = sublevel_split[0].replace("www.", "")
        return domain
    except IndexError:
        print("URL format error! url = {}".format(url))
        return None


def top_n(results, n):
    """Return the top n items from an already-sorted OrderedDict."""
    return OrderedDict(list(results.items())[:n])


def analyze(results):
    print("[.] {} unique sites found".format(len(results)))
    while True:
        prompt = input(
            "[.] Type <c> to print, <p> to plot, or <s> to save full list to CSV\n[>] "
        )
        if prompt.lower() == "c":
            n_str = input("[.] How many top sites to show? (blank = all) ")
            data = results if not n_str.strip() else top_n(results, int(n_str))
            for site, count in data.items():
                print(site, count)
            break
        elif prompt.lower() == "p":
            n_str = input("[.] How many top sites to plot? (default 20) ")
            n = int(n_str) if n_str.strip() else 20
            data = top_n(results, n)
            # horizontal bars, reversed so the biggest is on top
            sites = list(reversed(list(data.keys())))
            counts = list(reversed(list(data.values())))
            plt.figure(figsize=(10, max(4, len(sites) * 0.35)))
            plt.barh(range(len(sites)), counts)
            plt.yticks(range(len(sites)), sites)
            plt.xlabel("Visit count")
            plt.title("Top {} sites by visit count".format(len(sites)))
            plt.tight_layout()
            plt.show()
            break
        elif prompt.lower() == "s":
            import csv
            out_path = "history_by_site.csv"
            with open(out_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["site", "count"])
                for site, count in results.items():
                    writer.writerow([site, count])
            print("[.] Saved full list ({} sites) to {}".format(len(results), out_path))
            break
        else:
            print("[.] Uh?")


def main():
    data_path = get_chrome_history_path()
    temp_path = get_temp_dir()

    if not os.path.exists(data_path):
        print("[!] Could not find Chrome history at: {}".format(data_path))
        sys.exit(1)

    # create a copy of the history database in temp (Chrome locks the original while running)
    history_db = os.path.join(temp_path, 'History.db')
    shutil.copyfile(data_path, history_db)

    # connect to the copy of the history database
    conn = sqlite3.connect(history_db)
    cursor = conn.cursor()

    try:
        select_statement = "SELECT urls.url, urls.visit_count FROM urls, visits WHERE urls.id = visits.url;"
        cursor.execute(select_statement)
    except sqlite3.OperationalError:
        print("[!] The database is locked! Please exit Chrome and run the script again.")
        sys.exit(1)

    results = cursor.fetchall()
    conn.close()

    sites_count = {}
    for url, count in results:
        domain = parse(url)
        if domain is None:
            continue
        sites_count[domain] = sites_count.get(domain, 0) + 1

    sites_count_sorted = OrderedDict(
        sorted(sites_count.items(), key=operator.itemgetter(1), reverse=True)
    )

    analyze(sites_count_sorted)


if __name__ == '__main__':
    main()
