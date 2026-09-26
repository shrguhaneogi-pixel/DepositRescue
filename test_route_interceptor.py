import asyncio
import json
import sys
from pathlib import Path

# Add root directory to python path
sys.path.insert(0, str(Path(__file__).parent))

from api.core.schemas import AuditRequest
from api.index import audit_landlord_statement
from playwright.async_api import async_playwright

async def handle_api_route(route, request):
    if request.method == "POST":
        post_data = request.post_data_json
        text = post_data.get("text", "") if post_data else ""
        print(f"[Intercepted API Call] Text to audit: {text}")
        
        # Call the local Python engine
        req = AuditRequest(text=text)
        res = audit_landlord_statement(req)
        res_json = res.model_dump()
        print(f"[Engine Result] Raw total: ${res_json['raw_total']}, Illegal total: ${res_json['illegal_total']}")
        
        await route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(res_json)
        )
    else:
        await route.continue_()

async def test_interceptor():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Intercept any API calls
        await page.route("**/api/**", handle_api_route)
        
        await page.goto("https://deposit-rescue.vercel.app/", wait_until="networkidle")
        
        textarea = page.locator("textarea")
        await textarea.fill("Landlord says: $400 for painting, $150 for routine carpet cleaning, and $200 for a broken window.")
        
        audit_btn = page.locator("button", has_text="AUDIT")
        await audit_btn.click()
        
        await page.wait_for_timeout(3000)
        
        body_text = await page.inner_text("body")
        print("\nPage output after intercepted audit:")
        print(body_text[:1200])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_interceptor())
