from fastapi import FastAPI
from sinube import execute_query
from metrics import calculate_metrics
from cache import get_cache, set_cache

app = FastAPI()

def build_query(empresas, tipo, valor):
    empresas_filter = " OR ".join([f"F.empresa='{e}'" for e in empresas])

    base = f"""
    SELECT
    F.uuid AS UUID,
    F.fechaFactura,
    F.empresa AS 'RFC Emisor',
    FD.descripcion AS 'Descripción',
    F.importeTotal AS Importe,
    D.montoAplicado AS 'Monto del Pago'
    FROM DbFactura AS F
    INNER JOIN DbFacturaDet AS FD ON
    FD.empresa=F.empresa AND
    FD.sucursal=F.sucursal AND
    FD.serieFactura=F.serieFactura AND
    FD.folioFactura=F.folioFactura
    LEFT JOIN DbDepositoDet AS D ON
    D.empresa=F.empresa AND
    D.sucursal=F.sucursal AND
    D.folioFactura=F.folioFactura AND
    D.serieFactura=F.serieFactura
    WHERE
    F.sucursal='Matriz' AND
    ({empresas_filter}) AND
    D.cancelado=False
    """

    if tipo == "mes":
        base += f" AND F.mes={valor}"
    else:
        base += f" AND F.dia={valor}"

    base += " TAMPAG 100"
    return base


@app.post("/dashboard")
def dashboard(payload: dict):
    empresas = payload["empresas"]
    tipo = payload["tipo"]
    valor = payload["valor"]

    cache_key = f"{empresas}_{tipo}_{valor}"

    cached = get_cache(cache_key)
    if cached:
        return cached

    data = execute_query(build_query(empresas, tipo, valor))
    metrics = calculate_metrics(data)

    response = {
        "data": data,
        "metrics": metrics
    }

    set_cache(cache_key, response)

    return response
