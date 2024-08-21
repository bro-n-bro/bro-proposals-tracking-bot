FROM python:3.12

COPY requirements.txt .
RUN pip install -r ./requirements.txt

COPY get_data.py .
COPY notifier.py .
COPY sql.py .
COPY utils.py .
COPY data  data/
COPY _wallet.py .
COPY custom_typing.py .

CMD python -u ./notifier.py --log=INFO