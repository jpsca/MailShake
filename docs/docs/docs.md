
# Overview

Sending emails with Python 3 is a little easier than before, but still a mess. 
This library makes it way easier to send emails, test the
sending during development, and provides support for platforms that
don't use SMTP like Amazon SES.

Available mailers:

-   SMTPMailer
-   AmazonSESMailer
-   ToConsoleMailer (prints the emails in the console)
-   ToMemoryMailer (for testing)


## Installation

```python
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate said environment
source .venv/bin/activate

# 3. Install the library
python -m pip install mailshake
```
