import os
import sys
import shutil
import fileinput
import webbrowser
import click
import fileinput

cwd = os.getcwd()

@click.group()
def cli():
    """Blended: Static Website Generator"""

@cli.command('init', short_help='Initiate a new website')
def init():
    """Initiates a new website"""
    print("Blended: Static Website Generator -\n")
    wname = raw_input("Website Name: ")
    wdesc = raw_input("Website Description: ")
    wlic = raw_input("Website License: ")
    aname = raw_input("Author(s) Name(s): ")
    wlan = raw_input("Website Language: ")

    templ_dir = os.path.join(cwd, "templates")
    if not os.path.exists(templ_dir):
        os.makedirs(templ_dir)

    cont_dir = os.path.join(cwd, "content")
    if not os.path.exists(cont_dir):
        os.makedirs(cont_dir)

    build_dir = os.path.join(cwd, "build")
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    conf_file_dir = os.path.join(cwd, "conf.py")
    conf_file = open(conf_file_dir, "w")
    conf_file.write('# Configuration is atuomatically generated by Blended, feel free to edit any values\n\n')
    conf_file.write('website_name = "'+wname+'"\n')
    conf_file.write('website_description = "'+wdesc+'"\n')
    conf_file.write('website_license = "'+wlic+'"\n')
    conf_file.write('author_name = "'+aname+'"\n')
    conf_file.write('website_language = "'+wlan+'"\n')
    conf_file.write('\n')
    conf_file.close()
    
    print("\nThe required files for your website have been generated.")

@cli.command('purge', short_help='Purge the Blended files')
def purge():
    """Removes all files generated by Blended"""
    print("Purging the Blended files!")

    templ_dir = os.path.join(cwd, "templates")
    if os.path.exists(templ_dir):
        shutil.rmtree(templ_dir)

    cont_dir = os.path.join(cwd, "content")
    if os.path.exists(cont_dir):
        shutil.rmtree(cont_dir)

    build_dir = os.path.join(cwd, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    
    conf_file_dir = os.path.join(cwd, "conf.py")
    if os.path.exists(conf_file_dir):
        os.remove(conf_file_dir)
    
    conf2_file_dir = os.path.join(cwd, "conf.pyc")
    if os.path.exists(conf2_file_dir):
        os.remove(conf2_file_dir)

@cli.command('build', short_help='Build the Blended files into a website')
def build():
    """Blends the generated files and outputs a html website"""

    conf_file_dir = os.path.join(cwd, "conf.py")
    if not os.path.exists(conf_file_dir):
        sys.exit("There dosen't seem to be a configuration file. Have you run the init command?")
    else:
        sys.path.insert(0, cwd)
        from conf import website_name, website_description, author_name, website_language
    
    print("Building your Blended files into a website!")

    build_dir = os.path.join(cwd, "build")
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    header_file = open(os.path.join(cwd, "templates", "header.html"), "r")
    footer_file = open(os.path.join(cwd, "templates", "footer.html"), "r")

    home_working_file = open(os.path.join(cwd, "build", "index.html"), "w")

    home_working_file.write(header_file.read())

    home_templ_dir = os.path.join(cwd, "templates", "home_page.html")
    if os.path.exists(home_templ_dir):
        home_templ_file = open(home_templ_dir, "r")
        home_working_file.write(home_templ_file.read())

    home_working_file.write(footer_file.read())
    
    home_working_file.close()
    
    for filename in os.listdir(os.path.join(cwd, "content")):
        header_file = open(os.path.join(cwd, "templates", "header.html"), "r")
        footer_file = open(os.path.join(cwd, "templates", "footer.html"), "r")
        currents_working_file = open(os.path.join(cwd, "build", filename), "w")

        # Write the header
        currents_working_file.write(header_file.read())

        # Get the actual stuff we want to put on the page
        text_content = open(os.path.join(cwd, "content", filename), "r")
        text_cont1 = text_content.read()

        # Write the text content into the content template and onto the built file
        content_templ_dir = os.path.join(cwd, "templates", "content_page.html")
        if os.path.exists(content_templ_dir):
            content_templ_file = open(content_templ_dir, "r")
            content_templ_file1 = content_templ_file.read()
            content_templ_file2 = content_templ_file1.replace("{page_content}", text_cont1)
            currents_working_file.write(content_templ_file2)

        # Write the footer
        currents_working_file.write(footer_file.read())

        # Close the built file
        currents_working_file.close()
    
    # Replace global variables such as site name and language
    for filename in os.listdir(os.path.join(cwd, "build")):
        for line in fileinput.input(os.path.join(cwd, "build", filename), inplace=1):
            line = line.replace("{website_name}", website_name)
            line = line.replace("{website_language}", website_language)
            print line.rstrip('\n')
        fileinput.close()

    # Copy the asset folder to the build folder
    shutil.copytree(os.path.join(cwd, "templates", "assets"), os.path.join(cwd, "build", "assets"))

    print("The files are built! You can find them in the build/ directory. Run the view command to see what you have created in a web browser.")

@cli.command('view', short_help='View the finished Blended website')
def view():
    """Opens the built index.html file in a web browser"""

    webbrowser.open('file://' + os.path.realpath(os.path.join(cwd, "build", "index.html")))

if __name__ == '__main__':
    cli()
