import uvicorn
from fastapi import FastAPI

from user.router import router as auth_router
from account.router import router as account_router
from transactions.router import router as transaction_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(account_router)
app.include_router(transaction_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)
