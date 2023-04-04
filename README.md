<https://cs50.harvard.edu/x/2023/project/>
# PharmDooz
#### Video Demo:  <https://youtu.be/8rk2m9ECqKc>
## General description
**PharmDooz** is a web-based application dedicated to pharmacists for pharmaceutical care. It enables recording patient data and creating a patient database with past and present questionnaires.

It is dedicated to pharmacists working in pharmacies, hospital pharmacies and performing pharmaceutical care as independent pharmacists.

After creating a patient profile, the user can fill out the individual pharmaceutical care plan (Indywidualny Plan Opieki Farmaceutycznej - IPOF) which is a standard questionnaire suggested by the Polish pharmaceutical care team.

The questionnaire consists of three parts:
1. patient data (age, weight, health condition, etc.)
2. patient's assessment of their overall health condition and patient's medications
3. pharmacist's notes, care plan, interventions and case summary.

You can create an account:
- username cannot be taken,
- password must pass a security check.
When you log in, you can change your password.

You're able to add patients and fill out questionnaires for them. Each questionnaire can be edited or deleted. Some fields of the questionnaire are required and before sending the form, it is validated.

You can view the patient's profile with the brief overview of the latest questionnaire. The list of all patient's questionnaires is sorted by date and you can access it by clicking the "Wypełnione formularze" button.

## Technical part
Per CS50x requirements, here is a description of what each of the files I wrote for the project contains and does.
### Javascript, jQuery
I used jQuery library.\
In *myscript.js* there are:
- function that enables checkboxes (default: disabled) with medical specializations when number of doctors suprvising a patient is greater than 0
- function that enables/disables select box with cigarettes smoking and alcohol drinking frequency
- function creating a new section for another medicine when the "Add medicine" button is clicked
- bootstrap functionality that checks form's validity
- bootstrap functionality: scrollspy when you fill out the form


### CSS, Bootstrap v5
I mainly used Bootstrap v5, but there is also my own css file.\
*styles.css* is used to style: nav bar's colours, some headings, buttons and tables.

### HTML
Based on Jinja2 and my template *layout.html*, I created another 10 html files. In templates folder there is:\
 - *layout.html* which is a template with head and body tag. Inside body tag there is a navigation header, optional flashed messages, main block and a footer.
 - *register.html* -> displays a form to create a new account
 - *login.html* -> displays a form to log into your account
 - *index.html* -> it's a main page with the list of your patients
 - *addpatient.html* -> displays a form to add a new patient
 - *patient.html* -> patient's profile with the short version of the latest questionnaire (if exists)
 - *newform.html* -> displays a new questionnaire
 - *view_form.html* -> shows a full version of a patient's questionnaire
 - *edit.html* -> it's a page with a filled out questionnaire but each field can be edited
 - *change_password.html* -> contains a form to change your password
 - *apology.html* -> shows an apology when unauthorized access was prevented

### Python, Flask
*helpers.py* contains three functions:
- apology: uses [meme gen](https://github.com/jacebrowning/memegen) and renders message as an apology to the user
- [login_required](https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
): decorates routes to require login
- secure_password: returns True if password is secure, otherwise returns False. You can set your own password requirements such as minimum length, number of digits and uppercase/special characters.

In *app.py* I manage my website's paths, check corectness of provided data, prevent any malicious input (e.g. you can't view other user's patients, their forms nor edit anything that doesn't belong to your account) and insert/update/delete and select records from database.

### SQL, sqlite3
Database stores users, patients, questionnaires, each medicine taken by a patient and different options that are later available to choose while filling out a questionnaire (in select boxes, checkboxes etc.).

There are 13 different tables with primary and foreign keys.
![](https://github.com/chlorin3/pharmdooz-project/blob/main/db-diagram.png)
### Changing password
<img src="https://github.com/chlorin3/pharmdooz-project/blob/main/change-password-kopia.gif" width=800>

### Form validation
<img src="https://github.com/chlorin3/pharmdooz-project/blob/main/form-validation-kopia.gif" width=800>

### Form edition
<img src="https://github.com/chlorin3/pharmdooz-project/blob/main/login-edit-form-kopia.gif" width=800>
<img src="https://github.com/chlorin3/pharmdooz-project/blob/main/pharmdooz-username-kopia.gif" width=800>

### Responsiveness
<img src="https://github.com/chlorin3/pharmdooz-project/blob/main/responsive-1.gif" width=800>
<img src="https://github.com/chlorin3/pharmdooz-project/blob/main/responsive-2.gif" width=800>
<img src="https://github.com/chlorin3/pharmdooz-project/blob/main/responsive-form.gif" width=500>

### Unauthorized access
<img src="https://github.com/chlorin3/pharmdooz-project/blob/main/unauthorized-access-kopia.gif" width=800>
<img src="https://github.com/chlorin3/pharmdooz-project/blob/main/unauthorized-access-2-kopia.gif" width=800>
