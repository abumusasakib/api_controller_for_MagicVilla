# api_controller_for_MagicVilla

An GUI based API Controller for MagicVilla_VillaAPI made using Python and done by me. This project demostrates how various types of API calls can be done to manipulate data of a database.

## Dependencies

1. **datetime**, **time**
2. **Microsoft SQL Server Management Studio (SSMS)** (for the ms sql server)

    * Install from **<https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16>** *

3. **Microsoft Visual Studio 2022** (for running the MagicVilla_API)
4. **os** (for opening files)
5. **sys** (for checking platform)
6. **tkinter** (for GUI)
7. **prettytable** (for report generation)
8. **requests**, **json** (for accessing DotNetMastery's MagicVilla_VillaAPI)
9. **pdfkit**, **wkhtmltopdf** (for converting html to pdf) (install from **<https://wkhtmltopdf.org/downloads.html>**)

## How to Run

1. Install Python and the dependencies
2. Download DotNetMastery's MagicVilla_VillaAPI project from **<https://github.com/bhrugen/MagicVilla_API/tree/master/MagicVilla_VillaAPI>** and make necessary setups.
3. Open Microsoft Visual Studio 2022 and run the project. Make sure that the API is running at localhost, port 7155.
4. Run "magicvilla_api_controller.py"

## File Structure

1. **villa_data.json** - json file generated after data is fetched from the API
2. **villas.html** - html file generated by prettytable containing the list of villas
3. **villas.pdf** - converted pdf file of "villas.html"
4. **api_controller_for_MagicVilla.code-workspace** - generated by Visual Studio Code
5. **villa.log** - text file containing the log of the API controller

## Contributor: **Abu Musa Sakib**