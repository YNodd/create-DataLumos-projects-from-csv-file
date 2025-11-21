

"""
Script to automatically fill in the DataLumos fields from a csv file (exported spreadsheet), and upload the files.
Login, checking and publishing is done manually to avoid errors.

The path of the csv file has to be set before starting the script, the path to the folder with the data files too.
Also, the rows to be processed have to be set (start_row and end_row) - counting starts at 1 and doesn't include the column names row.

There is no error handling. But the browser remains open even if the script crashes, so the inputs could be checked and/or completed manually.
"""



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.keys import Keys
from time import sleep
import csv
import traceback
import os


#########################################################

# TODO: VARIABLES TO SET:
start_row = 2 # WITHOUT COUNTING THE COLUMNS ROW!  (and beginning at 1)
end_row = 2 # (to process only one row, set start_row and end_row to the same number)
csv_file_path = "my_current_inputdata.csv"  # or the complete path, for example: "/home/YNodd/PycharmProjects/datalumos/my_current_inputdata.csv"
folder_path_uploadfiles = "/media/YNodd/32 GB/data rescue project/"  # the folder where the upload files are (there, the subfolders for the single data projects are located)
# example: the files are on a USB flash drive, in a folder named "data rescue project", the example path would be: /media/YNodd/32 GB/data rescue project/
#   in there is the folder "national-transit-map-stops" which contains the zip-files and metadata.xml for uploading

#########################################################


url_datalumos = "https://www.datalumos.org/datalumos/workspace"
mydriver = webdriver.Firefox() # firefox must be installed on the computer, or the code should be changed for another browser
mydriver.get(url_datalumos) # start the browser window
sleep(1)


def wait_for_obscuring_elements(current_driver_obj):
    overlays = current_driver_obj.find_elements(By.ID, "busy")  # caution: find_elements, not find_element
    if len(overlays) != 0:  # there is an overlay
        print(f"... (Waiting for overlay to disappear. Overlay(s): {overlays})")
        for overlay in overlays:
            # Wait until the overlay becomes invisible:
            WebDriverWait(current_driver_obj, 360).until(EC.invisibility_of_element_located(overlay))
            sleep(0.5)

def read_csv_line(csv_file, line_to_process):
    # gets the input from the specified line of the csv file, to put it in the datalumos forms.
    with open(csv_file, "r", newline='') as datafile:
        datareader = csv.DictReader(datafile)
        for i, singlerow in enumerate(datareader):
            if i == (line_to_process - 1):  # -1 because i starts counting at 0
                return singlerow  # is already a dictionary

def get_paths_uploadfiles(folderpath):
    # Builds a list with all the single file paths to be uploaded. Takes as argument the path to the parent folder,
    #   where all the data folders are located (for example, the path to the external USB drive).
    mypath = datadict["path"]
    if mypath[0:2] == ".\\" or mypath[0:2] == "./":
        # eliminate the first two characters, the dot and the slash:
        mypath = mypath[2:]
    operatingsystem = os.name
    if operatingsystem == "posix":  # for linux or mac
        mypath = mypath.replace("\\", "/")
        folderpath = folderpath.replace("\\", "/")
    elif operatingsystem == "nt":  # for windows
        mypath = mypath.replace("/", "\\")
        folderpath = folderpath.replace("\\", "/")
    combinedpath = os.path.join(folderpath, mypath)
    #print("combinedpath:", combinedpath)
    uploadfiles_names = os.listdir(combinedpath)
    print("\nFiles that will be uploaded:", uploadfiles_names, "\n")
    # build the complete paths for the files that should be uploaded, by joining the single parts of the path:
    uploadfiles_paths = [os.path.join(combinedpath, filename) for filename in uploadfiles_names]
    return uploadfiles_paths

def drag_and_drop_file(drop_target, path):
    # the function fakes the drag-and-drop that drags a file from the computer into a specific area to upload it.
    # THE COMPLETE CODE OF THIS FUNCTION IS TAKEN FROM STACKOVERFLOW:
    #   https://stackoverflow.com/questions/43382447/python-with-selenium-drag-and-drop-from-file-system-to-webdriver

    # javascript code that will be executed by selenium:
    JS_DROP_FILE = """
        var target = arguments[0],
            offsetX = arguments[1],
            offsetY = arguments[2],
            document = target.ownerDocument || document,
            window = document.defaultView || window;
    
        var input = document.createElement('INPUT');
        input.type = 'file';
        input.onchange = function () {
          var rect = target.getBoundingClientRect(),
              x = rect.left + (offsetX || (rect.width >> 1)),
              y = rect.top + (offsetY || (rect.height >> 1)),
              dataTransfer = { files: this.files };
    
          ['dragenter', 'dragover', 'drop'].forEach(function (name) {
            var evt = document.createEvent('MouseEvent');
            evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
            evt.dataTransfer = dataTransfer;
            target.dispatchEvent(evt);
          });
    
          setTimeout(function () { document.body.removeChild(input); }, 25);
        };
        document.body.appendChild(input);
        return input;
    """
    driver = drop_target.parent
    file_input = driver.execute_script(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(path)



print("\nLog in now (manually) in the browser\n")

print("If you upload from USB device: MAKE SURE THE USB IS PLUGGED IN!\n")

for current_row in range(start_row, end_row + 1):

    new_project_btn = WebDriverWait(mydriver, 360).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn > span:nth-child(3)"))) # .btn > span:nth-child(3)
    #print("button found")
    wait_for_obscuring_elements(mydriver)
    new_project_btn.click()

    datadict = read_csv_line(csv_file_path, current_row)
    #print(datadict)
    print("\n----------------------------")
    print(f"Processing row {current_row}, Title: {datadict['4_title']}\n")


    # --- Title

    # <input type="text" class="form-control" name="title" id="title" value="" data-reactid=".2.0.0.1.2.0.$0.$0.$0.$displayPropKey2.0.2.0">
    project_title_form = WebDriverWait(mydriver, 10).until(EC.presence_of_element_located((By.ID, "title")))
    # title with pre-title (if existent):
    pojecttitle = datadict["4_title"] if len(datadict["4_pre_title"]) == 0 else datadict["4_pre_title"] + " " + datadict["4_title"]
    project_title_form.send_keys(pojecttitle)
    # .save-project
    project_title_apply = WebDriverWait(mydriver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".save-project")))
    #print("project_title_apply - found")
    project_title_apply.click()
    # <a role="button" class="btn btn-primary" href="workspace?goToPath=/datalumos/239181&amp;goToLevel=project" data-reactid=".2.0.0.1.2.1.0.0.0">Continue To Project Workspace</a>
    #   CSS-selector: a.btn-primary
    project_title_apply2 = WebDriverWait(mydriver, 100).until(EC.presence_of_element_located((By.LINK_TEXT, "Continue To Project Workspace")))
    #print("Continue To Project Workspace - found")
    project_title_apply2.click()


    # --- expand everything

    # collapse all: <span data-reactid=".0.3.1.1.0.1.2.0.1.0.1.1"> Collapse All</span>
    #   css-selector: #expand-init > span:nth-child(2)
    collapse_btn = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#expand-init > span:nth-child(2)")))
    wait_for_obscuring_elements(mydriver)
    collapse_btn.click()
    sleep(2)
    # expand all: <span data-reactid=".0.3.1.1.0.1.2.0.1.0.1.1"> Expand All</span>
    #   CSS-selector:    #expand-init > span:nth-child(2)
    expand_btn = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#expand-init > span:nth-child(2)")))
    wait_for_obscuring_elements(mydriver)
    expand_btn.click()
    sleep(2)


    # --- Government agency

    # government add value: <span data-reactid=".0.3.1.1.0.1.2.0.2.1:$0.$0.$0.0.$displayPropKey1.0.2.2"> add value</span>
    #   CSS-selector: #groupAttr0 > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(3) > span:nth-child(3)
    agency_investigator = [datadict["5_agency"], datadict["5_agency2"]]
    for singleinput in agency_investigator:
        if len(singleinput) != 0 and singleinput != " ":
            add_gvmnt_value = WebDriverWait(mydriver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#groupAttr0 > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(3) > span:nth-child(3)")))
            #print("add_gvmnt_value found")
            wait_for_obscuring_elements(mydriver)
            add_gvmnt_value.click()
            # <a href="#org" aria-controls="org" role="tab" data-toggle="tab" data-reactid=".2.0.0.1.0.1.0">Organization/Agency</a>
            #    css-selector: div.modal:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(2) > a:nth-child(1)
            agency_tab = WebDriverWait(mydriver, 100).until(EC.element_to_be_clickable((By.LINK_TEXT, "Organization/Agency")))
            #print("agency_tab found")
            wait_for_obscuring_elements(mydriver)
            agency_tab.click()
            # <input type="text" name="orgName" id="orgName" required="" class="form-control ui-autocomplete-input" value="" data-reactid=".2.0.0.1.1.1.0.0.0.1.0.0.0.1.0" autocomplete="off">
            agency_field = WebDriverWait(mydriver, 100).until(EC.presence_of_element_located((By.ID, "orgName")))
            agency_field.send_keys(singleinput)
            # submit: <button type="button" class="btn btn-primary save-org" data-reactid=".2.0.0.1.1.1.0.0.0.1.0.0.1.0.0">Save &amp; Apply</button>
            #   .save-org
            wait_for_obscuring_elements(mydriver)
            submit_agency_btn = WebDriverWait(mydriver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".save-org")))
            submit_agency_btn.click()


    # --- Summary

    summarytext = datadict["6_summary_description"]
    if len(summarytext) != 0 and summarytext != " ":
        # summary edit: <span data-reactid=".0.3.1.1.0.1.2.0.2.1:$0.$0.$0.0.$displayPropKey2.$dcterms_description_0.1.0.0.0.2.1"> edit</span>
        #   CSS-selector: #edit-dcterms_description_0 > span:nth-child(2)
        edit_summary = WebDriverWait(mydriver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#edit-dcterms_description_0 > span:nth-child(2)")))
        #print("edit_summary found")
        wait_for_obscuring_elements(mydriver)
        edit_summary.click()
        # summary form: <body contenteditable="true" class="editable-wysihtml5 wysihtml5-editor" spellcheck="true" style="background-color: rgb(255, 255, 255); color: rgb(51, 51, 51); cursor: text; font-family: &quot;Atkinson Hyperlegible&quot;, sans-serif; font-size: 16px; font-style: normal; font-variant: normal; font-weight: 400; line-height: 20px; letter-spacing: normal; text-align: start; text-decoration: rgb(51, 51, 51); text-indent: 0px; text-rendering: optimizelegibility; word-break: normal; overflow-wrap: break-word; word-spacing: 0px;"><span id="_wysihtml5-undo" class="_wysihtml5-temp">﻿</span></body>
        #   css-sel.: body
        summary_form = WebDriverWait(mydriver, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        wait_for_obscuring_elements(mydriver)
        summary_form.send_keys(datadict["6_summary_description"])
        # save: <i class="glyphicon glyphicon-ok"></i>
        #   .glyphicon-ok
        save_summary_btn = WebDriverWait(mydriver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".glyphicon-ok")))
    else:
        print("The summary is mandatory for the DataLumos project! Please fill it in manually.")


    # --- Original Distribution url

    original_url_text = datadict["7_original_distribution_url"]
    if len(original_url_text) != 0 and original_url_text != " ":
        # edit: <span data-reactid=".0.3.1.1.0.1.2.0.2.1:$0.$0.$0.0.$displayPropKey4.$imeta_sourceURL_0.1.0.0.0.2.0.1"> edit</span>
        #   css-sel: #edit-imeta_sourceURL_0 > span:nth-child(1) > span:nth-child(2)
        orig_distr_edit = WebDriverWait(mydriver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#edit-imeta_sourceURL_0 > span:nth-child(1) > span:nth-child(2)")))
        wait_for_obscuring_elements(mydriver)
        orig_distr_edit.click()
        # form: <input type="text" class="form-control input-sm" style="padding-right: 24px;">
        #   css-sel.: .editable-input > input:nth-child(1)
        orig_distr_form = WebDriverWait(mydriver, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".editable-input > input:nth-child(1)")))
        wait_for_obscuring_elements(mydriver)
        orig_distr_form.send_keys(original_url_text)
        # save: <button type="submit" class="btn btn-primary btn-sm editable-submit"><i class="glyphicon glyphicon-ok"></i> save</button>
        #   css-sel: .editable-submit
        orig_distr_form.submit()


    # --- Subject Terms / keywords

    # form: <input class="select2-search__field" type="search" tabindex="0" autocomplete="off" autocorrect="off" autocapitalize="none" spellcheck="false" role="textbox" aria-autocomplete="list" placeholder="" style="width: 0.75em;">
    #   css-sel: .select2-search__field
    # scroll bar: <li class="select2-results__option select2-results__option--highlighted" role="treeitem" aria-selected="false">HIFLD Open</li>
    #    css-sel: .select2-results__option
    keywordcells = [datadict["8_subject_terms1"], datadict["8_subject_terms2"], datadict["8_keywords"]]
    keywords_to_insert = []
    for single_keywordcell in keywordcells:
        if len(single_keywordcell) != 0 and single_keywordcell != " ":
            more_keywords = single_keywordcell.replace("'", "").replace("[", "").replace("]", "").replace('"', '')  # remove quotes and brackets
            more_keywordslist = more_keywords.split(",")
            keywords_to_insert += more_keywordslist
    print("\nkeywords_to_insert:", keywords_to_insert, "\n")
    for single_keyword in keywords_to_insert:
        keyword = single_keyword.strip(" '")
        try:
            wait_for_obscuring_elements(mydriver)
            keywords_form = WebDriverWait(mydriver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".select2-search__field")))
            keywords_form.click()
            keywords_form.send_keys(keyword)
            #sleep(2)
            wait_for_obscuring_elements(mydriver)
            #keyword_sugg = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".select2-results__option")))
            # find the list element, taking care to match the exact text [suggestion from user sefk]:
            keyword_sugg = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.XPATH, f"//li[contains(@class, 'select2-results__option') and text()='{keyword}']")))
            wait_for_obscuring_elements(mydriver)
            keyword_sugg.click()
        except:
            print("\nThere was a problem with the keywords! Please check if one ore more are missing in the form and fill them in manually.\n Problem:")
            print(traceback.format_exc())


    # --- Geographic Coverage

    geographic_coverage_text = datadict["9_geographic_coverage"]
    if len(geographic_coverage_text) != 0 and geographic_coverage_text != " ":
        # edit: <span data-reactid=".0.3.1.1.0.1.2.0.2.1:$0.$1.$1.0.$displayPropKey1.0.5:$dcterms_location_0_0.0.0.0.0.2.0.1"> edit</span>
        #   css-sel: #edit-dcterms_location_0 > span:nth-child(1) > span:nth-child(2)
        geogr_cov_edit = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#edit-dcterms_location_0 > span:nth-child(1) > span:nth-child(2)")))
        #print("edit-button geogr_cov_form found")
        wait_for_obscuring_elements(mydriver)
        geogr_cov_edit.click()
        # form: <input type="text" class="form-control input-sm" style="padding-right: 24px;">
        #   .editable-input > input:nth-child(1)
        geogr_cov_form = WebDriverWait(mydriver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".editable-input > input:nth-child(1)")))
        wait_for_obscuring_elements(mydriver)
        geogr_cov_form.send_keys(geographic_coverage_text)
        geogr_cov_form.submit()


    # --- Time Period

    timeperiod_start_text = datadict["10_time_period1"]
    timeperiod_end_text = datadict["10_time_period2"]
    if len(timeperiod_start_text) != 0 or len(timeperiod_end_text) != 0:
        # edit: <span data-reactid=".0.3.1.1.0.1.2.0.2.1:$0.$1.$1.0.$displayPropKey2.0.2.2"> add value</span>
        #   #groupAttr1 > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > a:nth-child(3) > span:nth-child(3)
        time_period_add_btn = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#groupAttr1 > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > a:nth-child(3) > span:nth-child(3)")))
        #print("time_period_add_btn found")
        wait_for_obscuring_elements(mydriver)
        time_period_add_btn.click()
        # start: <input type="text" class="form-control" name="startDate" id="startDate" required="" placeholder="YYYY-MM-DD or YYYY-MM or YYYY" title="Enter as YYYY-MM-DD or YYYY-MM or YYYY" value="" data-reactid=".4.0.0.1.1.0.1.0">
        #   #startDate
        time_period_start = WebDriverWait(mydriver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#startDate")))
        wait_for_obscuring_elements(mydriver)
        time_period_start.send_keys(timeperiod_start_text)
        # <input type="text" class="form-control" name="endDate" id="endDate" placeholder="YYYY-MM-DD or YYYY-MM or YYYY" title="Enter as YYYY-MM-DD or YYYY-MM or YYYY" value="" data-reactid=".4.0.0.1.1.1.1.0">
        #   #endDate
        time_period_end = WebDriverWait(mydriver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#endDate")))
        wait_for_obscuring_elements(mydriver)
        time_period_end.send_keys(timeperiod_end_text)
        print("\nYou have to fill in manually the textfield, if needed.\n")
        # <button type="button" class="btn btn-primary save-dates" data-reactid=".4.0.0.1.1.3.0.0">Save &amp; Apply</button>
        #    .save-dates
        save_time_btn = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".save-dates")))
        wait_for_obscuring_elements(mydriver)
        save_time_btn.click()


    # --- Data types

    datatype_to_select = datadict["11_data_types"]
    if len(datatype_to_select) != 0 and datatype_to_select != " ":
        # <span data-reactid=".0.3.1.1.0.1.2.0.2.1:$0.$1.$1.0.$displayPropKey5.$disco_kindOfData_0.1.0.0.0.2.1"> edit</span>
        #   #disco_kindOfData_0 > span:nth-child(2)
        datatypes_edit_btn = WebDriverWait(mydriver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#disco_kindOfData_0 > span:nth-child(2)")))
        wait_for_obscuring_elements(mydriver)
        datatypes_edit_btn.click()
        wait_for_obscuring_elements(mydriver)
        # <span> geographic information system (GIS) data</span>  # (there is a space character at the beginning of the string!)
        #   .editable-checklist > div:nth-child(8) > label:nth-child(1) > span:nth-child(2)
        datatype_text = WebDriverWait(mydriver, 50).until(EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{datatype_to_select}')]")))
        datatype_text.click()
        # <button type="submit" class="btn btn-primary btn-sm editable-submit"><i class="glyphicon glyphicon-ok"></i> save</button>
        #   .editable-submit
        datatypes_save_btn = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".editable-submit")))
        datatypes_save_btn.click()


    # --- Collection Notes

    if len(datadict["12_collection_notes"]) != 0 or len(datadict["12_download_date_original_source"]) != 0:
        # check if there is data in the date field (otherwise set it to empty string):
        downloaddate = f"(Downloaded {datadict['12_download_date_original_source']})" if len(datadict["12_download_date_original_source"]) != 0 else ""
        # the text for collection notes is the note and the download date, if the note cell in the csv file isn't empty (otherwise it's only the date):
        text_for_collectionnotes = datadict["12_collection_notes"] + " " + downloaddate if len(datadict["12_collection_notes"]) != 0 and datadict["12_collection_notes"] != " " else downloaddate
        # css-sel.: #edit-imeta_collectionNotes_0 > span:nth-child(2)
        coll_notes_edit_btn = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#edit-imeta_collectionNotes_0 > span:nth-child(2)")))
        wait_for_obscuring_elements(mydriver)
        coll_notes_edit_btn.click()
        # css-sel: body
        coll_notes_form = WebDriverWait(mydriver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        wait_for_obscuring_elements(mydriver)
        coll_notes_form.send_keys(text_for_collectionnotes)
        # css-sel: .editable-submit
        coll_notes_save_btn = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".editable-submit")))
        coll_notes_save_btn.click()


    # --- Upload files

    # upload-button: <span data-reactid=".0.3.1.1.0.0.0.0.0.0.1.2.3">Upload Files</span>
    #   a.btn-primary:nth-child(3) > span:nth-child(4)
    wait_for_obscuring_elements(mydriver)
    upload_btn = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-primary:nth-child(3) > span:nth-child(4)")))
    upload_btn.click()
    wait_for_obscuring_elements(mydriver)
    fileupload_field = WebDriverWait(mydriver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".col-md-offset-2 > span:nth-child(1)")))

    filepaths_to_upload = get_paths_uploadfiles(folder_path_uploadfiles)
    for singlefile in filepaths_to_upload:
        drag_and_drop_file(fileupload_field, singlefile)

    # when a file is uploaded and its progress bar is complete, a text appears: "File added to queue for upload."
    #   To check that the files are completey uploaded, this text has to be there as often as the number of files:
    filecount = len(filepaths_to_upload)
    #print("filecount:", filecount)
    #sleep(10)
    test2 = mydriver.find_elements(By.XPATH, "//span[text()='File added to queue for upload.']")
    # wait until the text has appeared as often as there are files:
    WebDriverWait(mydriver, 2000).until(lambda x: True if len(mydriver.find_elements(By.XPATH, "//span[text()='File added to queue for upload.']")) == filecount else False)
    print("\nEverything should be uploaded completely now.\n")



    # close-btn: .importFileModal > div:nth-child(3) > button:nth-child(1)
    wait_for_obscuring_elements(mydriver)
    close_btn = WebDriverWait(mydriver, 50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".importFileModal > div:nth-child(3) > button:nth-child(1)")))
    close_btn.click()


    print("\nContinue manually (check all the filled in details and publish the project).\n")

    #print("In the Inventory spreadsheet: Add the URL in the Download Location field, add 'Y’ to the Data Added field, and change the status field to ‘Done’.\n")
    print("In the Inventory spreadsheet: Add the needed data \n(for the HIFLD data: add the URL in the Download Location field, add 'Y’ to the Data Added field, and change the status field to ‘Done’).\n")





