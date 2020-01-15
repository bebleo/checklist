from wtforms.validators import InputRequired, Email, EqualTo


username_req = InputRequired("Username cannot be empty.")
username_email = Email("Username must be a valid email")
password_req = InputRequired("Password cannot be empty.")
password_conf = EqualTo("confirm",
                        message="Password and confirmation must match.")
confirm_req = InputRequired("Password cannot be empty.")

username_combo = [username_email, username_req]
