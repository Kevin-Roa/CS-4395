import sys
import os
import re
import pickle


# Class to hold employee data
class Person:
    def __init__(self, data):
        self.last = data[0].capitalize()
        self.first = data[1].capitalize()
        self.mi = data[2].capitalize()
        self.id = data[3]
        self.phone = data[4]

    # Display employee data
    def display(self):
        print(f"Employee id: {self.id}")
        print(f"    {self.first} {self.mi} {self.last}")
        print(f"    {self.phone}\n")


# Read the employee csv file at the given path 
# Transform the data into the new format
# Perform validation on the data, correcting any errors
# Return a dictionary of employees
def processFile(filePath):
    employees = {}
    with open(os.path.join(os.getcwd(), filePath), "r") as f:
        for line in f.readlines()[1:]:
            data = line.split(",")
            data[0] = data[0].capitalize().strip()
            data[1] = data[1].capitalize().strip()
            data[2] = validateMi(data[2].strip())
            data[3] = validateId(data[3].strip(), employees)
            data[4] = validatePhone(data[4])

            employees[data[3]] = Person(data)

    return employees


# Save the employee dictionary to a pickle file
def saveFile(filePath, employees):
    path = os.path.splitext(filePath)[0] + ".pkl"
    pickle.dump(employees, open(os.path.join(os.getcwd(), path), "wb"))


# Read the pickle file
# Load the data into a dictionary
# Display the employee list
def readFile(filePath):
    path = os.path.splitext(filePath)[0] + ".pkl"
    employees = pickle.load(open(os.path.join(os.getcwd(), path), "rb"))
    displayEmployeeList(employees)


# Loop through the given dictionary of employees and display them
def displayEmployeeList(employees):
    print("\nEmployee list:\n")
    for id in employees:
        employees[id].display()


# Validate the middle initial
# Ensure it is a single capital letter
def validateMi(mi):
    # Check if the middle initial is valid
    if re.match("^[a-zA-Z]$", mi):
        return mi.capitalize()

    # Check if the middle initial is empty
    str = re.sub("[0-9]", "", mi)  # remove numbers
    if len(str) == 0:
        return "X"

    # Take first letter of middle name
    return str[0].capitalize()


# Validate the employee id
# Ensure it is two letters followed by four digits
# Ensure it is unique
# Prompt the user to enter a new id if it invalid or not unique
def validateId(id, employees):
    # Check if the id is unique
    if id.upper() in employees:
        print("test2")
        print("Employee id already exists: " + id)
        return validateId(input("Please enter a valid id: "), employees)

    # Check if the id is valid
    if re.match("^[a-zA-Z]{2}[0-9]{4}$", id):
        return id.upper()

    # On invalid id, prompt the user to enter a new id
    print("ID invalid: " + id)
    print("ID is two letters followed by four digits")
    return validateId(input("Please enter a valid id: "), employees)


# Validate the phone number
# Ensure it is in the form 123-456-7890
# Correct any errors if possible
def validatePhone(phone):
    if re.match("^[0-9]{3}-[0-9]{3}-[0-9]{4}$", phone):
        return phone

    nums = re.sub("\D", "", phone)  # remove non-numbers
    if len(nums) == 10:
        return nums[:3] + "-" + nums[3:6] + "-" + nums[6:]

    print("Phone number invalid: " + phone)
    print("Enter phone number in form 123-456-7890")
    return validatePhone(input("Please enter a valid phone number: "))


# Process the file given in the command line arguments
# Save the data to a pickle file
# Read the pickle file and display the data
def main(filePath):
    employees = processFile(filePath)
    saveFile(filePath, employees)
    readFile(filePath)


# Run the main function if this file is run directly
if __name__ == "__main__":
    # Check if the file path was given in the command line arguments
    if len(sys.argv) < 2:
        print("Please provide an input file.")
        exit()
        
    main(sys.argv[1])
