cd /home/ploi/staging.mintscale.io
git stash
git pull origin main
python3 -m venv ms
source ms/bin/activate
pip3 install --upgrade setuptools pip
pip3 install -r requirements.txt
opentelemetry-bootstrap --action=install
cp -r site/* /home/ploi/mintscale.io/public/
pushd tools/api
PCS=`ps aux |grep gunicorn |grep mintapi | awk '{ print $2 }'`
[ -z "$PCS" ] && echo "gunicorn not running, starting" || kill -9 $PCS
export MONGODB_URL="mongodb+srv://<username>:<password>@<url>?retryWrites=true&w=majority"
export OTEL_RESOURCE_ATTRIBUTES=service.name=mintapi
export OTEL_EXPORTER_OTLP_ENDPOINT="http://<IP>:<PORT>"
opentelemetry-instrument --traces_exporter otlp_proto_http gunicorn mintapi:app --workers 4 -k uvicorn.workers.UvicornWorker --bind :8080  --access-logfile guniaccess.log --log-level 'debug' --error-logfile gunistdout.log --capture-output --daemon
echo "🚀 Application deployed!"