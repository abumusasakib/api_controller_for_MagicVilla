import datetime
import os
import sys
import time
# gui modules
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showerror, showinfo
import tksheet

# report generate module
from prettytable import PrettyTable

import requests
import json

import logging
from logging.handlers import RotatingFileHandler
import traceback

import asyncio

global modified, data_loaded
modified = False
data_loaded = False

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Create a rotating file handler
log_file = 'villa.log'
max_file_size = 1024  # 1KB
max_backup_files = 5
handler = RotatingFileHandler(log_file, maxBytes=max_file_size, backupCount=max_backup_files)

# Configure log rotation options
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))

# Add the handler to the logger
logger = logging.getLogger()
logger.addHandler(handler)

# html to pdf convert function
def html_to_pdf(input_file_name):
    import pdfkit
    if sys.platform == 'win32':
        path_wkthmltopdf = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

    options = {
        'page-size': 'Letter',
        'orientation': 'Landscape',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'custom-header': [
                    ('Accept-Encoding', 'gzip')
        ],
        'no-outline': None
    }
    if sys.platform == 'win32':
        pdfkit.from_file(f"{input_file_name}.html", f"{input_file_name}.pdf",
                        configuration=config, options=options)
    elif sys.platform == 'linux':
        pdfkit.from_file(f"{input_file_name}.html", f"{input_file_name}.pdf",
                        options=options)

def get_villas_through_api():

    url = "https://localhost:7155/api/VillaAPI"

    querystring = {
    }

    headers = {
        'cache-control': "no-cache"
    }

    try:
        response = requests.request("GET", url,
                                    headers=headers,
                                    params=querystring,
                                    verify=False)
        if(response.status_code == 200):
            logger.info("Obtaining Villas OK")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)

        result = response.json()

        return {"result": result, "status": response.status_code}

    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")

def create_villa_through_api(name, details, rate, sqft, occupancy, imageUrl, amenity):
    url = "https://localhost:7155/api/VillaAPI"

    querystring = {
        "name": name,
        "details": details,
        "rate": rate,
        "occupancy": occupancy,
        "sqft": sqft,
        "imageUrl": imageUrl,
        "amenity": amenity
    }

    headers = {
        'cache-control': "no-cache"
    }

    try:
        response = requests.request("POST", url,
                                    headers=headers,
                                    json=querystring,
                                    verify=False)
        
        if(response.status_code == 201):
            logger.info("Villa Creation Done")
        elif(response.status_code == 400):
            logger.error("API Error (Bad Request)")
        elif(response.status_code == 500):
            logger.error("API Error (Internal Server Error)")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)

        return response.status_code


    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")

def update_villa_through_api(id, name, details, rate, occupancy, sqft, imageurl, amenity):
    url = f"https://localhost:7155/api/VillaAPI/{id}/"
    querystring = {
        "id": id,
        "name": name,
        "details": details,
        "rate": rate,
        "occupancy": occupancy,
        "sqft": sqft,
        "imageUrl": imageurl,
        "amenity": amenity
    }
    headers = {
        'cache-control': "no-cache"
    }

    try:
        response = requests.put(url,
                                headers=headers,
                                json=querystring,
                                verify=False)

        if response.status_code == 204:
            logger.info("Updating Villa OK")
        elif response.status_code == 400:
            logger.error("API Error (Bad Request)")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)

        return response.status_code

    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")

def get_villa_through_api(id):
    url = f"https://localhost:7155/api/VillaAPI/{id}/"

    querystring = {
    }

    headers = {
        'cache-control': "no-cache"
    }

    try:
        response = requests.request("GET", url,
                                    headers=headers,
                                    params=querystring,
                                    verify=False)
        
        if(response.status_code == 200):
            logger.info("Obtaining Villa OK")
        elif(response.status_code == 400):
            logger.error("API Error (Bad Request)")
        elif(response.status_code == 404):
            logger.error("Data not found")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)
        
        result = response.json()

        return {"result": result, "status": response.status_code}

    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")

def delete_villa_through_api(id):
    url = f"https://localhost:7155/api/VillaAPI/{id}/"

    querystring = {
    }

    headers = {
        'cache-control': "no-cache"
    }

    try:
        response = requests.request("DELETE", url,
                                    headers=headers,
                                    params=querystring,
                                    verify=False)
        
        if(response.status_code == 204):
            logger.info("Deleting Villa OK")
        elif(response.status_code == 400):
            logger.error("API Error (Bad Request)")
        elif(response.status_code == 404):
            logger.error("Data not found")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)
        

        return response.status_code

    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")

def update_partial_villa_through_api(id, querystring):
    url = f"https://localhost:7155/api/VillaAPI/{id}/"

    headers = {
        'Content-Type': 'application/json',
        'cache-control': "no-cache"
    }

    try:
        response = requests.request("PATCH", url,
                                    headers=headers,
                                    data=json.dumps(querystring),
                                    verify=False)

        if(response.status_code == 204):
            logger.info("Updating Villa OK")
        elif(response.status_code == 404):
            logger.error("Data not found")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)

        return response.status_code

    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")

def read_json(file_name):
    # Opening JSON file
    with open(f'{file_name}.json', 'r') as openfile:
        # Reading from json file
        json_object = json.load(openfile)
    return json_object

def write_json(json_object, file_name):
    # Writing to json file
    with open(f"{file_name}.json", "w") as outfile:
        json.dump(json_object, outfile)

# create the root window
root = tk.Tk()
root.title('MagicVilla API Controller')
root.resizable(False, False)
root.geometry('420x300')

def make_html():
    global data_loaded, modified
    
    if (data_loaded == False):
        print("Getting data from API")
        write_json(get_villas_through_api(),"villa_data")
        data_loaded = True
    elif(modified == True):
        print("Getting updated data from API")
        write_json(get_villas_through_api(),"villa_data")
        data_loaded = True
        modified = False

    villa_data = read_json("villa_data")
    
    if(villa_data['status'] == 200):
        heading = '--------------Villas--------------'

        dt_object = datetime.datetime.fromtimestamp(int(time.time()))
        date_time_formal = dt_object.strftime("%A, %d %B %Y at %I:%M %p")

        date = f"Date: {date_time_formal}"

        table = PrettyTable(
            ['ID', 'Name', 'Details', 'Rate', 'Sqft', 'Occupancy', 'Image URL', 'Amenity', 'Created Date', 'Updated Date'])

        for row in villa_data['result']:
            id = row['id']
            name = row['name']
            details = row['details']
            rate = row['rate']
            sqft = row['sqft']
            occupancy = row['occupancy']
            imageUrl = row['imageUrl']
            amenity = row['amenity']
            
            created_dt_obj = datetime.datetime.fromisoformat(row['createdDate'])

            createdDate = created_dt_obj.strftime(
                    "%Y-%m-%d %I:%M:%S %p")
            
            updated_dt_obj = datetime.datetime.fromisoformat(row['updatedDate'])

            updatedDate = updated_dt_obj.strftime(
                    "%Y-%m-%d %I:%M:%S %p")

            table.add_row([id, name, details, rate,
                           sqft, occupancy, imageUrl, amenity, createdDate, updatedDate])

        table_starting = "<html>\n<head>\n<title>List of villas</title>\n<style>\ntr > * + * {\n\tpadding-left: 4em;\n}\ntable, th, td {\n\tborder: 1px solid black;\n\tborder-collapse: collapse;\n}\n</style>\n</head>\n<body>\n"

        report = table_starting + f"<h1>{heading}</h1><br>\n" + f"<h2>{date}</h2>\n" + table.get_html_string() + "\n</body>\n</html>"

        file_name = "villas"

        file = open(f"{file_name}.html", 'w', encoding='utf-8')
        file.write(report)
        file.close()
    else:
        showerror(
            title='Error',
            message="An error has occured"
        )
        time.sleep(3)

def convert_dict_to_list(dict):
    # Get all the keys from the data
    keys = dict[0].keys()

    # Create a 2D list with keys in the first row
    result = [list(keys)]

    # Iterate over the data and extract values for each key
    for item in dict:
        values = [item[key] for key in keys]
        result.append(values)

    return result
def reload_villas():
    write_json(get_villas_through_api(), "villa_data")
    
    global data_loaded, modified
    villas = read_json("villa_data")
    data_loaded = True
    modified = False

    data = villas['result']

    result = convert_dict_to_list(data)

    # ✅ get the number of rows
    rows = len(result)
    print(rows)

    # ✅ get the number of columns
    cols = len(result[0])
    print(cols)

    global sheet
    sheet.set_sheet_data(result, redraw=True)
    sheet.sheet_data_dimensions(total_rows = rows, total_columns = cols)

def show_villas():
    from tksheet import Sheet
    import tkinter as tk
    from tkinter import ttk

    global app
    app = tk.Tk()
    app.title('List of villas')
    app.resizable(True, True)
    app.geometry('680x400')
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)

    main_frame = tk.Frame(app)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)

    global data_loaded
    write_json(get_villas_through_api(), "villa_data")
    data_loaded = True
    
    if data_loaded == True:
        villa_data = read_json("villa_data")
        data = villa_data['result']
    else:
        logger.exception("Data is not available")
        raise ValueError

    result = convert_dict_to_list(data)

    # ✅ get the number of rows
    rows = len(result)
    print(rows)

    # ✅ get the number of columns
    cols = len(result[0])
    print(cols)

    global sheet
    sheet = Sheet(main_frame, total_rows=rows, total_columns=cols)
    sheet.grid(row=1, column=0, sticky="nswe", padx=10, pady=10)
    sheet.set_sheet_data(result, redraw=True)

    sheet.headers(newheaders=0, index=None, reset_col_positions=False, show_headers_if_not_sheet=True, redraw=False)
    sheet.hide_rows(rows={0}, redraw=True, deselect_all=True)

    # table enable choices listed below:
    sheet.enable_bindings(("single_select",
                           "row_select",
                           "column_width_resize",
                           "arrowkeys",
                           "right_click_popup_menu",
                           "rc_select",
                           "copy",))

    def export_to_html():
        make_html()
        os.system("villas.html")

    def export_to_pdf():
        make_html()
        html_to_pdf("villas")
        os.system("villas.pdf")

    export_buttons_frame = ttk.Frame(app)
    export_buttons_frame.grid(row=1, column=0, sticky="se", padx=10, pady=10)

    export_to_html_button = ttk.Button(
        export_buttons_frame,
        text='Export to HTML',
        command=export_to_html
    )

    export_to_pdf_button = ttk.Button(
        export_buttons_frame,
        text='Export to PDF',
        command=export_to_pdf
    )

    export_to_html_button.grid(row=0, column=0, padx=5, pady=5)
    export_to_pdf_button.grid(row=0, column=1, padx=5, pady=5)

    reload_button_frame = ttk.Frame(app)
    reload_button_frame.grid(row=0, column=0, sticky="ne", padx=10, pady=10)

    reload_button = ttk.Button(
        reload_button_frame,
        text='Reload',
        command=reload_villas()
    )

    # Add a button at the top right
    reload_button.grid(row=0, column=0, padx=5, pady=5)

    # Frame for bottom left buttons
    bottom_buttons_frame = ttk.Frame(app)
    bottom_buttons_frame.grid(row=1, column=0, sticky="sw", padx=10, pady=10)

    create_villa_button = ttk.Button(
        bottom_buttons_frame,
        text='Create',
        command=create_villa
    )

    find_villa_button = ttk.Button(
        bottom_buttons_frame,
        text='Find',
        command=find_villa
    )

    update_villa_button = ttk.Button(
        bottom_buttons_frame,
        text='Update',
        command=update_villa
    )    
    
    update_partial_villa_button = ttk.Button(
        bottom_buttons_frame,
        text='Update partial',
        command=update_partial_villa
    )

    delete_villa_button = ttk.Button(
        bottom_buttons_frame,
        text='Delete',
        command=delete_villa
    )

    create_villa_button.grid(row=0, column=0, padx=5, pady=5)
    find_villa_button.grid(row=0, column=1, padx=5, pady=5)
    update_villa_button.grid(row=0, column=2, padx=5, pady=5)
    update_partial_villa_button.grid(row=0, column=3, padx=5, pady=5)
    delete_villa_button.grid(row=0, column=4, padx=5, pady=5)

    app.mainloop()



def create_villa():
    showinfo(
                title='Create villa',
                message='Please enter the requested information to create a villa'
            )

    # create a GUI window
    root = tk.Tk()

    # set the title of GUI window
    root.title("Create a new villa")

    # set the configuration of GUI window
    root.geometry("550x400")

    root.resizable(False, False)

    # create a Name label
    name = ttk.Label(
        root, text="Name", justify=tk.LEFT, padding=15)

    # create a Details label
    details = ttk.Label(
        root, text="Details", justify=tk.LEFT, padding=15)

    # create a Rate label
    rate = ttk.Label(
        root, text="Rate", justify=tk.LEFT, padding=15)
    
    # create a Sqft label
    sqft = ttk.Label(
        root, text="Sqft", justify=tk.LEFT, padding=15)

    # create a Occupancy label
    occupancy = ttk.Label(
        root, text="Occupancy", justify=tk.LEFT, padding=15)
    
    # create a imageUrl label
    imageurl = ttk.Label(
        root, text="Image URL", justify=tk.LEFT, padding=15)
    
    # create a amenity label
    amenity = ttk.Label(
        root, text="Amenity", justify=tk.LEFT, padding=15)

    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure .
    name.grid(row=1, column=0)
    details.grid(row=2, column=0)
    rate.grid(row=3, column=0)
    sqft.grid(row=4, column=0)
    occupancy.grid(row=5, column=0)
    imageurl.grid(row=6, column=0)
    amenity.grid(row=7, column=0)

    def insert():
        name = name_field.get()
        details = details_field.get()
        rate = rate_field.get()
        sqft = sqft_field.get()
        occupancy = occupancy_field.get()
        imageurl = imageurl_field.get()
        amenity = amenity_field.get()

        try:
            api_response = create_villa_through_api(
                name, details, rate, sqft, occupancy, imageurl, amenity)
            
            if api_response == 201:
                global modified, sheet
                modified = True
                showinfo(title='Success', message="Villa created successfully")

                if sheet is not None:
                    reload_villas()
            elif api_response is not None:
                raise ValueError(f"An API error occured with status code {api_response}")
            else:
                raise requests.exceptions.RequestException
        
        except requests.exceptions.RequestException as e:
            showerror(title='Error', message="A network error occurred. Please check your internet connection.")
            
        except ValueError as e:
            showerror(title='Error', message=str(e))
            
        except Exception as e:
            showerror(title='Error', message="An unexpected error occurred.")
            # Log the error for debugging purposes
            logging.exception("An unexpected error occurred in the insert() function.")

        
    # create a text entry box
    # for typing the information
    name_field = ttk.Entry(root)
    details_field = ttk.Entry(root)
    rate_field = ttk.Entry(root)
    occupancy_field = ttk.Entry(root)
    sqft_field = ttk.Entry(root)
    imageurl_field = ttk.Entry(root)
    amenity_field = ttk.Entry(root)

    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure .
    name_field.grid(row=1, column=1, ipadx="80")
    details_field.grid(row=2, column=1, ipadx="80")
    rate_field.grid(row=3, column=1, ipadx="80")
    occupancy_field.grid(row=4, column=1, ipadx="80")
    sqft_field.grid(row=5, column=1, ipadx="80")
    imageurl_field.grid(row=6, column=1, ipadx="80")
    amenity_field.grid(row=7, column=1, ipadx="80")

    submit = ttk.Button(root, text="Submit", command=insert)
    submit.grid(row=8, column=2)

    # start the GUI
    root.mainloop()

def find_villa():
    new_root = tk.Tk()

    # config the root window
    new_root.geometry('350x250')
    new_root.resizable(False, False)
    new_root.title('Search for villas')

    # label
    label = ttk.Label(new_root,text="Enter id: ")
    label.pack(fill=tk.X, padx=5, pady=5)

    id_field = ttk.Entry(new_root)

    id_field.pack(ipadx=120)

    def search():
        query = id_field.get()

        villa = get_villa_through_api(query)

        if villa is not None:
            if (villa['status'] == 200):
                id = villa['result']['id']
                name = villa['result']['name']
                details = villa['result']['details']
                rate = villa['result']['rate']
                sqft = villa['result']['sqft']
                occupancy = villa['result']['occupancy']
                imageurl = villa['result']['imageUrl']
                amenity = villa['result']['amenity']

                created_dt_obj = datetime.datetime.fromisoformat(villa['result']['createdDate'])

                createdDate = created_dt_obj.strftime(
                        "%Y-%m-%d %I:%M:%S %p")
                
                updated_dt_obj = datetime.datetime.fromisoformat(villa['result']['updatedDate'])

                updatedDate = updated_dt_obj.strftime(
                        "%Y-%m-%d %I:%M:%S %p")
                
                output = f"ID: {id}\nName: {name}\nDetails: {details}\nRate: {rate}\nSqft: {sqft}\nOccupancy: {occupancy}\nImage URL: {imageurl}\nAmenity: {amenity}\nCreated Date: {createdDate}\nUpdated Date: {updatedDate}"
                showinfo(
                    title='Record found',
                    message=output
                )
            elif (villa['status'] == 404):
                showerror(
                    title='Error',
                    message="Cannot find data"
                )
            else:
                showerror(
                    title='Error',
                    message=f"API returned status code {villa['status']}"
                )
        else:
            showerror(
                title='Error',
                message=f"Unable to access API"
            )
    
    search_button = ttk.Button(
        new_root,
        text='Search',
        command=search
    )

    search_button.pack(expand=True)
    # run the app
    new_root.mainloop()

def delete_villa():
    new_root = tk.Tk()

    # config the root window
    new_root.geometry('350x250')
    new_root.resizable(False, False)
    new_root.title('Delete villa')

    # label
    label = ttk.Label(new_root,text="Enter id: ")
    label.pack(fill=tk.X, padx=5, pady=5)

    id_field = ttk.Entry(new_root)

    id_field.pack(ipadx=120)

    def delete():
        query = id_field.get()

        result = delete_villa_through_api(query)

        if (result == 204):
            global modified, sheet
            modified = True
            
            showinfo(
                title='Success',
                message="Deleted successfully"
            )

            if sheet is not None:
                reload_villas()
        else:
            showerror(
                title='Error',
                message="Unable to delete"
            )
    
    delete_button = ttk.Button(
        new_root,
        text='Delete',
        command=delete
    )

    delete_button.pack(expand=True)
    # run the app
    new_root.mainloop()

def update_villa():
    showinfo(
                title='Update villa',
                message='Please enter the requested information to update a villa'
            )

    # create a GUI window
    root = tk.Tk()

    # set the title of GUI window
    root.title("Update existing villa")

    # set the configuration of GUI window
    root.geometry("550x450")

    root.resizable(False, False)

    # create an ID label
    id = ttk.Label(
        root, text="ID", justify=tk.LEFT, padding=15)

    # create a Name label
    name = ttk.Label(
        root, text="Name", justify=tk.LEFT, padding=15)

    # create a Details label
    details = ttk.Label(
        root, text="Details", justify=tk.LEFT, padding=15)

    # create a Rate label
    rate = ttk.Label(
        root, text="Rate", justify=tk.LEFT, padding=15)
    
    # create a Sqft label
    sqft = ttk.Label(
        root, text="Sqft", justify=tk.LEFT, padding=15)

    # create a Occupancy label
    occupancy = ttk.Label(
        root, text="Occupancy", justify=tk.LEFT, padding=15)

    
    # create a imageUrl label
    imageurl = ttk.Label(
        root, text="Image URL", justify=tk.LEFT, padding=15)
    
    # create a amenity label
    amenity = ttk.Label(
        root, text="Amenity", justify=tk.LEFT, padding=15)

    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure .
    id.grid(row=1, column=0)
    name.grid(row=2, column=0)
    details.grid(row=3, column=0)
    rate.grid(row=4, column=0)
    sqft.grid(row=5, column=0)
    occupancy.grid(row=6, column=0)
    imageurl.grid(row=7, column=0)
    amenity.grid(row=8, column=0)

    def update():
        id = id_field.get()
        name = name_field.get()
        details = details_field.get()
        rate = rate_field.get()
        occupancy = occupancy_field.get()
        sqft = sqft_field.get()
        imageurl = imageurl_field.get()
        amenity = amenity_field.get()
        
        result = update_villa_through_api(
                id, name, details, rate, occupancy, sqft, imageurl, amenity)

        if (result == 204):
            global modified
            modified = True

            showinfo(
                title='Success',
                message="Updated successfully"
            )

            if sheet is not None:
                reload_villas()
        else:
            showerror(
                title='Error',
                message="Unable to update"
            )
        
    # create a text entry box
    # for typing the information
    id_field = ttk.Entry(root)
    name_field = ttk.Entry(root)
    details_field = ttk.Entry(root)
    rate_field = ttk.Entry(root)
    occupancy_field = ttk.Entry(root)
    sqft_field = ttk.Entry(root)
    imageurl_field = ttk.Entry(root)
    amenity_field = ttk.Entry(root)

    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure .
    id_field.grid(row=1, column=1, ipadx="80")
    name_field.grid(row=2, column=1, ipadx="80")
    details_field.grid(row=3, column=1, ipadx="80")
    rate_field.grid(row=4, column=1, ipadx="80")
    occupancy_field.grid(row=5, column=1, ipadx="80")
    sqft_field.grid(row=6, column=1, ipadx="80")
    imageurl_field.grid(row=7, column=1, ipadx="80")
    amenity_field.grid(row=8, column=1, ipadx="80")

    submit = ttk.Button(root, text="Submit", command=update)
    submit.grid(row=9, column=2)

    # start the GUI
    root.mainloop()

def update_partial_villa():
    showinfo(title='Update partial villa', message='Please enter the ID as well as tick the checkboxes and enter values to update a villa')

    # Create dictionaries to store the checkbox values and text entry fields
    checkbox_values = {}
    entry_fields = {}

    def update():
        # Retrieve the values from the checkboxes and text entry fields
        selected_values = []
        single_value = {}
        for label_text, var in checkbox_values.items():
            value = var.get()  # Get the value of the IntVar
            entry_text = entry_fields[label_text].get()  # Get the value of the corresponding text entry field
            if value == 1 and entry_text != '':
                single_value = {"label_text": label_text, "entry_text":entry_text}
                selected_values.append(single_value)
        print(selected_values)

        if selected_values == []:
            showerror(
                title='Error',
                message="Nothing has been selected"
            )
        elif selected_values[0]['label_text'] != 'ID':
            showerror(
                title='Error',
                message="Please enter an ID"
            )
        
        if selected_values != []:
            id = selected_values[0]['entry_text']


        only_id = True  # Assume only 'ID' is selected
        for single_val in selected_values:
            if single_val['label_text'] != 'ID':
                only_id = False  # Found a label other than 'ID'
                break  # No need to continue checking

        if only_id:
            showerror(title='Error', message="Please select other entities")
        
        queryparams = []
        if not only_id and selected_values:
            id = selected_values[0]['entry_text']

            for index, single_val in enumerate(selected_values):
                if index == 0:
                    continue  # Skip the first element

                label_text = single_val['label_text']
                entry_text = single_val['entry_text']
                queryparams.append({"op": "replace", "path": f"/{label_text.lower()}", "value": entry_text})


            response = update_partial_villa_through_api(id,queryparams)

            
            if (response == 204):
                global modified
                modified = True

                showinfo(
                    title='Success',
                    message="Updated successfully"
                )

                if sheet is not None:
                    reload_villas()
            else:
                showerror(
                    title='Error',
                    message="Unable to update"
                )
            





   # Create a new window as a child of root
    new_root = tk.Toplevel(root)
    new_root.title("Update existing villa")
    new_root.geometry("550x450")
    new_root.resizable(False, False)
    
    # Function to create a checkbox and label pair
    def create_checkbox_label_pair(row, label_text, always_checked=False):
        var = tk.IntVar()
        if always_checked:
            var.set(1)  # Set the value of the IntVar to 1 (checked)
            checkbox = ttk.Checkbutton(new_root, variable=var, state='disabled')
        else:
            checkbox = ttk.Checkbutton(new_root, variable=var)
        checkbox.grid(row=row, column=0, sticky='w')
        checkbox_values[label_text] = var
        ttk.Label(new_root, text=label_text, justify=tk.LEFT, padding=15).grid(row=row, column=1, sticky='w')


    # Create checkbox and label pairs
    create_checkbox_label_pair(1, "ID", always_checked=True)
    create_checkbox_label_pair(2, "Name")
    create_checkbox_label_pair(3, "Details")
    create_checkbox_label_pair(4, "Rate")
    create_checkbox_label_pair(5, "Sqft")
    create_checkbox_label_pair(6, "Occupancy")
    create_checkbox_label_pair(7, "Image URL")
    create_checkbox_label_pair(8, "Amenity")

    # Create text entry boxes
    id_field = ttk.Entry(new_root)
    name_field = ttk.Entry(new_root)
    details_field = ttk.Entry(new_root)
    rate_field = ttk.Entry(new_root)
    occupancy_field = ttk.Entry(new_root)
    sqft_field = ttk.Entry(new_root)
    imageurl_field = ttk.Entry(new_root)
    amenity_field = ttk.Entry(new_root)

    # Grid placement for text entry boxes
    id_field.grid(row=1, column=2, padx=5, ipadx="125")
    name_field.grid(row=2, column=2, padx=5, ipadx="125")
    details_field.grid(row=3, column=2, padx=5, ipadx="125")
    rate_field.grid(row=4, column=2, padx=5, ipadx="125")
    occupancy_field.grid(row=5, column=2, padx=5, ipadx="125")
    sqft_field.grid(row=6, column=2, padx=5, ipadx="125")
    imageurl_field.grid(row=7, column=2, padx=5, ipadx="125")
    amenity_field.grid(row=8, column=2, padx=5, ipadx="125")

    # Store text entry fields in the entry_fields dictionary
    entry_fields["ID"] = id_field
    entry_fields["Name"] = name_field
    entry_fields["Details"] = details_field
    entry_fields["Rate"] = rate_field
    entry_fields["Occupancy"] = occupancy_field
    entry_fields["Sqft"] = sqft_field
    entry_fields["Image URL"] = imageurl_field
    entry_fields["Amenity"] = amenity_field

    submit = ttk.Button(new_root, text="Submit", command=update)
    submit.grid(row=9, column=2, pady=10)

    # Start the GUI
    new_root.mainloop()



def close():
    global root
    root.destroy()

list_villas_button = ttk.Button(
    root,
    text='Show all villas through API',
    command=show_villas
)
create_villa_button = ttk.Button(
    root,
    text='Create a new villa',
    command=create_villa
)
search_villa_button = ttk.Button(
    root,
    text='Find vila through API',
    command=find_villa
)
delete_villa_button = ttk.Button(
    root,
    text='Delete villa through API',
    command=delete_villa
)

update_villa_button = ttk.Button(
    root,
    text='Update villa through API',
    command=update_villa
)

update_partial_villa_button = ttk.Button(
    root,
    text='Update partial villa through API',
    command=update_partial_villa
)

quit_button = ttk.Button(
    root,
    text='Close',
    command=close
)

list_villas_button.pack(expand=True)
create_villa_button.pack(expand=True)
search_villa_button.pack(expand=True)
delete_villa_button.pack(expand=True)
update_villa_button.pack(expand=True)
update_partial_villa_button.pack(expand=True)
quit_button.pack(expand=True)

root.protocol("WM_DELETE_WINDOW", close)

# run the app
root.mainloop()