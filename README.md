# Simpel-Invoice-Generator-
Simpel Invoice Generator for small business
How to run it (quick)

Make sure you have Python 3 installed.

Install required packages:

pip install reportlab pillow


Open the canvas file named Invoice Desktop App and save the code locally as invoice_desktop_app.py.

(Optional) Put your logo file in the same folder or use the app's Load Logo button.

Run:

python invoice_desktop_app.py


Notes & tips

Default currency is USD — change the CURRENCY variable at top of the script (e.g., to LKR or Rs) if you want another symbol.

Default filename uses a timestamp to avoid overwriting.

The app writes invoices as PDF; you can preview, print, or email them
