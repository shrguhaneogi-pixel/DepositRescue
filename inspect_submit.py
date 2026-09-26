import asyncio
from playwright.async_api import async_playwright

async def inspect_submit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://deposit-rescue.vercel.app/", wait_until="networkidle")
        
        textarea = page.locator("textarea")
        await textarea.fill("Landlord says: $400 for painting, $150 for routine carpet cleaning, and $200 for a broken window.")
        
        audit_btn = page.locator("button", has_text="AUDIT")
        await audit_btn.click()
        
        # Wait for network idle or results
        await page.wait_for_timeout(3000)
        
        body_text = await page.inner_text("body")
        print("Page text snippet after audit:")
        print(body_text[:1000])

        headings = await page.query_selector_all("h1, h2, h3, h4, div")
        for h in headings[:15]:
            t = await h.inner_text()
            if any(w in t.lower() for w in ["total", "illegal", "statutory", "recovered", "ledger", "deduction"]):
                print("Matching element text:", t.strip().replace('\n', ' '))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_submit())
