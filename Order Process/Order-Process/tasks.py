from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables
from RPA.Archive import Archive




@task
def order_robots_from_RobotSpareBin():
    """Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=200,
    )
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
    archive_receipts()       



def open_robot_order_website():
        """Navigates to the given URL"""
        browser.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders():
     http = HTTP()
     http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
     workbook = Tables()       
     return workbook.read_table_from_csv(
    "orders.csv" 
    )

def close_annoying_modal():

    page = browser.page()  
    page.click("text=OK")

def fill_the_form(row):
     page = browser.page()
     page.select_option("#head",str(row["Head"]))
     page.click("#id-body-"+str(row["Body"]))     
     page.get_by_placeholder("Enter the part number for the legs").fill(str(row["Legs"]))     
     page.fill("#address",str(row["Address"]))
     page.click("text=Preview")
     
     while True:
             
        page.click("#order")
        order_another_exists = page.query_selector("#order-another")
        if order_another_exists:
             pdf_file = store_receipt_as_pdf(str(row["Order number"]))
             screenshot = screenshot_robot(str(row["Order number"]))
             embed_screenshot_to_receipt(screenshot,pdf_file)
             page.click("text=Order another robot")
             break
        
def store_receipt_as_pdf(order_number):
     page = browser.page()
     order_receipt_html = page.locator("#receipt").inner_html()
     pdf = PDF()
     pdf_path = "output/receipts/{0}.pdf".format(order_number)
     pdf.html_to_pdf(order_receipt_html,pdf_path)
     return pdf_path

def screenshot_robot(order_number):
     page = browser.page()
     screenshot_path = "output/receipts/{0}.png".format(order_number)
     page.screenshot(path=screenshot_path)
     return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
     pdf = PDF()
     pdf.add_watermark_image_to_pdf(
          image_path= screenshot,
          source_path= pdf_file,
          output_path= pdf_file            
        )
     
def archive_receipts():
     lib = Archive()
     lib.archive_folder_with_zip('./output/receipts', './output/receipts.zip', include='*.pdf')