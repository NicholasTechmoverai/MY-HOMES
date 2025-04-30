from fastapi import FastAPI,Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routes.main import main_router
from routes.properties import property_router
import uvicorn

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_items(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/trending_videos", response_class=HTMLResponse)
async def lt(request: Request):
    return templates.TemplateResponse("videos.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def abt(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/for_sale", response_class=HTMLResponse)
async def buy(request: Request):
    return templates.TemplateResponse("for_Sale.html", {"request": request})

@app.get("/sell", response_class=HTMLResponse)
async def sell(request: Request):
    return templates.TemplateResponse("sell.html", {"request": request})

@app.get("/guide", response_class=HTMLResponse)
async def guide(request: Request):
    return templates.TemplateResponse("guides.html", {"request": request})

@app.get("/for_rent", response_class=HTMLResponse)
async def rent(request: Request):
    return templates.TemplateResponse("rent.html", {"request": request})

@app.get("/contact_us", response_class=HTMLResponse)
async def contact_us(request: Request):
    return templates.TemplateResponse("contactUs.html", {"request": request})

@app.get("/more", response_class=HTMLResponse)
async def more(request: Request):
    return templates.TemplateResponse("more.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

# Mount routers
app.include_router(main_router)
app.include_router(property_router, prefix="/property")  # FIX: correct usage of prefix

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Run with: python main.py
if __name__ == "__main__":
    uvicorn.run("appp:app", host="127.0.0.1", port=8000, reload=True)
