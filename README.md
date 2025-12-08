


# Create DataLumos projects from csv file


## [**PLEASE NOTE: The script doesn't work anymore, because the it is detected by the webpage / Cloudflare!**]

Script to automatically fill in the DataLumos forms from a csv file (exported spreadsheet), and upload the data files.<br>
Login, checking and publishing is done manually to avoid errors.<br>
It allows adding many data projects to DataLumos in one go.


## How it works:
You prepare the spreadsheet with the metadata, save it as csv file, then run the script and log in manually in the browser. Then the script fills in the data and uploads the files automatically.
After that, you manually check and publish the project.
- Prepare the csv file: Fill in your metadata etc. in the template spreadsheet, then save it as a csv file. (For details to the template, see further below).
- Prepare the code:
The path of the csv file has to be set before starting the script, the path to the folder with the data files too.
Also, the rows to be processed have to be set (start_row and end_row) - counting starts at 1 and doesn't include the column names row.
- Run the script.
- Log in manually in the browser.

While the script is running, you can work normally on your computer, and even on the internet on a separate browser window.<br>
But don't click in the automated browser while the script is running!<br>


It uses Firefox as browser, so Firefox has to be installed on the computer.<br>

There is no error handling. But the browser remains open even if the script crashes, so the inputs could be checked and/or completed manually.


### About the template spreadsheet:
- The black column names are the ones that are processed by the code (I added the red columns for my own use).
- The names of the columns that are processed in the script cannot be changed (or the code has to be changed too), but they can be left empty if not needed.
Other columns can be added (but will be ignored by the code), and the order of the columns doesn't matter (they can be arranged as you work best).
- The script works for different datastes, but the column names of the template are adapted for the HIFLD Open datasets (The numbers in the column rows relate to the steps
of the instruction ("HIFLD Open to DataLumos Workflow", https://docs.google.com/document/d/12rZAhiOeqFzRsE6HxQIZRs7Ts8JSyQ9up25aCnHS9p0/edit ), and the first content line in the spreadsheet contains the details that are always the same for the HIFLD data (they have a grey background). This row is only for convenience, I copy it when I begin the work on a new HIFLD dataset. It must not be included in the
selection of the rows that are proceeded by the code, and this row can be deleted in the spreadsheet/csv, if not needed).
- The "path" column is the folder name for the folder where the data files are located, and can be identical to the one in the inventory sheet (for example: .\epa-facilities), but can also be written without .\ at the beginning. It also doesn't matter if the path is in linux or windows format, both / and \ can be used. 
- the keywords have to be separated by commas in the spreadsheet cell. They can be written with quotation marks or not, and they can optionally be between square brackets.

## Benefits:
- it's easier to fill in the data in a spreadsheet than in the forms of DataLumos (for example the keywords). And you simply can copy-paste the details that stay the same. 
- you can process more than one data project at once with the csv file; the script adds the projects to the workspace. You can check and publish them later.
- when the site is loading slow, you don't need to wait for every single input to be processed while you stare at the "busy" icon ;) 

## Installation

[Firefox][] is a requirement.

Selenium does the heavy lifting for the script. But before installing that, you may
want to create a virtual environment.

```bash
python3 -m venv env
source ./env/bin/activate
```

If you do this, remember to source this virtual environment every time you work
here. Or consider setting up [direnv][] as a convenient way to automatically
source this environment whenever you're in this directory. The provided `.envrc`
assumes your virtual environment is in `env`.

_Now_ you're ready to install your requirements.

```bash
pip3 install -r requirements.txt
```

[Firefox]: https://www.firefox.com/
[direnv]: https://direnv.net/

<br>
<br>

----------------------
Thanks to sefk for his contributions.