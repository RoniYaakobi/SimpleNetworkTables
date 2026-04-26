from .forgot_password import ForgotPage
from .login import LoginPage
from .reset_password import ResetPasswordPage
from .settings import SettingsPage
from .signup import SignUpPage
from .verify_account import VerifyPage
from .verify_forgot import ForgotCodePage


ALL_PAGES = [SettingsPage, ForgotCodePage, ForgotPage, LoginPage,ResetPasswordPage, SignUpPage, VerifyPage]

from .GUI import App