import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://deposit-rescue.vercel.app/", wait_until="networkidle")
        print("Page title:", await page.title())
        
        # Get text content or buttons / textareas
        textareas = await page.query_selector_all("textarea")
        print("Textareas found:", len(textareas))
        for i, ta in enumerate(textareas):
            placeholder = await ta.get_attribute("placeholder")
            print(f"Textarea {i}: placeholder='{placeholder}'")
            
        buttons = await page.query_selector_all("button")
        print("Buttons found:", len(buttons))
        for i, b in enumerate(buttons):
            text = await b.inner_text()
            print(f"Button {i}: text='{text.strip()}'")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
