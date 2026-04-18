import asyncio
from urllib.parse import quote
from playwright.async_api import async_playwright

async def scrape_lens_titles(image_url):
    async with async_playwright() as p:
        # Pass args to disable the "Chrome is being controlled by automated test software" flag
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        # Manually mask the webdriver property to bypass bot detection 
        # without needing the playwright-stealth package.
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        encoded_url = quote(image_url, safe='')
        lens_url = f"https://lens.google.com/upload?url={encoded_url}"
        
        print(f"Navigating to: {lens_url}")
        
        try:
            # Navigating immediately with no artificial sleep delays
            await page.goto(lens_url, wait_until="domcontentloaded")
            
            await page.wait_for_selector('div[role="listitem"]', timeout=15000)

            # Extract titles
            titles = await page.locator('div[role="listitem"] h3, .UA8B8e').all_inner_texts()

            clean_titles = [t.strip() for t in titles if t.strip()]
            return list(dict.fromkeys(clean_titles))

        except Exception as e:
            await page.screenshot(path=r"C:\Me\Python Projects\Pokedex 2.0\v6\error_state.png")
            print(f"Error encountered: {e}")
            return []
        finally:
            await browser.close()

if __name__ == "__main__":
    image = "https://media.52poke.com/wiki/0/05/038Ninetales.png"
    results = asyncio.run(scrape_lens_titles(image))
    
    if results:
        print("\n--- Visual Match Titles ---")
        for i, title in enumerate(results, 1):
            print(f"{i}. {title}")
    else:
        print("Failed to retrieve titles. See error_state.png")