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
sheet = None

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Create a rotating file handler
log_file = "villa.log"
max_file_size = 1024  # 1KB
max_backup_files = 5
handler = RotatingFileHandler(
    log_file, maxBytes=max_file_size, backupCount=max_backup_files
)

# Configure log rotation options
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))

# Add the handler to the logger
logger = logging.getLogger()
logger.addHandler(handler)


# html to pdf convert function
def html_to_pdf(input_file_name):
    import pdfkit

    if sys.platform == "win32":
        path_wkthmltopdf = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

    options = {
        "page-size": "Letter",
        "orientation": "Landscape",
        "margin-top": "0.75in",
        "margin-right": "0.75in",
        "margin-bottom": "0.75in",
        "margin-left": "0.75in",
        "encoding": "UTF-8",
        "custom-header": [("Accept-Encoding", "gzip")],
        "no-outline": None,
    }
    if sys.platform == "win32":
        pdfkit.from_file(
            f"{input_file_name}.html",
            f"{input_file_name}.pdf",
            configuration=config,
            options=options,
        )
    elif sys.platform == "linux":
        pdfkit.from_file(
            f"{input_file_name}.html", f"{input_file_name}.pdf", options=options
        )


field_labels = {
    "id": "ID",
    "name": "Name",
    "details": "Details",
    "rate": "Rate",
    "sqft": "Sqft",
    "occupancy": "Occupancy",
    "imageUrl": "Image URL",
    "amenity": "Amenity",
}

numeric_fields = {"rate": "float", "sqft": "int", "occupancy": "int"}


def get_villas_through_api():

    url = "http://localhost:7155/api/VillaAPI"

    querystring = {}

    headers = {"cache-control": "no-cache"}

    try:
        response = requests.request(
            "GET", url, headers=headers, params=querystring, verify=False
        )
        print(response)
        print(response.text)
        if response.status_code == 200:
            logger.info("Obtaining Villas OK")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)

        result = response.json()

        return {"result": result, "status": response.status_code}

    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")


def create_villa_through_api(name, details, rate, sqft, occupancy, imageUrl, amenity):
    url = "http://localhost:7155/api/VillaAPI"

    querystring = {
        "name": name,
        "details": details,
        "rate": rate,
        "occupancy": occupancy,
        "sqft": sqft,
        "imageUrl": imageUrl,
        "amenity": amenity,
    }

    headers = {"cache-control": "no-cache"}

    try:
        response = requests.request(
            "POST", url, headers=headers, json=querystring, verify=False
        )

        if response.status_code == 201:
            logger.info("Villa Creation Done")
        elif response.status_code == 400:
            logger.error("API Error (Bad Request)")
        elif response.status_code == 500:
            logger.error("API Error (Internal Server Error)")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)

        return response.status_code

    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")


def update_villa_through_api(
    id, name, details, rate, occupancy, sqft, imageurl, amenity
):
    url = f"http://localhost:7155/api/VillaAPI/{id}/"
    querystring = {
        "id": id,
        "name": name,
        "details": details,
        "rate": rate,
        "occupancy": occupancy,
        "sqft": sqft,
        "imageUrl": imageurl,
        "amenity": amenity,
    }
    headers = {"cache-control": "no-cache"}

    try:
        response = requests.put(url, headers=headers, json=querystring, verify=False)

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
    url = f"http://localhost:7155/api/VillaAPI/{id}/"

    querystring = {}

    headers = {"cache-control": "no-cache"}

    try:
        response = requests.request(
            "GET", url, headers=headers, params=querystring, verify=False
        )

        if response.status_code == 200:
            logger.info("Obtaining Villa OK")
        elif response.status_code == 400:
            logger.error("API Error (Bad Request)")
        elif response.status_code == 404:
            logger.error("Data not found")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)

        result = response.json()

        return {"result": result, "status": response.status_code}

    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")


def delete_villa_through_api(id):
    url = f"http://localhost:7155/api/VillaAPI/{id}/"

    querystring = {}

    headers = {"cache-control": "no-cache"}

    try:
        response = requests.request(
            "DELETE", url, headers=headers, params=querystring, verify=False
        )

        if response.status_code == 204:
            logger.info("Deleting Villa OK")
        elif response.status_code == 400:
            logger.error("API Error (Bad Request)")
        elif response.status_code == 404:
            logger.error("Data not found")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)

        return response.status_code

    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")


def update_partial_villa_through_api(id, querystring):
    url = f"http://localhost:7155/api/VillaAPI/{id}/"

    headers = {"Content-Type": "application/json", "cache-control": "no-cache"}

    try:
        response = requests.request(
            "PATCH", url, headers=headers, data=json.dumps(querystring), verify=False
        )

        if response.status_code == 204:
            logger.info("Updating Villa OK")
        elif response.status_code == 404:
            logger.error("Data not found")
        else:
            logger.warning("Unhandled status code: %s", response.status_code)

        return response.status_code

    except Exception as e:
        logger.exception("An exception occurred while updating the villa:")


def read_json(file_name):
    # Opening JSON file
    with open(f"{file_name}.json", "r") as openfile:
        # Reading from json file
        json_object = json.load(openfile)
    return json_object


def write_json(json_object, file_name):
    # Writing to json file
    with open(f"{file_name}.json", "w") as outfile:
        json.dump(json_object, outfile)


# create the root window
global app
app = tk.Tk()
app.title("MagicVilla API Controller")
app.resizable(False, False)
app.geometry("420x300")


def make_html():
    global data_loaded, modified

    if data_loaded == False:
        print("Getting data from API")
        write_json(get_villas_through_api(), "villa_data")
        data_loaded = True
    elif modified == True:
        print("Getting updated data from API")
        write_json(get_villas_through_api(), "villa_data")
        data_loaded = True
        modified = False

    villa_data = read_json("villa_data")

    if villa_data["status"] == 200:
        heading = "--------------Villas--------------"

        dt_object = datetime.datetime.fromtimestamp(int(time.time()))
        date_time_formal = dt_object.strftime("%A, %d %B %Y at %I:%M %p")

        date = f"Date: {date_time_formal}"

        table = PrettyTable(
            [
                "ID",
                "Name",
                "Details",
                "Rate",
                "Sqft",
                "Occupancy",
                "Image URL",
                "Amenity",
                "Created Date",
                "Updated Date",
            ]
        )

        for row in villa_data["result"]:
            id = row["id"]
            name = row["name"]
            details = row["details"]
            rate = row["rate"]
            sqft = row["sqft"]
            occupancy = row["occupancy"]
            imageUrl = row["imageUrl"]
            amenity = row["amenity"]

            created_dt_obj = datetime.datetime.fromisoformat(row["createdDate"])

            createdDate = created_dt_obj.strftime("%Y-%m-%d %I:%M:%S %p")

            updated_dt_obj = datetime.datetime.fromisoformat(row["updatedDate"])

            updatedDate = updated_dt_obj.strftime("%Y-%m-%d %I:%M:%S %p")

            table.add_row(
                [
                    id,
                    name,
                    details,
                    rate,
                    sqft,
                    occupancy,
                    imageUrl,
                    amenity,
                    createdDate,
                    updatedDate,
                ]
            )

        table_starting = "<html>\n<head>\n<title>List of villas</title>\n<style>\ntr > * + * {\n\tpadding-left: 4em;\n}\ntable, th, td {\n\tborder: 1px solid black;\n\tborder-collapse: collapse;\n}\n</style>\n</head>\n<body>\n"

        report = (
            table_starting
            + f"<h1>{heading}</h1><br>\n"
            + f"<h2>{date}</h2>\n"
            + table.get_html_string()
            + "\n</body>\n</html>"
        )

        file_name = "villas"

        file = open(f"{file_name}.html", "w", encoding="utf-8")
        file.write(report)
        file.close()
    else:
        showerror(title="Error", message="An error has occured")
        time.sleep(3)


def convert_dict_to_list(dict_list):
    if not dict_list:
        return []  # return empty list if no data

    keys = dict_list[0].keys()
    result = [list(keys)]

    for item in dict_list:
        values = [item[key] for key in keys]
        result.append(values)

    return result


def reload_villas():
    write_json(get_villas_through_api(), "villa_data")

    global data_loaded, modified, view_app
    villas = read_json("villa_data")
    data_loaded = True
    modified = True

    # Destroy current window if it exists
    try:
        if view_app is not None:
            view_app.destroy()
    except Exception as e:
        logging.warning("Failed to destroy existing view window: %s", e)

    # Recreate the entire villa list window
    show_villas()


def show_villas():
    from tksheet import Sheet
    import tkinter as tk
    from tkinter import ttk

    global data_loaded
    write_json(get_villas_through_api(), "villa_data")
    data_loaded = True

    if data_loaded == True:
        villa_data = read_json("villa_data")
        data = villa_data["result"]
    else:
        logger.exception("Data is not available")
        raise ValueError

    if not data:
        showinfo("No Villas", "No villas found in the database.")
        return

    global view_app
    view_app = tk.Tk()
    view_app.title("List of villas")
    view_app.resizable(True, True)
    view_app.geometry("680x400")
    view_app.grid_columnconfigure(0, weight=1)
    view_app.grid_rowconfigure(0, weight=1)

    main_frame = tk.Frame(view_app)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)

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

    sheet.headers(
        newheaders=0,
        index=None,
        reset_col_positions=False,
        show_headers_if_not_sheet=True,
        redraw=False,
    )
    sheet.hide_rows(rows={0}, redraw=True, deselect_all=True)

    # table enable choices listed below:
    sheet.enable_bindings(
        (
            "single_select",
            "row_select",
            "column_width_resize",
            "arrowkeys",
            "right_click_popup_menu",
            "rc_select",
            "copy",
        )
    )

    def export_to_html():
        make_html()
        os.system("villas.html")

    def export_to_pdf():
        make_html()
        html_to_pdf("villas")
        os.system("villas.pdf")

    export_buttons_frame = ttk.Frame(view_app)
    export_buttons_frame.grid(row=1, column=0, sticky="se", padx=10, pady=10)

    export_to_html_button = ttk.Button(
        export_buttons_frame, text="Export to HTML", command=export_to_html
    )

    export_to_pdf_button = ttk.Button(
        export_buttons_frame, text="Export to PDF", command=export_to_pdf
    )

    export_to_html_button.grid(row=0, column=0, padx=5, pady=5)
    export_to_pdf_button.grid(row=0, column=1, padx=5, pady=5)

    reload_button_frame = ttk.Frame(view_app)
    reload_button_frame.grid(row=0, column=0, sticky="ne", padx=10, pady=10)

    reload_button = ttk.Button(
        reload_button_frame, text="Reload", command=reload_villas
    )

    # Add a button at the top right
    reload_button.grid(row=0, column=0, padx=5, pady=5)

    # Frame for bottom left buttons
    bottom_buttons_frame = ttk.Frame(view_app)
    bottom_buttons_frame.grid(row=1, column=0, sticky="sw", padx=10, pady=10)

    create_villa_button = ttk.Button(
        bottom_buttons_frame, text="Create", command=create_villa
    )

    find_villa_button = ttk.Button(
        bottom_buttons_frame, text="Find", command=find_villa
    )

    update_villa_button = ttk.Button(
        bottom_buttons_frame, text="Update", command=update_villa
    )

    update_partial_villa_button = ttk.Button(
        bottom_buttons_frame, text="Update partial", command=update_partial_villa
    )

    delete_villa_button = ttk.Button(
        bottom_buttons_frame, text="Delete", command=delete_villa
    )

    create_villa_button.grid(row=0, column=0, padx=5, pady=5)
    find_villa_button.grid(row=0, column=1, padx=5, pady=5)
    update_villa_button.grid(row=0, column=2, padx=5, pady=5)
    update_partial_villa_button.grid(row=0, column=3, padx=5, pady=5)
    delete_villa_button.grid(row=0, column=4, padx=5, pady=5)

    view_app.mainloop()


def create_villa():
    showinfo(
        title="Create villa",
        message="Please enter the requested information to create a villa",
    )

    # create a GUI window
    root = tk.Tk()

    # set the title of GUI window
    root.title("Create a new villa")

    # set the configuration of GUI window
    root.geometry("550x400")

    root.resizable(False, False)

    # create labels
    # create a Name label
    name = ttk.Label(root, text="Name", justify=tk.LEFT, padding=15)

    # create a Details label
    details = ttk.Label(root, text="Details", justify=tk.LEFT, padding=15)

    # create a Rate label
    rate = ttk.Label(root, text="Rate", justify=tk.LEFT, padding=15)

    # create a Sqft label
    sqft = ttk.Label(root, text="Sqft", justify=tk.LEFT, padding=15)

    # create a Occupancy label
    occupancy = ttk.Label(root, text="Occupancy", justify=tk.LEFT, padding=15)

    # create a imageUrl label
    imageurl = ttk.Label(root, text="Image URL", justify=tk.LEFT, padding=15)

    # create a amenity label
    amenity = ttk.Label(root, text="Amenity", justify=tk.LEFT, padding=15)

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

    def mark_valid(widget, is_valid):
        widget.configure(background="white" if is_valid else "#ffdddd")

    def validate_fields(*args):
        name = name_field.get().strip()
        details = details_field.get().strip()
        rate = rate_field.get().strip()
        sqft = sqft_field.get().strip()
        occupancy = occupancy_field.get().strip()
        imageurl = imageurl_field.get().strip()

        message = ""
        is_valid = True

        # Field checks (in priority order for UX)
        if not name:
            message = "Name is required."
            is_valid = False
        elif not details:
            message = "Details are required."
            is_valid = False
        elif not rate.replace(".", "", 1).isdigit():
            message = "Rate must be a number."
            is_valid = False
        elif not sqft.isdigit():
            message = "Sqft must be an integer."
            is_valid = False
        elif not occupancy.isdigit():
            message = "Occupancy must be an integer."
            is_valid = False
        elif not imageurl.startswith("http://") and not imageurl.startswith("https://"):
            message = "Image URL must start with http:// or https://"
            is_valid = False

        # Highlight fields based on their individual validity
        mark_valid(rate_field, rate.replace(".", "", 1).isdigit())
        mark_valid(sqft_field, sqft.isdigit())
        mark_valid(occupancy_field, occupancy.isdigit())
        mark_valid(
            imageurl_field,
            imageurl.startswith("http://") or imageurl.startswith("https://"),
        )

        # Show or clear message
        validation_message.config(text=message)
        submit.config(state="normal" if is_valid else "disabled")

    def insert():
        name_val = name_field.get().strip()
        details_val = details_field.get().strip()
        rate_val = rate_field.get().strip()
        sqft_val = sqft_field.get().strip()
        occupancy_val = occupancy_field.get().strip()
        imageurl_val = imageurl_field.get().strip()
        amenity_val = amenity_field.get().strip()

        # --- Validation ---
        errors = []

        if not name_val:
            errors.append("Name is required.")
        if not details_val:
            errors.append("Details are required.")
        if not rate_val:
            errors.append("Rate is required.")
        if not sqft_val:
            errors.append("Sqft is required.")
        if not occupancy_val:
            errors.append("Occupancy is required.")
        if not imageurl_val:
            errors.append("Image URL is required.")

        # Numeric checks
        try:
            rate_val = float(rate_val)
        except ValueError:
            errors.append("Rate must be a valid number.")

        try:
            sqft_val = int(sqft_val)
        except ValueError:
            errors.append("Sqft must be a valid integer.")

        try:
            occupancy_val = int(occupancy_val)
        except ValueError:
            errors.append("Occupancy must be a valid integer.")

        # URL format basic check (optional)
        if imageurl_val and not (
            imageurl_val.startswith("http://") or imageurl_val.startswith("https://")
        ):
            errors.append("Image URL must start with http:// or https://")

        if errors:
            showerror("Validation Error", "\n".join(errors))
            return

        # --- API Call ---
        try:
            api_response = create_villa_through_api(
                name_val,
                details_val,
                rate_val,
                sqft_val,
                occupancy_val,
                imageurl_val,
                amenity_val,
            )

            if api_response == 201:
                global modified, sheet
                modified = True
                showinfo(title="Success", message="Villa created successfully")

                if "sheet" in globals() and sheet is not None:
                    root.destroy()  # close the window
                    reload_villas()

            elif api_response is not None:
                raise ValueError(
                    f"An API error occurred with status code {api_response}"
                )
            else:
                raise requests.exceptions.RequestException

        except requests.exceptions.RequestException:
            showerror(
                title="Error",
                message="A network error occurred. Please check your internet connection.",
            )

        except ValueError as e:
            showerror(title="Error", message=str(e))

        except Exception:
            showerror(title="Error", message="An unexpected error occurred.")
            logging.exception("An unexpected error occurred in the insert() function.")

    # create a text entry box
    # for typing the information
    name_field = tk.Entry(root)
    details_field = tk.Entry(root)
    rate_field = tk.Entry(root)
    sqft_field = tk.Entry(root)
    occupancy_field = tk.Entry(root)
    imageurl_field = tk.Entry(root)
    amenity_field = tk.Entry(root)

    # Bind validation to all fields
    name_field.bind("<KeyRelease>", validate_fields)
    details_field.bind("<KeyRelease>", validate_fields)
    rate_field.bind("<KeyRelease>", validate_fields)
    occupancy_field.bind("<KeyRelease>", validate_fields)
    sqft_field.bind("<KeyRelease>", validate_fields)
    imageurl_field.bind("<KeyRelease>", validate_fields)

    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure .
    name_field.grid(row=1, column=1, ipadx="80")
    details_field.grid(row=2, column=1, ipadx="80")
    rate_field.grid(row=3, column=1, ipadx="80")
    sqft_field.grid(row=4, column=1, ipadx="80")
    occupancy_field.grid(row=5, column=1, ipadx="80")
    imageurl_field.grid(row=6, column=1, ipadx="80")
    amenity_field.grid(row=7, column=1, ipadx="80")

    # Label to show validation error messages
    validation_message = tk.Label(root, text="", fg="red", font=("Arial", 9))
    validation_message.grid(row=8, column=0, columnspan=2, pady=(10, 0))

    # Submit button
    submit = ttk.Button(root, text="Submit", command=insert, state="disabled")
    submit.grid(row=8, column=2)

    # start the GUI
    root.mainloop()


def find_villa():
    new_root = tk.Tk()

    # config the root window
    new_root.geometry("350x250")
    new_root.resizable(False, False)
    new_root.title("Search for villas")

    # label
    label = ttk.Label(new_root, text="Enter id: ")
    label.pack(fill=tk.X, padx=5, pady=5)

    id_field = tk.Entry(new_root)

    id_field.pack(ipadx=120)

    validation_label = tk.Label(new_root, text="", fg="red")
    validation_label.pack()

    def mark_valid(widget, valid):
        widget.configure(bg="white" if valid else "#ffdddd")

    def validate_id(*args):
        value = id_field.get().strip()
        is_valid = value.isdigit() and int(value) > 0
        mark_valid(id_field, is_valid)
        validation_label.config(
            text="" if is_valid else "ID must be a positive integer"
        )
        search_button.config(state="normal" if is_valid else "disabled")

    def search():
        query = id_field.get()

        villa = get_villa_through_api(query)

        if villa is not None:
            if villa["status"] == 200:
                v = villa["result"]
                createdDate = datetime.datetime.fromisoformat(
                    v["createdDate"]
                ).strftime("%Y-%m-%d %I:%M:%S %p")
                updatedDate = datetime.datetime.fromisoformat(
                    v["updatedDate"]
                ).strftime("%Y-%m-%d %I:%M:%S %p")
                output = (
                    f"ID: {v['id']}\nName: {v['name']}\nDetails: {v['details']}\n"
                    f"Rate: {v['rate']}\nSqft: {v['sqft']}\nOccupancy: {v['occupancy']}\n"
                    f"Image URL: {v['imageUrl']}\nAmenity: {v['amenity']}\n"
                    f"Created Date: {createdDate}\nUpdated Date: {updatedDate}"
                )
                showinfo(title="Record found", message=output)
            elif villa["status"] == 404:
                showerror(title="Error", message="Cannot find data")
            else:
                showerror(
                    title="Error", message=f"API returned status code {villa['status']}"
                )
        else:
            showerror(title="Error", message=f"Unable to access API")

    id_field.bind("<KeyRelease>", validate_id)

    search_button = ttk.Button(new_root, text="Search", command=search, state="disabled")

    search_button.pack(expand=True)
    # run the app
    new_root.mainloop()


def delete_villa():
    new_root = tk.Tk()

    # config the root window
    new_root.geometry("350x250")
    new_root.resizable(False, False)
    new_root.title("Delete villa")

    # label
    label = ttk.Label(new_root, text="Enter id: ")
    label.pack(fill=tk.X, padx=5, pady=5)

    id_field = tk.Entry(new_root)

    id_field.pack(ipadx=120)

    validation_label = tk.Label(new_root, text="", fg="red")
    validation_label.pack()

    def mark_valid(widget, valid):
        widget.configure(bg="white" if valid else "#ffdddd")

    def validate_id(*args):
        value = id_field.get().strip()
        is_valid = value.isdigit() and int(value) > 0
        mark_valid(id_field, is_valid)
        validation_label.config(
            text="" if is_valid else "ID must be a positive integer"
        )
        delete_button.config(state="normal" if is_valid else "disabled")

    def delete():
        query = id_field.get()

        result = delete_villa_through_api(query)

        if result == 204:
            global modified, sheet
            modified = True

            showinfo(title="Success", message="Deleted successfully")

            if "sheet" in globals() and sheet is not None:
                new_root.destroy()  # close the window
                reload_villas()
        else:
            showerror(title="Error", message="Unable to delete")

    id_field.bind("<KeyRelease>", validate_id)

    delete_button = ttk.Button(new_root, text="Delete", command=delete, state="disabled")

    delete_button.pack(expand=True)
    # run the app
    new_root.mainloop()


def update_villa():
    showinfo(
        title="Update villa",
        message="Please enter the requested information to update a villa",
    )

    # create a GUI window
    root = tk.Tk()

    # set the title of GUI window
    root.title("Update existing villa")

    # set the configuration of GUI window
    root.geometry("550x450")

    root.resizable(False, False)

    # create labels
    # create an ID label
    id = ttk.Label(root, text="ID", justify=tk.LEFT, padding=15)

    # create a Name label
    name = ttk.Label(root, text="Name", justify=tk.LEFT, padding=15)

    # create a Details label
    details = ttk.Label(root, text="Details", justify=tk.LEFT, padding=15)

    # create a Rate label
    rate = ttk.Label(root, text="Rate", justify=tk.LEFT, padding=15)

    # create a Sqft label
    sqft = ttk.Label(root, text="Sqft", justify=tk.LEFT, padding=15)

    # create a Occupancy label
    occupancy = ttk.Label(root, text="Occupancy", justify=tk.LEFT, padding=15)

    # create a imageUrl label
    imageurl = ttk.Label(root, text="Image URL", justify=tk.LEFT, padding=15)

    # create a amenity label
    amenity = ttk.Label(root, text="Amenity", justify=tk.LEFT, padding=15)

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

    def mark_valid(widget, is_valid):
        widget.configure(background="white" if is_valid else "#ffdddd")

    def validate_fields(*args):
        id_val = id_field.get().strip()
        name_val = name_field.get().strip()
        details_val = details_field.get().strip()
        rate_val = rate_field.get().strip()
        sqft_val = sqft_field.get().strip()
        occupancy_val = occupancy_field.get().strip()
        imageurl_val = imageurl_field.get().strip()

        message = ""
        is_valid = True

        # Field checks (in priority order for UX)
        if not id_val:
            message = "ID is required."
            is_valid = False
        elif not id_val.isdigit():
            message = "ID must be an integer."
            is_valid = False
        if not name_val:
            message = "Name is required."
            is_valid = False
        elif not details_val:
            message = "Details are required."
            is_valid = False
        elif not rate_val.replace(".", "", 1).isdigit() or not rate_val:
            message = "Rate must be a number."
            is_valid = False
        elif not sqft_val.isdigit() or not sqft_val:
            message = "Sqft must be an integer."
            is_valid = False
        elif not occupancy_val.isdigit() or not occupancy_val:
            message = "Occupancy must be an integer."
            is_valid = False
        elif (
            imageurl_val
            and not imageurl_val.startswith("http://")
            and not imageurl_val.startswith("https://")
        ):
            message = "Image URL must start with http:// or https://"
            is_valid = False

        # Highlight fields based on their individual validity
        mark_valid(id_field, id_val.isdigit() and bool(id_val))
        mark_valid(name_field, bool(name_val))
        mark_valid(details_field, bool(details_val))
        mark_valid(
            rate_field, rate_val.replace(".", "", 1).isdigit() and bool(rate_val)
        )
        mark_valid(sqft_field, sqft_val.isdigit() and bool(sqft_val))
        mark_valid(occupancy_field, occupancy_val.isdigit() and bool(occupancy_val))
        mark_valid(
            imageurl_field,
            not imageurl_val
            or imageurl_val.startswith("http://")
            or imageurl_val.startswith("https://"),
        )

        # Show or clear message
        validation_message.config(text=message)
        submit.config(state="normal" if is_valid else "disabled")

    def update():
        id_val = id_field.get().strip()
        name_val = name_field.get().strip()
        details_val = details_field.get().strip()
        rate_val = rate_field.get().strip()
        sqft_val = sqft_field.get().strip()
        occupancy_val = occupancy_field.get().strip()
        imageurl_val = imageurl_field.get().strip()
        amenity_val = amenity_field.get().strip()

        errors = []

        if not id_val:
            errors.append("ID is required.")
        if not name_val:
            errors.append("Name is required.")
        if not details_val:
            errors.append("Details are required.")
        if not rate_val:
            errors.append("Rate is required.")
        if not sqft_val:
            errors.append("Sqft is required.")
        if not occupancy_val:
            errors.append("Occupancy is required.")
        if not imageurl_val:
            errors.append("Image URL is required.")

        try:
            int(id_val)
        except ValueError:
            errors.append("ID must be a valid integer.")

        try:
            rate_val = float(rate_val)
        except ValueError:
            errors.append("Rate must be a valid number.")

        try:
            sqft_val = int(sqft_val)
        except ValueError:
            errors.append("Sqft must be a valid integer.")

        try:
            occupancy_val = int(occupancy_val)
        except ValueError:
            errors.append("Occupancy must be a valid integer.")

        if imageurl_val and not (
            imageurl_val.startswith("http://") or imageurl_val.startswith("https://")
        ):
            errors.append("Image URL must start with http:// or https://")

        if errors:
            showerror("Validation Error", "\n".join(errors))
            return

        result = update_villa_through_api(
            id_val,
            name_val,
            details_val,
            rate_val,
            occupancy_val,
            sqft_val,
            imageurl_val,
            amenity_val,
        )

        if result == 204:
            global modified
            modified = True

            showinfo(title="Success", message="Updated successfully")

            if "sheet" in globals() and sheet is not None:
                root.destroy()  # close the window
                reload_villas()
        else:
            showerror(title="Error", message="Unable to update")

    # create a text entry box
    # for typing the information
    id_field = tk.Entry(root)
    name_field = tk.Entry(root)
    details_field = tk.Entry(root)
    rate_field = tk.Entry(root)
    sqft_field = tk.Entry(root)
    occupancy_field = tk.Entry(root)
    imageurl_field = tk.Entry(root)
    amenity_field = tk.Entry(root)

    # Bind validation to all fields
    id_field.bind("<KeyRelease>", validate_fields)
    name_field.bind("<KeyRelease>", validate_fields)
    details_field.bind("<KeyRelease>", validate_fields)
    rate_field.bind("<KeyRelease>", validate_fields)
    sqft_field.bind("<KeyRelease>", validate_fields)
    occupancy_field.bind("<KeyRelease>", validate_fields)
    imageurl_field.bind("<KeyRelease>", validate_fields)
    amenity_field.bind("<KeyRelease>", validate_fields)

    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure .
    id_field.grid(row=1, column=1, ipadx="80")
    name_field.grid(row=2, column=1, ipadx="80")
    details_field.grid(row=3, column=1, ipadx="80")
    rate_field.grid(row=4, column=1, ipadx="80")
    sqft_field.grid(row=5, column=1, ipadx="80")
    occupancy_field.grid(row=6, column=1, ipadx="80")
    imageurl_field.grid(row=7, column=1, ipadx="80")
    amenity_field.grid(row=8, column=1, ipadx="80")

    # Label to show validation error messages
    validation_message = tk.Label(root, text="", fg="red", font=("Arial", 9))
    validation_message.grid(row=9, column=0, columnspan=2, pady=(10, 0))

    submit = ttk.Button(root, text="Update", command=update)
    submit.grid(row=9, column=2)

    # start the GUI
    root.mainloop()


def update_partial_villa():
    showinfo(
        title="Update partial villa",
        message="Please enter the ID as well as tick the checkboxes and enter values to update a villa",
    )

    # Create dictionaries to store the checkbox values and text entry fields
    checkbox_values = {}
    entry_fields = {}

    def update():
        # Retrieve the values from the checkboxes and text entry fields
        selected_values = []
        single_value = {}
        for label_text, var in checkbox_values.items():
            value = var.get()  # Get the value of the IntVar
            entry_text = entry_fields[
                label_text
            ].get()  # Get the value of the corresponding text entry field
            if value == 1 and entry_text != "":
                single_value = {"label_text": label_text, "entry_text": entry_text}
                selected_values.append(single_value)
        print(selected_values)

        if selected_values == []:
            showerror(title="Error", message="Nothing has been selected")
        elif selected_values[0]["label_text"] != "ID":
            showerror(title="Error", message="Please enter an ID")

        if selected_values != []:
            id = selected_values[0]["entry_text"]

        only_id = True  # Assume only 'ID' is selected
        for single_val in selected_values:
            if single_val["label_text"] != "ID":
                only_id = False  # Found a label other than 'ID'
                break  # No need to continue checking

        print("Checkbox values:", {k: v.get() for k, v in checkbox_values.items()})
        print("Entry values:", {k: entry_fields[k].get() for k in entry_fields})

        if only_id:
            showerror(title="Error", message="Please select other entities")
            return

        errors = []

        if not selected_values:
            showerror("Validation Error", "Nothing selected.")
            return

        if selected_values[0]["label_text"] != "ID":
            showerror("Validation Error", "ID must be selected and provided.")
            return

        id_val = selected_values[0]["entry_text"].strip()
        try:
            int(id_val)
        except ValueError:
            showerror("Validation Error", "ID must be a valid integer.")
            return

        # Check if only ID is selected
        if len(selected_values) == 1:
            showerror("Validation Error", "Please select other entities to update.")
            return

        # Validate fields based on label
        for item in selected_values[1:]:  # skip ID
            label = item["label_text"]
            val = item["entry_text"].strip()
            if label in ("Rate", "Sqft", "Occupancy"):
                try:
                    if label == "Rate":
                        float(val)
                    else:
                        int(val)
                except ValueError:
                    errors.append(f"{label} must be a valid number.")
            if (
                label == "Image URL"
                and val
                and not val.startswith(("http://", "https://"))
            ):
                errors.append("Image URL must start with http:// or https://")

        if errors:
            showerror("Validation Error", "\n".join(errors))
            return

        queryparams = []
        if not only_id and selected_values:
            id = selected_values[0]["entry_text"]

            for index, single_val in enumerate(selected_values):
                if index == 0:
                    continue  # Skip the first element

                label_text = single_val["label_text"]
                entry_text = single_val["entry_text"]
                queryparams.append(
                    {
                        "op": "replace",
                        "path": f"/{label_text.lower()}",
                        "value": entry_text,
                    }
                )

            response = update_partial_villa_through_api(id, queryparams)

            if response == 204:
                global modified
                modified = True

                showinfo(title="Success", message="Updated successfully")

                if "sheet" in globals() and sheet is not None:
                    new_root.destroy()  # close the window
                    reload_villas()
            else:
                showerror(title="Error", message="Unable to update")

    # Create a new window as a child of root
    new_root = tk.Toplevel(app)
    new_root.title("Update existing villa")
    new_root.geometry("550x450")
    new_root.resizable(False, False)

    # Function to create a checkbox and label pair
    def create_checkbox_label_pair(row, label_text, always_checked=False):
        var = tk.IntVar()
        if always_checked:
            var.set(1)  # Set the value of the IntVar to 1 (checked)
            checkbox = ttk.Checkbutton(new_root, variable=var, state="disabled")
        else:
            checkbox = ttk.Checkbutton(new_root, variable=var)
        checkbox.grid(row=row, column=0, sticky="w")
        checkbox_values[label_text] = var
        ttk.Label(new_root, text=label_text, justify=tk.LEFT, padding=15).grid(
            row=row, column=1, sticky="w"
        )

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
    sqft_field.grid(row=5, column=2, padx=5, ipadx="125")
    occupancy_field.grid(row=6, column=2, padx=5, ipadx="125")
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
    global app
    app.destroy()


list_villas_button = ttk.Button(
    app, text="Show all villas through API", command=show_villas
)
create_villa_button = ttk.Button(app, text="Create a new villa", command=create_villa)
search_villa_button = ttk.Button(app, text="Find vila through API", command=find_villa)
delete_villa_button = ttk.Button(
    app, text="Delete villa through API", command=delete_villa
)

update_villa_button = ttk.Button(
    app, text="Update villa through API", command=update_villa
)

update_partial_villa_button = ttk.Button(
    app, text="Update partial villa through API", command=update_partial_villa
)

quit_button = ttk.Button(app, text="Close", command=close)

list_villas_button.pack(expand=True)
create_villa_button.pack(expand=True)
search_villa_button.pack(expand=True)
delete_villa_button.pack(expand=True)
update_villa_button.pack(expand=True)
update_partial_villa_button.pack(expand=True)
quit_button.pack(expand=True)

app.protocol("WM_DELETE_WINDOW", close)

# run the app
app.mainloop()
