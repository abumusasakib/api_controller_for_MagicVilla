from dateutil import parser

userInput = input("Enter a date/time: ")

dt_obj = parser.parse(userInput)

updatedDate = dt_obj.strftime(
                    "%Y-%m-%d %I:%M:%S %p")
print(updatedDate)