FROM almalinux:latest

RUN dnf -y update && \
    dnf -y install python3 python3-pip && \
    dnf clean all

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY vpn_user_activity.py /app/

EXPOSE 9101

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:9101", "vpn_user_activity:app"]
