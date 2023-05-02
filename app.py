import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, secure_password

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION-PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///pharmdooz.db")

EDUCATION_OPT = [
        "Niepełne podstawowe",
        "Podstawowe",
        "Zawodowe",
        "Średnie",
        "Wyższe",
    ]

HEALTH_OPT = [
    "Bardzo dobra",
    "Dobra",
    "Średnia/Umiarkowana",
    "Zła",
]

SPEC_OPT = db.execute("SELECT * FROM specialization")

QUESTIONS = db.execute("SELECT * FROM open_ended_questions")

MEDICINE_CATEGORY = db.execute("SELECT * FROM medicine_category")

MEDICINE_SOURCES = db.execute("SELECT * FROM medicine_source")

MEDICINE_ADMINISTRATION = db.execute("SELECT * FROM medicine_administration")

MEDICINE_PROBLEM = db.execute("SELECT * FROM problem")

INTERVENTION_OPT = db.execute("SELECT * FROM intervention")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Portfolio of patients"""

    if request.method == "POST":
        return apology()
    else:
        patients = db.execute(
            "SELECT * FROM patients WHERE user_id = ?", session["user_id"]
        )
        return render_template("index.html", patients=patients)


@app.route("/addpatient", methods=["GET", "POST"])
@login_required
def addpatient():
    if request.method == "POST":
        if not (
            request.form.get("patientCode")
            and request.form.get("patientName")
            and request.form.get("patientSurname")
        ):
            return apology("TODO")

        # Patient's code should be unique in user's scope
        if db.execute(
            "SELECT patient_id FROM patients WHERE code = ? AND user_id = ?",
            request.form.get("patientCode"),
            session["user_id"],
        ):
            return apology("Patient's code already exists")

        """
            SPRAWDZIĆ POPRAWNOŚĆ DANYCH ale to potem
        """

        # Add new patient to db
        db.execute(
            "INSERT INTO patients(patient_name, patient_surname, code, user_id) " +
            "VALUES (?, ?, ?, ?)",
            request.form.get("patientName"),
            request.form.get("patientSurname"),
            request.form.get("patientCode"),
            session["user_id"],
        )

        patientCode = request.form.get("patientCode")
        # Redirect to new form
        return redirect(f"/patient/{patientCode}")
    else:
        return render_template("addpatient.html")


@app.route("/addform", methods=["POST"])
@login_required
def addform():
    """Let user add form"""

    # Check if required data was sent
    if not (
        request.form.get("sex")
        and request.form.get("age")
        and request.form.get("weight")
        and request.form.get("height")
        and request.form.get("education_level")
        and request.form.get("doctors_num")
        and request.form.get("health_status")
        and request.form.get("cigarettes")
        and request.form.get("alcohol")
        and request.form.getlist("medicineName")
        and request.form.getlist("medicineDate")
        and request.form.getlist("medicineAdministration")
        and request.form.getlist("medicineCategory")
        and request.form.getlist("medicineSource")
        and request.form.getlist("compliance")
    ):
        return apology("Missing fields!")

    patient = db.execute(
        "SELECT * FROM patients " +
        "WHERE patient_id = ? " +
        "AND code = ? " +
        "AND user_id = ?",
        request.form.get("patient_id"),
        request.form.get("patient_code"),
        session["user_id"],
    )

    if not patient:
        return apology("Patient does not exist")

    alcohol_freq = request.form.get("alcohol_freq")
    cigarettes_freq = request.form.get("cigarettes_freq")
    # If patient doesn't smoke/drink alcohol, change "None" values to ""
    if not alcohol_freq:
        alcohol_freq = ""
    if not cigarettes_freq:
        cigarettes_freq = ""

    # Add form to forms
    db.execute(
        "INSERT INTO forms(" +
        "age, sex, weight, height, doctors_num, " +
        "education_level, health_status, medical_diagnosis, " +
        "allergy, cigarettes_status, cigarettes_freq, " +
        "alcohol_status, alcohol_freq, " +
        "problem_id, problem_detail, intervention_id, intervention_detail, " +
        "therapeutic_effect_objective, therapeutic_effect_subjective, " +
        "side_effects, knowledge_est, " +
        "diagnosis, issue, goal, current_condition, intervention, recommendation, " +
        "patient_id, user_id) " +
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, " +
        "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, " +
        "?, ?, ?, ?, ?, ?, ?, ?, ?)",
        request.form.get("age"),
        request.form.get("sex"),
        request.form.get("weight"),
        request.form.get("height"),
        request.form.get("doctors_num"),
        request.form.get("education_level"),
        request.form.get("health_status"),
        request.form.get("medical_diagnosis"),
        request.form.get("allergy"),
        request.form.get("cigarettes"),
        cigarettes_freq,
        request.form.get("alcohol"),
        alcohol_freq,
        request.form.get("medicineProblem"),
        request.form.get("problemText"),
        request.form.get("medicineIntervention"),
        request.form.get("interventionText"),
        request.form.get("effect_obj"),
        request.form.get("effect_sub"),
        request.form.get("side_effect"),
        request.form.get("knowledge_est"),
        request.form.get("diagnosis"),
        request.form.get("issue"),
        request.form.get("goal"),
        request.form.get("condition"),
        request.form.get("intervention"),
        request.form.get("recommendation"),
        request.form.get("patient_id"),
        session["user_id"],
    )

    # Obtain form's id
    form_id = db.execute(
        "SELECT form_id FROM forms WHERE patient_id = ? " +
        "AND user_id = ? ORDER BY filled_date DESC LIMIT 1",
        request.form.get("patient_id"),
        session["user_id"],
    )[0]["form_id"]

    # Add information about medical supervision
    for id in request.form.getlist("specialization"):
        db.execute("INSERT INTO medical_supervision VALUES (?, ?)", id, form_id)

    # Add answers to open-ended questions
    for row in QUESTIONS:
        db.execute(
            "INSERT INTO open_ended_answers VALUES (?, ?, ?, ?)",
            form_id,
            row["question_id"],
            request.form.get("sub" + str(row["question_id"])),
            request.form.get("obj" + str(row["question_id"])),
        )

    # Add information about taken medicine to db
    for i in range(len(request.form.getlist("medicineName"))):
        db.execute(
            "INSERT INTO taken_medicine VALUES (?, ?, ?, ?, ?, ?, ?)",
            form_id,
            request.form.getlist("medicineName")[i],
            request.form.getlist("medicineDate")[i],
            request.form.getlist("medicineCategory")[i],
            request.form.getlist("medicineSource")[i],
            request.form.getlist("medicineAdministration")[i],
            request.form.getlist("compliance")[i],
        )

    flash("Pomyślnie dodano formularz!")
    return redirect(f"/patient/{ request.form.get('patient_code') }")


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def change_password():
    """Allow user to change password"""

    # User reached route via POST
    if request.method == "POST":

        old_pwd = request.form.get("old_password")
        new_pwd = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Ensure every field was submitted
        if not (old_pwd and new_pwd and confirmation):
            return apology("blank field(s)!", 400)

        # Query database for user information
        rows = db.execute("SELECT * FROM users WHERE user_id = ?", session["user_id"])

        # Ensure current password is correct
        if not check_password_hash(rows[0]["hash"], old_pwd):
            return apology("invalid old password", 400)

        # Ensure new password is secure
        elif not secure_password(new_pwd):
            flash(
                #"New password is not secure! Password must contain at least 10 characters, 2 digits, 2 uppercase and 2 special characters (no spaces)."
                "Hasło powinno zawierać co najmniej 8 znaków, 1 dużą literę i 1 cyfrę."
            )
            return redirect("/changepassword")

        # Ensure passwords match
        elif not new_pwd == confirmation:
            flash("Hasła się nie zgadzają!")
            return redirect("/changepassword")

        # Update password
        db.execute(
            "UPDATE users SET hash = ? WHERE user_id = ?",
            generate_password_hash(new_pwd),
            session["user_id"],
        )

        # Redirect user to home page
        flash("Hasło zostało zmienione!")
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("change_password.html")


@app.route("/delete_form", methods=["GET", "POST"])
@login_required
def delete_form():
    if request.method == "POST":
        if not (request.form.get("form_id") and request.form.get("patient_code")):
            return apology("Missing data")

        form = db.execute("SELECT * FROM forms WHERE form_id = ? AND user_id = ?", request.form.get("form_id"), session["user_id"])

        if not form:
            return apology("Form not found")

        db.execute("DELETE FROM taken_medicine WHERE form_id = ?", request.form.get("form_id"))
        db.execute("DELETE FROM open_ended_answers WHERE form_id = ?", request.form.get("form_id"))
        db.execute("DELETE FROM medical_supervision WHERE form_id = ?", request.form.get("form_id"))
        db.execute("DELETE FROM forms WHERE form_id = ?", request.form.get("form_id"))

        flash("Pomyślnie usunięto formularz")
        return redirect(f"/patient/{request.form.get('patient_code')}")
    else:
        return redirect("/")


@app.route("/edit_form", methods=["GET", "POST"])
@login_required
def edit_form():
    if request.method == "POST":
        if not request.form.get("form_id"):
            return apology("Wrong form!")

        if not (
            request.form.get("sex")
            and request.form.get("age")
            and request.form.get("weight")
            and request.form.get("height")
            and request.form.get("education_level")
            and request.form.get("doctors_num")
            and request.form.get("health_status")
            and request.form.get("cigarettes")
            and request.form.get("alcohol")
            and request.form.getlist("medicineName")
            and request.form.getlist("medicineDate")
            and request.form.getlist("medicineAdministration")
            and request.form.getlist("medicineCategory")
            and request.form.getlist("medicineSource")
            and request.form.getlist("compliance")
        ):
            form = db.execute(
                "SELECT * FROM forms AS f, patients AS p " +
                "WHERE f.patient_id = p.patient_id " +
                "AND form_id = ? " +
                "AND f.user_id = ? ",
                request.form.get("form_id"),
                session["user_id"])

            answers = db.execute(
                "SELECT * FROM open_ended_answers " +
                "WHERE form_id = ? " +
                "ORDER BY question_id ASC",
                request.form.get("form_id")
            )

            supervision = db.execute(
                "SELECT * FROM medical_supervision " +
                "WHERE form_id = ?",
                request.form.get("form_id")
            )

            taken_medicine = db.execute(
                "SELECT * FROM taken_medicine " +
                "WHERE form_id = ?",
                request.form.get("form_id")
            )

            return render_template("edit.html",
                form=form,
                answers=answers,
                supervision=supervision,
                taken_medicine=taken_medicine,
                education_opt=EDUCATION_OPT,
                health_opt=HEALTH_OPT,
                specialization_opt=SPEC_OPT,
                questions=QUESTIONS,
                medicine_category=MEDICINE_CATEGORY,
                medicine_sources=MEDICINE_SOURCES,
                medicine_administration=MEDICINE_ADMINISTRATION,
                medicine_problem=MEDICINE_PROBLEM,
                intervention_opt=INTERVENTION_OPT
            )
        else:
            patient = db.execute(
                "SELECT * FROM patients " +
                "WHERE patient_id = ? " +
                "AND code = ? " +
                "AND user_id = ?",
                request.form.get("patient_id"),
                request.form.get("patient_code"),
                session["user_id"],
            )

            if not patient:
                return apology("Patient does not exist")

            form = db.execute("SELECT * FROM forms WHERE form_id = ? " +
                "AND patient_id = ? " +
                "AND user_id = ?",
                request.form.get("form_id"),
                request.form.get("patient_id"),
                session["user_id"]
            )

            if not form:
                return apology("Wrong form")

            alcohol_freq = request.form.get("alcohol_freq")
            cigarettes_freq = request.form.get("cigarettes_freq")
            # If patient doesn't smoke/drink alcohol, change "None" values to ""
            if not alcohol_freq:
                alcohol_freq = ""
            if not cigarettes_freq:
                cigarettes_freq = ""

            db.execute(
                "UPDATE forms SET " +
                "age = ?, sex = ?, weight = ?, height = ?, doctors_num = ?, " +
                "education_level = ?, health_status = ?, medical_diagnosis = ?, " +
                "allergy = ?, cigarettes_status = ?, cigarettes_freq = ?, " +
                "alcohol_status = ?, alcohol_freq = ?, " +
                "problem_id = ?, problem_detail = ?, intervention_id = ?, intervention_detail = ?, " +
                "therapeutic_effect_objective = ?, therapeutic_effect_subjective = ?, " +
                "side_effects = ?, knowledge_est = ?, " +
                "diagnosis = ?, issue = ?, goal = ?, " +
                "current_condition = ?, intervention = ?, recommendation = ? " +
                "WHERE form_id = ?",
                request.form.get("age"),
                request.form.get("sex"),
                request.form.get("weight"),
                request.form.get("height"),
                request.form.get("doctors_num"),
                request.form.get("education_level"),
                request.form.get("health_status"),
                request.form.get("medical_diagnosis"),
                request.form.get("allergy"),
                request.form.get("cigarettes"),
                cigarettes_freq,
                request.form.get("alcohol"),
                alcohol_freq,
                request.form.get("medicineProblem"),
                request.form.get("problemText"),
                request.form.get("medicineIntervention"),
                request.form.get("interventionText"),
                request.form.get("effect_obj"),
                request.form.get("effect_sub"),
                request.form.get("side_effect"),
                request.form.get("knowledge_est"),
                request.form.get("diagnosis"),
                request.form.get("issue"),
                request.form.get("goal"),
                request.form.get("condition"),
                request.form.get("intervention"),
                request.form.get("recommendation"),
                request.form.get("form_id")
            )

            # Update information about medical supervision
            db.execute("DELETE FROM medical_supervision WHERE form_id = ?",
                request.form.get("form_id")
            )
            for id in request.form.getlist("specialization"):
                db.execute("INSERT INTO medical_supervision VALUES (?, ?)",
                    id,
                    request.form.get("form_id")
                )

            # Update answers to open-ended questions
            for row in QUESTIONS:
                db.execute(
                    "UPDATE open_ended_answers " +
                    "SET subjective_data = ?, " +
                    "objective_data = ? " +
                    "WHERE form_id = ? " +
                    "AND question_id = ?",
                    request.form.get("sub" + str(row["question_id"])),
                    request.form.get("obj" + str(row["question_id"])),
                    request.form.get("form_id"),
                    row["question_id"]
                )

            # Update information about taken medicine to db
            db.execute("DELETE FROM taken_medicine WHERE form_id = ?",
                request.form.get("form_id")
            )
            for i in range(len(request.form.getlist("medicineName"))):
                db.execute(
                    "INSERT INTO taken_medicine VALUES (?, ?, ?, ?, ?, ?, ?)",
                    request.form.get("form_id"),
                    request.form.getlist("medicineName")[i],
                    request.form.getlist("medicineDate")[i],
                    request.form.getlist("medicineCategory")[i],
                    request.form.getlist("medicineSource")[i],
                    request.form.getlist("medicineAdministration")[i],
                    request.form.getlist("compliance")[i],
                )
            flash("Pomyślnie edytowano formularz")
            return redirect(f"/patient/{request.form.get('patient_code')}")
    else:
        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/newform/<patientCode>", methods=["GET", "POST"])
@login_required
def newform(patientCode):

    """ DISPLAY NEW FORM """
    if request.method == "POST":

        if not (
            request.form.get("id")
            and request.form.get("code")
        ):
            return apology("Missing patient data")

        patient = db.execute(
            "SELECT * FROM patients " +
            "WHERE patient_id = ? " +
            "AND code = ? " +
            "AND user_id = ?",
            request.form.get("id"),
            patientCode,
            session["user_id"]
        )

        if not patient:
            return apology("Patient does not exist")

        return render_template(
            "newform.html",
            patient=patient,
            education_opt=EDUCATION_OPT,
            health_opt=HEALTH_OPT,
            specialization_opt=SPEC_OPT,
            questions=QUESTIONS,
            medicine_category=MEDICINE_CATEGORY,
            medicine_sources=MEDICINE_SOURCES,
            medicine_administration=MEDICINE_ADMINISTRATION,
            medicine_problem=MEDICINE_PROBLEM,
            intervention_opt=INTERVENTION_OPT,
        )
    else:
        if not db.execute("SELECT * FROM patients WHERE code = ? AND user_id = ?", patientCode, session["user_id"]):
            return apology("Patient does not exist")

        return redirect(f"/patient/{patientCode}")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure passwords match
        elif not password == confirmation:
            return apology("passwords don't match", 400)

        # Ensure password is secure
        elif not secure_password(password):
            flash(
                #"Password is not secure! Password must contain at least 10 characters, 2 digits, 2 uppercase and 2 special characters (no spaces)."
                "Hasło powinno zawierać co najmniej 8 znaków, 1 dużą literę i 1 cyfrę."
            )
            return redirect("/register")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username doesn't exist
        if len(rows) != 0:
            return apology("Username is not available", 400)

        # Add user to database
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            generate_password_hash(password),
        )

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        flash("Zarejestrowano!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/search")
@login_required
def search():
    q = request.args.get("q")
    if q:
        patients = db.execute(
            "SELECT * FROM patients WHERE user_id = ? AND code LIKE ?",
            session["user_id"],
            "%" + q + "%",
        )
    else:
        patients = []
    return jsonify(patients)


@app.route("/patient/<patientCode>", methods=["GET", "POST"])
@login_required
def patient(patientCode):
    """Show patient's profile"""

    # Get patient's data from patients table
    patient = db.execute(
        "SELECT * FROM patients WHERE code = ? AND user_id = ?",
        patientCode,
        session["user_id"],
    )
    print(patient)
    if not patient:
        return apology("Patient does not exist")

    # Get all forms that belong to this patient sorted from the newest
    forms = db.execute(
        "SELECT * FROM forms WHERE patient_id = ? ORDER BY filled_date DESC",
        patient[0]["patient_id"],
    )

    if not forms:
        return render_template( "patient.html", patient=patient[0])
    print(forms[0])
    specializations = db.execute(
        "SELECT specialization_name FROM specialization AS s, " +
        "medical_supervision AS ms " +
        "WHERE s.specialization_id = ms.specialization_id AND form_id = ?",
        forms[0]["form_id"],
    )
    open_ended_answers = db.execute(
        "SELECT * FROM open_ended_answers WHERE form_id = ?", forms[0]["form_id"]
    )
    taken_medicine = db.execute(
        "SELECT * FROM taken_medicine WHERE form_id = ?", forms[0]["form_id"]
    )
    return render_template(
        "patient.html",
        patient=patient[0],
        forms=forms,
        specializations=specializations,
        open_ended_answers=open_ended_answers,
        taken_medicine=taken_medicine,
    )


@app.route("/view_form", methods=["POST"])
@login_required
def view_form():
    """View specific form for a current patient"""
    if not request.form.get("id"):
        apology("Wrong form")

    # Consider adding patient id as condition
    form = db.execute(
        "SELECT * FROM forms AS f, problem AS p, " +
        "intervention AS i WHERE f.problem_id = p.problem_id " +
        "AND f.intervention_id = i.intervention_id AND form_id = ? AND user_id = ?",
        request.form.get("id"),
        session["user_id"],
    )

    if not form:
        apology("Form does not exist")

    patient = db.execute("SELECT * FROM patients WHERE patient_id = ?",
        form[0]["patient_id"])[0]

    specializations = db.execute(
        "SELECT specialization_name FROM specialization AS s, " +
        "medical_supervision AS ms " +
        "WHERE s.specialization_id = ms.specialization_id AND form_id = ?",
        request.form.get("id"),
    )

    open_ended_answers = db.execute(
        "SELECT question_text, subjective_data, objective_data " +
        "FROM open_ended_questions AS q, open_ended_answers AS a " +
        "WHERE q.question_id = a.question_id AND form_id = ?",
        request.form.get("id"),
    )

    taken_medicine = db.execute(
        "SELECT medicine_name, "+
        "start_date, category_name, source_name, administration_name, "+
        "compliance "+
        "FROM taken_medicine AS tm, medicine_administration AS ma, "+
        "medicine_category AS mc, medicine_source AS ms "+
        "WHERE ma.administration_id=tm.administration_id "+
        "AND mc.category_id=tm.category_id "+
        "AND ms.source_id=tm.source_id "+
        "AND tm.form_id = ?",
        request.form.get("id"),
    )

    summary_answer = [
        form[0]["diagnosis"],
        form[0]["issue"],
        form[0]["goal"],
        form[0]["current_condition"],
        form[0]["intervention"],
        form[0]["recommendation"]
    ]

    summary_title = ["Rozpoznanie", "Lek/preparat - problem terapeutyczny",
        "Cel do osiągnięcia", "Obecny stan", "Interwencja farmaceutyczna",
        "Zalecenia farmaceuty"]

    summary = zip(summary_title, summary_answer)

    return render_template(
        "view_form.html",
        form=form[0],
        patient=patient,
        specializations=specializations,
        open_ended_answers=open_ended_answers,
        taken_medicine=taken_medicine,
        summary=summary
    )
