from selenium.webdriver.common.by import By

def extract_all_links_from_page(driver) -> set[str]:
    print(f"Extracting all links from the page: {driver.current_url}")
 
    links: list = driver.find_elements(By.TAG_NAME, "a")

    extracted_links: set[str] = set()

    for link in links: # can be put in one after optimization
        ahref = link.get_attribute("href")
        if ahref and 'wikipedia' in ahref and '#' not in ahref:
            extracted_links.add(ahref)
            print(ahref)

    return extracted_links
