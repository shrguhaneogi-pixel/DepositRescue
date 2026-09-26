import asyncio
from playwright.async_api import async_playwright

async def test_sample():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://deposit-rescue.vercel.app/", wait_until="networkidle")
        
        sample_btn = page.locator("button", has_text="LOAD SAMPLE NOTICE")
        await sample_btn.click()
        await page.wait_for_timeout(3000)
        
        body = await page.inner_text("body")
        print("Body after sample notice:")
        print(body[:800])
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_sample())
