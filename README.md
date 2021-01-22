# assembla_validation_gui
Gui for validating apps in realtime

Note: after performing the complete app and including the attachements then run this program.

- Initial step:
install the below modules, run below commands in cmd:

pip install assembla



- Step 1: create a file named as "creds_personal.py"
place your assembla secret keys inside it, for example:

access_key= "xxxxxxxxxxxxxxxxxxxxxxxxx";

access_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";

-- To create assembla secret keys: go to your assembla:

-- Now go to profile from settings.

-- select "API Applications & Sessions", in this tab "Register new personal key".

-- check the "API access" and "Repository access".

By following above method you will get your access and secret keys.


- Step 2: place this "creds_personal.py" in the same directory where you are cloning this.


- Step 3: double click on "run.bat" to run the program.


This takes gc code as an input (it should be integer value), and if errors are found, it will write in json file and show the error message as popup.

The validation code includes the following validations for assembla inputs:

Below is the list of validations it entertains:


* Attachments names against each activity.

* Http version field.

* Personal vs Corporate.

* Http host (pattern matching).

* Http uri path (pattern matching).

* Login-LoginFail depth verification.

* Response field only be filled for login and login-fail.

* Response should not be filled for another activity.

* Multiple Request methods, then all fields will be of same size.

* Request method should not be empty.

* If request method is NA or REMAINING then all fields should be empty.

* If request method is filled then atleast host should be filled.

* Attachments counts should be same as the activities performed.

