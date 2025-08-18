from rich import print
import requests

def count_words_at_url(url):
    """Just an example function that's called async."""
    resp = requests.get(url)
    return len(resp.text.split())

def report_success(job, connection, result, *args, **kwargs):
    print(f"Job {job.id} completed successfully with result: {result}")
    

def embed_job(job, connection, *args, **kwargs):
    """This function is called when the job is embedded."""
    print(f"Job {job.id} has been embedded.")
    return job.id