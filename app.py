from flask import Flask, request, jsonify
from flask_cors import CORS
import pandapower as pp
import pandapower.shortcircuit as sc

app = Flask(__name__)
CORS(app) 

@app.route('/calcular_curto', methods=['POST'])
def calcular_curto():
    try:
        dados = request.get_json()
        comprimento_linha = float(dados.get('distancia_km', 5.0))

        net = pp.create_empty_network()

        # Barramentos
        b_at = pp.create_bus(net, vn_kv=69.0, name="Barra 69kV (SE)")
        b_mt = pp.create_bus(net, vn_kv=13.8, name="Barra 13.8kV (Alimentador)")
        b_cliente = pp.create_bus(net, vn_kv=13.8, name="Ponto de Falta (Cliente)")

        # Grid Externo (adicionado parâmetros de sequência zero)
        pp.create_ext_grid(net, bus=b_at, s_sc_max_mva=1000, s_sc_min_mva=800, rx_max=0.1, rx_min=0.1, r0x0_max=0.1, x0x_max=1.0)

        # Transformador (Adicionado grupo vetorial Dyn1 e impedância de sequência zero)
        pp.create_transformer_from_parameters(
            net, hv_bus=b_at, lv_bus=b_mt, sn_mva=15.0, vn_hv_kv=69.0, vn_lv_kv=13.8,
            vk_percent=10.0, vkr_percent=0.5, pfe_kw=10.0, i0_percent=0.1,
            vector_group="Dyn1", vk0_percent=10.0, vkr0_percent=0.5, mag0_percent=100, mag0_rx=0.0
        )

        # Linha de Distribuição (Adicionado R0 e X0 típicos: ~3x o valor de R1 e X1)
        pp.create_line_from_parameters(
            net, from_bus=b_mt, to_bus=b_cliente, length_km=comprimento_linha,
            r_ohm_per_km=0.17, x_ohm_per_km=0.38, c_nf_per_km=10.0, max_i_ka=0.53,
            r0_ohm_per_km=0.51, x0_ohm_per_km=1.14, c0_nf_per_km=5.0
        )

        # CÁLCULO 1: Curto Máximo (Trifásico)
        sc.calc_sc(net, case="max", fault="3ph", ip=True, ith=True, branch_results=True)
        icc_max = net.res_bus_sc.ikss_ka.at[b_cliente] * 1000

        # CÁLCULO 2: Curto Mínimo (Monofásico Fase-Terra)
        sc.calc_sc(net, case="min", fault="1ph", ip=True, ith=True, branch_results=True)
        icc_min = net.res_bus_sc.ikss_ka.at[b_cliente] * 1000

        return jsonify({
            "status": "sucesso",
            "icc_max_a": round(icc_max, 2),
            "icc_min_a": round(icc_min, 2),
            "distancia_utilizada_km": comprimento_linha
        }), 200

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
