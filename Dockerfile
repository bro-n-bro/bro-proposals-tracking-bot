FROM python:3.8

COPY requirements.txt .
RUN pip install -r ./requirements.txt

COPY get_data.py .
COPY notifier.py .
COPY sql.py .
COPY utils.py .
COPY data  data/
COPY _wallet.py .
COPY _typing.py .

CMD python -u ./notifier.py --log=INFO