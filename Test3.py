

import os
import clr
import logging
import datetime
import io
import tkinter as tk
from tkinter import Text, Button, Scrollbar, messagebox, PhotoImage

# Add references to the required DLL files
clr.AddReference('System')
clr.AddReference('C:/Users/hamza/OneDrive/Desktop/Test3/SDK/Newtonsoft.Json.dll')
clr.AddReference('C:/Users/hamza/OneDrive/Desktop/Test2/IXMDemo.Common.dll')
clr.AddReference('C:/Users/hamza/OneDrive/Desktop/Test2/IXMSoft.Business.Managers.dll')
clr.AddReference('C:/Users/hamza/OneDrive/Desktop/Test2/IXMSoft.Business.SDK.dll')
clr.AddReference('C:/Users/hamza/OneDrive/Desktop/Test2/IXMSoft.Common.Models.dll')
clr.AddReference('C:/Users/hamza/OneDrive/Desktop/Test2/IXMSoft.Data.DataAccess.dll')

# Import the necessary functions and classes from the DLLs using ctypes
from System import DateTime
from IXMSoft.Common.Models import TransactionLogArg, TransactionLog, Device
from IXMSoft.Common.Models import *
from IXMSoft.Business.SDK import *
from IXMSoft.Data.DataAccess import *
from IXMSoft.Business.SDK.Data import DeviceConnectionType, TransactionLogEventType
from IXMSoft.Business.SDK import NetworkConnection, TransactionLogManager, DeviceInfoManager 
from IXMSoft.Business.SDK.Commands import ITransactionLogArgs, ITransactionLog
from IXMSoft.Business.SDK.Commands import *

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_full_path(path):
    app_folder_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(app_folder_path, path)
    return path

def check_device_status(device):
    if device.IPaddress and device.Port:
        try:
            response = os.system(f"ping {device.IPaddress} -n 1")
            if response == 0:
                return True
        except Exception as ex:
            logging.error(f"Error checking device status: {ex}")
    return False

# Define a function to display the logs in a GUI window
def show_logs(logs):
    log_window = tk.Toplevel()
    log_window.title("Log Viewer")

    log_text = Text(log_window, wrap=tk.WORD, width=60, height=20)
    log_text.pack(fill=tk.BOTH, expand=True)

    scrollbar = Scrollbar(log_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=log_text.yview)

    for log in logs:
        log_str = ";".join([str(log['UserRecordId']), log['check_date'], log['check_time']])
        log_text.insert(tk.END, log_str + "\n")

# Define a function to restart the device
def restart_device():
    # Add code here to restart the device
    logging.info("Device restarted")
    messagebox.showinfo("Device Restarted", "The device has been restarted successfully.")

def get_transaction_logs(conn, start_date_dotnet, end_date_dotnet):
    print(conn)
    print()
    print("we will start TransactionLogManager")
    log_data = TransactionLogManager(conn)
    print("we will start TransactionLogArg with {0},{1}".format(start_date_dotnet, end_date_dotnet))

    transaction_log_arguments = TransactionLogArg()
    transaction_log_arguments.StartDate = start_date_dotnet
    transaction_log_arguments.EndDate = end_date_dotnet
    print(transaction_log_arguments.StartDate)

    transaction_logs = []
    try:
        device_info_manager = DeviceInfoManager(conn)
        # to restart the device uncomment the below line
        # device_info_manager.RebootDeviceGracefully()
        print("we will start GetAllDateWiseTransactionLogCount")

        all_log_counter = log_data.GetAllDateWiseTransactionLogCount(
            transaction_log_arguments.StartDate,
            transaction_log_arguments.EndDate
        )

        print("we will start count is : {0}".format(all_log_counter))

        if all_log_counter > 0:
            for i in range(0, all_log_counter, 100):
                transaction_log_arguments.StartCounter = i
                transaction_log_arguments.EndCounter = i + 100
                datawise = log_data.GetDateWiseTransactionLog(transaction_log_arguments)

                for item in datawise:
                    if item.EventType == TransactionLogEventType.Authentication:
                        std_log_data = {}
                        std_log_data["UserRecordId"] = item.UserId if item.UserId else None
                        std_log_data["check_date"] = item.Date.ToShortDateString()
                        std_log_data["check_time"] = item.Time

                        if std_log_data is not None:
                            transaction_logs.append(std_log_data)

    except Exception as ex:
        print("InshAllah will work")
        conn.CloseConnection()
        conn.Dispose()
    return transaction_logs

def main():
    # Create the main GUI window
    root = tk.Tk()
    root.title("Device Log Viewer")
    root.geometry("300x150")  # Set the window size to be smaller

    # Set the background color to black
    root.configure(bg="black")

    # Load the logo image
    logo_image = PhotoImage(file="CCDS.png")

    # Create a label to display the logo
    logo_label = tk.Label(root, image=logo_image, bg="black")
    logo_label.grid(row=0, column=0, columnspan=2)

    # Create a frame for buttons
    log_frame = tk.Frame(root, bg="black")  # Set background color
    log_frame.grid(row=1, column=0, columnspan=2, pady=10)

    # Create "Show Logs" button
    show_logs_button = Button(log_frame, text="Show Logs", command=lambda: show_logs(rows))
    show_logs_button.grid(row=0, column=0, padx=10)

    # Create "Restart Device" button
    restart_button = Button(log_frame, text="Restart Device", command=restart_device)
    restart_button.grid(row=0, column=1, padx=10)

    # Create a logs folder if it doesn't exist
    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    # Create Python datetime objects
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=1)

    # Convert Python datetime objects to System.DateTime objects
    start_date_dotnet = DateTime(start_date.year, start_date.month, start_date.day, start_date.hour, start_date.minute, start_date.second)
    end_date_dotnet = DateTime(end_date.year, end_date.month, end_date.day, end_date.hour, end_date.minute, end_date.second)
    file_name_date = end_date.strftime("%d_%m_%Y_%H_%M_%S")

    # Configure the device
    device = Device()
    device.IPaddress = "192.168.200.143"
    device.Port = "9734"
    device.ConnectionType = DeviceConnectionType.Ethernet

    logging.info(f"Checking device status for IP: {device.IPaddress}")
    status = check_device_status(device)
    logging.info(f"Device status: {status}")

    if status:
        rows = []  # Initialize an empty list to store transaction logs
        logging.info(f"Establishing a network connection to IP: {device.IPaddress}")
        conn = NetworkConnection(device)
        log_count = 0  # Initialize log_count here
        try:
            conn.OpenConnection()
            logging.info(f"Network connection established: {conn.OpenConnection()}")

            logging.info(f"Retrieving transaction logs for IP: {device.IPaddress} from {start_date_dotnet} to {end_date_dotnet}")
            # Update rows and log_count
            rows = get_transaction_logs(conn, start_date_dotnet, end_date_dotnet)
            log_count = len(rows)
            conn.CloseConnection()
            conn.Dispose()
        except Exception as ex:
            conn.CloseConnection()
            conn.Dispose()
            logging.error(f"Error during network communication: {ex}")

        # Print the count of logs
        logging.info(f"Total logs retrieved: {log_count}")

        # Save logs to a file
        log_path = f"{device.IPaddress}_{file_name_date}.txt"
        log_path = os.path.join(logs_folder, log_path)
        log_path = get_full_path(log_path)
        with open(log_path, 'w') as writer:
            writer.write("UserRecordId;check_date;check_time\n")  # Write header
            for row in rows:
                data = f"{row['UserRecordId']};{row['check_date']};{row['check_time']}"
                writer.write(data + '\n')

    # Check for auto close file
    auto_close = False
    auto_close_path = "auto_close.txt"
    auto_close_path = get_full_path(auto_close_path)
    if os.path.exists(auto_close_path):
        auto_close = True
    logging.info("Finished")

    # Start the GUI main loop
    if not auto_close:
        root.mainloop()

if __name__ == "__main__":
    main()