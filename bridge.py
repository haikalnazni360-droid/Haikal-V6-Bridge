import os, time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
TOKEN = os.getenv("BRIDGE_TOKEN", "CHANGE_THIS_SECRET")
latest = {"side":"WAIT","score":0,"symbol":"XAUUSD","ts":0}

@app.get("/")
def home():
    return jsonify(ok=True, service="Haikal V6.2 TradingView-MT5 Bridge")

@app.post("/webhook")
def webhook():
    data = request.get_json(silent=True) or {}
    if data.get("token") != TOKEN:
        return jsonify(ok=False, error="unauthorized"), 401
    side = str(data.get("side","WAIT")).upper()
    if side not in ("BUY","SELL","WAIT"):
        return jsonify(ok=False, error="bad side"), 400
    default_score = 85 if side=="BUY" else (-85 if side=="SELL" else 0)
    score = max(-100, min(100, float(data.get("score", default_score))))
    latest.update(side=side, score=score, symbol=str(data.get("symbol","XAUUSD")), ts=int(time.time()))
    return jsonify(ok=True, **latest)

@app.get("/signal")
def signal():
    if request.args.get("token") != TOKEN:
        return Response("unauthorized", status=401, mimetype="text/plain")
    age = 999999 if not latest["ts"] else max(0, int(time.time())-latest["ts"])
    body = f"score={latest['score']};side={latest['side']};age={age}"
    return Response(body, mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.getenv("PORT","8080"))
    app.run(host="0.0.0.0", port=port)
