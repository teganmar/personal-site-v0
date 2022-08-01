from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, Depends
from starlette.responses import JSONResponse, HTMLResponse
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List
import uvicorn
from dotenv import dotenv_values
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


creds = dotenv_values(".env")

class EmailSchema(BaseModel):
    #email: List[EmailStr] = [EmailStr(creds['EMAIL'])]
    name: str
    ema: EmailStr
    msg: str
    email: List[EmailStr] = [EmailStr(creds['EMAIL'])]

    @classmethod
    def as_form(
        cls,
        name: str = Form(..., max_length=30),
        ema: EmailStr = Form(...),
        msg: str = Form(...),
        email: List[EmailStr] = Form([EmailStr(creds['EMAIL'])])
    ):
        class Config:
            orm_mode=True

        return cls(
            name=name,
            ema=ema,
            msg=msg,
            email=email
        )

# class EmailContent(BaseModel): #sender's email
#     name: str
#     ema: str
#     msg: str

conf = ConnectionConfig(
    MAIL_USERNAME = creds['EMAIL'],
    MAIL_PASSWORD = creds['PASS'],
    MAIL_FROM = creds['EMAIL'],
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    #VALIDATE_CERTS = True
)

app = FastAPI()

# include html file
templates = Jinja2Templates(directory="templates")
# include css file
app.mount("/static", StaticFiles(directory="static"), name="static")

# not yet sure what this is for will look into it
origins = ["*"]#["http://localhost:8404"]#["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})


@app.post("/email")
async def simple_send(email: EmailSchema = Depends(EmailSchema.as_form)) -> JSONResponse:#, content:EmailContent) -> JSONResponse:
    html = f"""
    <p>Hi my name is {email.name}.</p>
    <br>
    <p>You can contact me at: {email.ema}.</p>
    <br>
    <p>{email.msg}</p>
    """

    message = MessageSchema(
        subject=f"Hello from {email.name}",
        recipients=email.dict().get("email"),  # List of recipients, as many as you can pass 
        body=html,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"}) 

if __name__ == "__main__":
    uvicorn.run("example:app", host='127.0.0.1', port=8404,reload=True,debug=True)
