from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List
import uvicorn
from dotenv import dotenv_values

creds = dotenv_values(".env")

class EmailSchema(BaseModel):
    email: List[EmailStr] = [EmailStr(creds['EMAIL'])]

class EmailContent(BaseModel): #sender's email
    name: str
    ema: str
    msg: str

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


@app.post("/email")
async def simple_send(email: EmailSchema, content:EmailContent) -> JSONResponse:
    html = f"""
    <p>Hi my name is {content.name}.</p>
    <br>
    <p>You can contact me at: {content.ema}.</p>
    <br>
    <p>{content.msg}</p>
    """

    message = MessageSchema(
        subject=f"Hello from {content.name}",
        recipients=email.dict().get("email"),  # List of recipients, as many as you can pass 
        body=html,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"}) 

if __name__ == "__main__":
    uvicorn.run("example:app", host='127.0.0.1', port=8404,reload=True,debug=True)
