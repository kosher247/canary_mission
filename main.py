from playwright.sync_api import Playwright, sync_playwright
import time
import json

def scrape_canary_mission() -> list:
    def process_socials(socials):
        result = {}
        key = None
        for item in socials:
            if item.endswith(':'):
                key = item[:-1]
            elif key:
                result[key] = item
                key = None
        return result

    def run(playwright: Playwright) -> list:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        
        groups = ['students', 'professors', 'professionals']
        processed_json = []
        
        for group in groups:
            # Open new page
            page = context.new_page()
            page.goto('https://canarymission.org/' + group)
    
            # Scroll down the page to load more content
            for i in range(100):  # Adjust the range as needed
                page.mouse.wheel(0, 1000)
                time.sleep(1)
    
            # Get all elements matching the XPath
            elements = page.query_selector_all('//*[contains(concat( " ", @class, " " ), concat( " ", "name", " " ))]/a')
            hrefs = [element.get_attribute('href') for element in elements]
            urls = ['https://canarymission.org' + href for href in hrefs]
    
            for url in urls:
                page.goto(url)
                time.sleep(2)
                name = page.locator("h1").inner_text()
                socials = page.locator("b+ a , b").all_inner_texts()
                university = page.locator('dl:nth-child(2) span').all_inner_texts()
                image = page\
                .locator('xpath=/html/body/div[1]/div[5]/div[5]/main/div/div[2]/div[3]/div[1]/div[1]/img')\
                .get_attribute('src')
                last_modified = page.locator('br~ dd').inner_text()
    
                try:
                    processed_socials = process_socials(socials)
                except:
                    processed_socials = []
    
                processed_json.append({
                  'name': name, 
                  'image': image, 
                  'group': group, 
                  'url': url,
                  'university-employer':university, 
                  'socials': processed_socials,
                  'last-modified':last_modified
                  }
                  )
        
        context.close()
        browser.close()
        
        return processed_json

    with sync_playwright() as playwright:
        return run(playwright)

# To run the function and get the data
data = scrape_canary_mission()

with open("canary.json", 'w') as f:
    json.dump(data, f)