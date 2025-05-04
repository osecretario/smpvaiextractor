# 
FROM python:3.11.9

# 
COPY ./requirements.txt .

# 
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 
WORKDIR /fastapi

# 
COPY src/ /fastapi/src/

# 
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
