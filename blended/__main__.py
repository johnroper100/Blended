import os
import os.path
import sys
import shutil
from shutil import copyfile
import fileinput
import webbrowser
import fileinput
import datetime
import click
from random import randint
import pkg_resources
import time
from ftplib import FTP, error_perm
import markdown
import textile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Very important, get the directory that the user wants run commands in
cwd = os.getcwd()

try:
    app_version = pkg_resources.require("blended")[0].version
except:
    app_version = "NOTSET"
    print("WARNING: app_version not set.\n")


@click.group()
def cli():
    """Blended: Static Website Generator"""


@cli.command('version', short_help='Show which version of Blended you are running.')
def version():
    """Prints Blended's current version"""

    print("You are running Blended v"+app_version)


@cli.command('init', short_help='Initiate a new website')
def init():
    """Initiates a new website"""

    print("Blended: Static Website Generator -\n")

    config_file_dir1 = os.path.join(cwd, "config.py")
    if os.path.exists(config_file_dir1):
        print("Making a backup of your config file!")
        config_file_dir2 = os.path.join(cwd, "config.py.oldbak")
        copyfile(config_file_dir1, config_file_dir2)

    if (sys.version_info > (3, 0)):
        wname = input("Website Name: ")
        wdesc = input("Website Description: ")
        wlan = input("Website Language: ")
        wlic = input("Website License: ")
        aname = input("Author(s) Name(s): ")
    else:
        wname = raw_input("Website Name: ")
        wdesc = raw_input("Website Description: ")
        wlan = raw_input("Website Language: ")
        wlic = raw_input("Website License: ")
        aname = raw_input("Author(s) Name(s): ")

    # Create the templates folder
    templ_dir = os.path.join(cwd, "templates")
    if not os.path.exists(templ_dir):
        os.makedirs(templ_dir)

    # Create the content folder
    cont_dir = os.path.join(cwd, "content")
    if not os.path.exists(cont_dir):
        os.makedirs(cont_dir)

    # Populate the configuration file
    config_file_dir = os.path.join(cwd, "config.py")
    config_file = open(config_file_dir, "w")
    config_file.write('blended_version = '+app_version+'\n')
    config_file.write('\n')
    config_file.write('# Configuration is automatically generated by Blended, feel free to edit any values below')
    config_file.write('\n')
    config_file.write('website_name = "'+wname+'"\n')
    config_file.write('website_description = "'+wdesc+'"\n')
    config_file.write('website_description_long = "" # Use for things like author bio on a blog\n')
    config_file.write('website_license = "'+wlic+'"\n')
    config_file.write('author_name = "'+aname+'"\n')
    config_file.write('website_language = "'+wlan+'"\n')
    config_file.write('home_page_list = "no"\n')
    config_file.write('\n')
    config_file.write('# The following values are used for FTP uploads')
    config_file.write('\n')
    config_file.write('ftp_server = "localhost"\n')
    config_file.write('ftp_username = "user"\n')
    config_file.write('ftp_password = "pass"\n')
    config_file.write('ftp_port = 21\n')
    config_file.write('ftp_upload_path = "public_html/myWebsite"\n')
    config_file.close()

    print("\nThe required files for your website have been generated.")


def placeFiles(ftp, path):
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            print("STOR", name, localpath)
            ftp.storbinary('STOR ' + name, open(localpath, 'rb'))
        elif os.path.isdir(localpath):
            print("MKD", name)

            try:
                ftp.mkd(name)

            # ignore "directory already exists"
            except error_perm as e:
                if not e.args[0].startswith('550'):
                    raise

            print("CWD", name)
            ftp.cwd(name)
            placeFiles(ftp, localpath)
            print("CWD", "..")
            ftp.cwd("..")


@cli.command('ftp', short_help='Upload the files via ftp')
def ftp():
    """Upload the built website to FTP"""
    print("Uploading the files in the 'build' directory!\n")

    # Make sure there is actually a configuration file
    config_file_dir = os.path.join(cwd, "config.py")
    if not os.path.exists(config_file_dir):
        sys.exit("There dosen't seem to be a configuration file. Have you run the init command?")
    else:
        sys.path.insert(0, cwd)
        try:
            from config import ftp_server, ftp_username, ftp_password, ftp_port, ftp_upload_path
        except:
            sys.exit("The FTP settings could not be found. Maybe your config file is too old. Re-run 'blended init' to fix it.")

    server = ftp_server
    username = ftp_username
    password = ftp_password
    port = ftp_port

    ftp = FTP()
    ftp.connect(server, port)
    ftp.login(username, password)
    filenameCV = os.path.join(cwd, "build")

    try:
        ftp.cwd(ftp_upload_path)
        placeFiles(ftp, filenameCV)
    except:
        ftp.quit()
        sys.exit("Files not able to be uploaded! Are you sure the directory exists?")

    ftp.quit()

    print("\nFTP Done!")


@cli.command('clean', short_help='Remove the build folder')
def clean():
    """Removes all built files"""
    print("Removing the built files!")

    # Remove the  build folder
    build_dir = os.path.join(cwd, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)


@cli.command('purge', short_help='Purge all the files created by Blended')
def purge():
    """Removes all files generated by Blended"""
    print("Purging the Blended files!")

    # Remove the templates folder
    templ_dir = os.path.join(cwd, "templates")
    if os.path.exists(templ_dir):
        shutil.rmtree(templ_dir)

    # Remove the content folder
    cont_dir = os.path.join(cwd, "content")
    if os.path.exists(cont_dir):
        shutil.rmtree(cont_dir)

    # Remove the  build folder
    build_dir = os.path.join(cwd, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    # Remove config.py
    config_file_dir = os.path.join(cwd, "config.py")
    if os.path.exists(config_file_dir):
        os.remove(config_file_dir)

    # Remove config.pyc
    config2_file_dir = os.path.join(cwd, "config.pyc")
    if os.path.exists(config2_file_dir):
        os.remove(config2_file_dir)

    # Remove config.py
    config3_file_dir = os.path.join(cwd, "config.py.oldbak")
    if os.path.exists(config3_file_dir):
        os.remove(config3_file_dir)


def build_files():
    # Make sure there is actually a configuration file
    config_file_dir = os.path.join(cwd, "config.py")
    if not os.path.exists(config_file_dir):
        sys.exit("There dosen't seem to be a configuration file. Have you run the init command?")
    else:
        sys.path.insert(0, cwd)
        try:
            from config import website_name, website_description, website_description_long, website_license, author_name, website_language, home_page_list, blended_version
        except:
            sys.exit("Some of the configuration values could not be found! Maybe your config.py is too old. Run 'blended init' to fix.")

    # Create the build folder
    build_dir = os.path.join(cwd, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        os.makedirs(build_dir)
    else:
        os.makedirs(build_dir)

    # Make sure there is actually a header template file
    header_file_dir = os.path.join(cwd, "templates", "header.html")
    if not os.path.exists(header_file_dir):
        sys.exit("There dosen't seem to be a header template file. You need one to generate.")

    # Make sure there is actually a footer template file
    footer_file_dir = os.path.join(cwd, "templates", "footer.html")
    if not os.path.exists(footer_file_dir):
        sys.exit("There dosen't seem to be a footer template file. You need one to generate.")

    # Open the header and footer files for reading
    header_file = open(header_file_dir, "r")
    footer_file = open(footer_file_dir, "r")

    # Create the html page listing
    page_list = '<ul class="page-list">\n'
    for filename in os.listdir(os.path.join(cwd, "content")):
        file_modified = str(time.ctime(os.path.getmtime(os.path.join(cwd, "content", filename))))
        if ".html" in filename:
            newFilename = filename
        elif ".md" in filename:
            newFilename = filename.replace(".md", ".html")
        elif ".tile" in filename:
            newFilename = filename.replace(".tile", ".html")
        elif ".txt" in filename:
            newFilename = filename.replace(".txt", ".html")
        newFilename2 = filename.replace(".html", "")
        newFilename2 = newFilename2.replace(".md", "")
        newFilename2 = newFilename2.replace(".txt", "")
        newFilename2 = newFilename2.replace(".tile", "")
        newFilename2 = newFilename2.replace("index", "home")
        newFilename2 = newFilename2.replace("-", " ")
        newFilename2 = newFilename2.replace("_", " ")
        newFilename2 = newFilename2.title()
        page_list = page_list + '<li class="page-list-item"><a href="'+newFilename+'">'+newFilename2+'</a><span class="page-list-item-time"> - '+file_modified+'</span></li>\n'
    page_list = page_list + '</ul>'

    if home_page_list == "yes":
        # Open the home page file (index.html) for writing
        home_working_file = open(os.path.join(cwd, "build", "index.html"), "w")

        home_working_file.write(header_file.read())

        # Make sure there is actually a home page template file
        home_templ_dir = os.path.join(cwd, "templates", "home_page.html")
        if os.path.exists(home_templ_dir):
            home_templ_file = open(home_templ_dir, "r")
            home_working_file.write(home_templ_file.read())
        else:
            print("No home page template file found. Writing page list to index.html")
            home_working_file.write(page_list)

        home_working_file.write(footer_file.read())

        home_working_file.close()

    for filename in os.listdir(os.path.join(cwd, "content")):
        header_file = open(header_file_dir, "r")
        footer_file = open(footer_file_dir, "r")
        if ".md" in filename:
            newFilename = filename.replace(".md", ".html")
        elif ".tile" in filename:
            newFilename = filename.replace(".tile", ".html")
        elif ".html" in filename:
            newFilename = filename
        elif ".txt" in filename:
            newFilename = filename.replace(".txt", ".html")
        else:
            print(filename+" is not a valid file type!")

        currents_working_file = open(os.path.join(cwd, "build", newFilename), "w")

        # Write the header
        currents_working_file.write(header_file.read())

        # Get the actual stuff we want to put on the page
        text_content = open(os.path.join(cwd, "content", filename), "r")
        if ".md" in filename:
            text_cont1 = "\n"+markdown.markdown(text_content.read())+"\n"
        elif ".tile" in filename:
            text_cont1 = "\n"+textile.textile(text_content.read())+"\n"
        elif ".html" in filename:
            text_cont1 = text_content.read()
        elif ".txt" in filename:
            text_cont1 = text_content.read()
        else:
            print(filename+" is not a valid file type!")

        # Write the text content into the content template and onto the build file
        content_templ_dir = os.path.join(cwd, "templates", "content_page.html")
        if os.path.exists(content_templ_dir):
            content_templ_file = open(content_templ_dir, "r")
            content_templ_file1 = content_templ_file.read()
            content_templ_file2 = content_templ_file1.replace("{page_content}", text_cont1)
            currents_working_file.write(content_templ_file2)
        else:
            currents_working_file.write(text_cont1)

        # Write the footer to the build file
        currents_working_file.write("\n"+footer_file.read())

        # Close the build file
        currents_working_file.close()

    nav1_dir = os.path.join(cwd, "templates", "nav1.html")
    if os.path.exists(nav1_dir):
        nav1_file = open(nav1_dir, "r")
        nav1_cont = nav1_file.read()
    else:
        nav1_cont = ""

    nav2_dir = os.path.join(cwd, "templates", "nav2.html")
    if os.path.exists(nav2_dir):
        nav2_file = open(nav2_dir, "r")
        nav2_cont = nav2_file.read()
    else:
        nav2_cont = ""

    nav3_dir = os.path.join(cwd, "templates", "nav3.html")
    if os.path.exists(nav3_dir):
        nav3_file = open(nav3_dir, "r")
        nav3_cont = nav3_file.read()
    else:
        nav3_cont = ""

    nav4_dir = os.path.join(cwd, "templates", "nav4.html")
    if os.path.exists(nav4_dir):
        nav4_file = open(nav4_dir, "r")
        nav4_cont = nav4_file.read()
    else:
        nav4_cont = ""

    nav5_dir = os.path.join(cwd, "templates", "nav5.html")
    if os.path.exists(nav5_dir):
        nav5_file = open(nav5_dir, "r")
        nav5_cont = nav5_file.read()
    else:
        nav5_cont = ""

    nav6_dir = os.path.join(cwd, "templates", "nav6.html")
    if os.path.exists(nav6_dir):
        nav6_file = open(nav6_dir, "r")
        nav6_cont = nav6_file.read()
    else:
        nav6_cont = ""

    # Replace global variables such as site name and language
    for filename in os.listdir(os.path.join(cwd, "build")):
        newFilename = filename.replace(".html", "")
        newFilename = newFilename.replace("index", "home")
        newFilename = newFilename.replace("-", " ")
        newFilename = newFilename.replace("_", " ")
        newFilename = newFilename.title()
        page_file = filename.replace(".html", "")
        file_modified = str(time.ctime(os.path.getmtime(os.path.join(cwd, "build", filename))))
        blended_version_message = "Built with Blended v"+str(app_version)
        for line in fileinput.input(os.path.join(cwd, "build", filename), inplace=1):
            line = line.replace("{nav1}", nav1_cont)
            line = line.replace("{nav2}", nav2_cont)
            line = line.replace("{nav3}", nav3_cont)
            line = line.replace("{nav4}", nav4_cont)
            line = line.replace("{nav5}", nav5_cont)
            line = line.replace("{nav6}", nav6_cont)
            line = line.replace("{website_name}", website_name)
            line = line.replace("{website_description}", website_description)
            line = line.replace("{website_description_long}", website_description_long)
            line = line.replace("{website_license}", website_license)
            line = line.replace("{website_language}", website_language)
            line = line.replace("{author_name}", author_name)
            line = line.replace("{random_number}", str(randint(0, 100000000)))
            line = line.replace("{build_date}", str(datetime.datetime.now().date()))
            line = line.replace("{build_time}", str(datetime.datetime.now().time()))
            line = line.replace("{build_datetime}", str(datetime.datetime.now()))
            line = line.replace("{page_list}", page_list)
            line = line.replace("{page_name}", newFilename)
            line = line.replace("{page_filename}", page_file)
            line = line.replace("{page_file}", filename)
            line = line.replace("{page_time}", file_modified)
            line = line.replace("{blended_version}", str(app_version))
            line = line.replace("{blended_version_message}", blended_version_message)
            print(line.rstrip('\n'))
        fileinput.close()

    # Copy the asset folder to the build folder
    if os.path.exists(os.path.join(cwd, "templates", "assets")):
        shutil.copytree(os.path.join(cwd, "templates", "assets"), os.path.join(cwd, "build", "assets"))


@cli.command('build', short_help='Build the Blended files into a website')
def build():
    """Blends the generated files and outputs a html website"""

    print("Building your Blended files into a website!")

    build_files()

    print("The files are built! You can find them in the build/ directory. Run the view command to see what you have created in a web browser.")


class Watcher:
    DIRECTORY_TO_WATCH = os.path.join(cwd, "content")

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        threads = []
        paths = [os.path.join(cwd, "content"), os.path.join(cwd, "templates")]

        for i in paths:
            targetPath = str(i)
            self.observer.schedule(event_handler, targetPath, recursive=True)
            threads.append(self.observer)

        self.observer.start()

        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("\nObserver stopped.")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            build_files()
            print("%s created" % event.src_path)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            build_files()
            print("%s modified" % event.src_path)

        elif event.event_type == 'deleted':
            # Taken any action here when a file is modified.
            build_files()
            print("%s deleted" % event.src_path)


@cli.command('interactive', short_help='Build the Blended files into a website on each file change')
def interactive():
    """Blends the generated files and outputs a html website on file change"""

    print("Building your Blended files into a website!")

    build_files()

    print("Watching the content and templates directories for changes, press CTRL+C to stop...\n")

    w = Watcher()
    w.run()


@cli.command('view', short_help='View the finished Blended website')
def view():
    """Opens the built index.html file in a web browser"""

    index_path = os.path.realpath(os.path.join(cwd, "build", "index.html"))
    if os.path.exists(index_path):
        webbrowser.open('file://' + index_path)
    else:
        print("The index.html file could not be found! Have you deleted it or have you built with home_page_list set to 'no' in config.py?")

if __name__ == '__main__':
    cli()
