import requests


def load_env():
    """
    Reads development configuration from environment variables
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    return {
        "MAILGUN_API_KEY": os.getenv("MAILGUN_API_KEY"),
        "MAILGUN_DOMAIN": os.getenv("MAILGUN_DOMAIN"),
        "RECEIVER_EMAIL": os.getenv("RECEIVER_EMAIL"),
    }


def send_failure_email(context):
    config = load_env()
    MAILGUN_API_KEY = config["MAILGUN_API_KEY"]
    MAILGUN_DOMAIN = config["MAILGUN_DOMAIN"]
    receiver_email = config["RECEIVER_EMAIL"]

    subject = f"Airflow Task Failed: {context['task_instance'].task_id}"
    body = f"""
    Task: {context['task_instance'].task_id}
    DAG: {context['dag'].dag_id}
    Execution Date: {context['execution_date']}
    Log URL: {context['task_instance'].log_url}
    """

    requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Airflow <mailgun@{MAILGUN_DOMAIN}>",
            "to": receiver_email,
            "subject": subject,
            "text": body,
        },
    )
