from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.extract_links import extract_all_links_from_page
import threading
import json

chrome_options = Options()
chrome_options.add_argument("--headless")

QUEUE: list[str] = []
CONCURRENCY: int = 10 
threads: list = []
for _ in range(CONCURRENCY):
    threads.append(None)
START_URL: str = "https://en.wikipedia.org/wiki/Software_engineering"
indexed_pages: set[str] = {START_URL}
driver = webdriver.Chrome(options=chrome_options)

QUEUE.append(START_URL)
driver.get(START_URL)
extracted_links: set[str] = extract_all_links_from_page(driver)
QUEUE.remove(START_URL)
QUEUE.extend(extracted_links)

states: dict[str, set[str]] = {
        START_URL: extracted_links
}

instances: list[dict[str, webdriver.Chrome | None | bool]] = [{
    "driver": driver,
    "busy": False,
}]

for _ in range(CONCURRENCY - 1):
    instances.append({
        "driver": webdriver.Chrome(options=chrome_options),
        "busy": False,
    })

def get_free_instance() -> int:
    for i, instance in enumerate(instances):
        if not instance["busy"]:
            return i
    return -1


def extraction(driver: webdriver.Chrome, url: str) -> set[str]:
    print("Extracting links from:", url)
    driver.get(url)
    extracted_links: set[str] = extract_all_links_from_page(driver)
    states[url] = extracted_links
    return extracted_links

while len(list(states.keys())) < 10:
    print("Queue length:", len(QUEUE))
    for i in range(CONCURRENCY): # The size of threading is equal to the number of threads and instances
        if len(QUEUE) == 0:
            print("Queue is empty, waiting for threads to finish...")

        instance_number: int = get_free_instance()

        if instance_number == -1 or (threads[instance_number] is not None and threads[instance_number].is_alive()): # type: ignore
            print("No free instance available, waiting for threads to finish...")
            continue

        driver: webdriver.Chrome = instances[instance_number]["driver"] # type: ignore
        instances[instance_number]["busy"] = True

        url: str = QUEUE.pop(0)
    
        if url in states:
            instances[instance_number]["busy"] = False
            continue

        threads[instance_number] = threading.Thread(target=extraction, args=(driver, url)) # type: ignore
        threads[instance_number].start() # type: ignore

        for link in extracted_links:
            if link not in indexed_pages:
                indexed_pages.add(link)
                QUEUE.append(link)


# Wait until all threads are finish
while any(thread is not None and thread.is_alive() for thread in threads): # type: ignore
    pass

"""
The output of this program is the state object and it should look like this:

{
    "wiki_link": ["wiki_link1", "wiki_link2", "wiki_link3"],
    "wiki_link1": ["wiki_link4", "wiki_link5"],
    "wiki_link2": ["wiki_link6", "wiki_link7"]
}

from this the knowledge graph shpould be generated
"""

for key, obj in states.items():
  states[key] = list(obj) # type: ignore


with open("output.json", "w") as f:
  json.dump(states, f, indent=4)
