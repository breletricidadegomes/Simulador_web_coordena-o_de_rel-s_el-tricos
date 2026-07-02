from flask import Flask, request, jsonify
from flask_cors import CORS
import pandapower as pp
import pandapower.shortcircuit as sc
import math

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

        # Grid Externo
        pp.create_ext_grid(net, bus=b_at, s_sc_max_mva=1000, s_sc_min_mva=800, rx_max=0.1, rx_min=0.1, r0x0_max=0.1, x0x_max=1.0)

        # Transformador
        pp.create_transformer_from_parameters(
            net, hv_bus=b_at, lv_bus=b_mt, sn_mva=15.0, vn_hv_kv=69.0, vn_lv_kv=13.8,
            vk_percent=10.0, vkr_percent=0.5, pfe_kw=10.0, i0_percent=0.1,
            vector_group="Dyn1", vk0_percent=10.0, vkr0_percent=0.5, mag0_percent=100, mag0_rx=0.0
        )

        # Linha de Distribuição
        pp.create_line_from_parameters(
            net, from_bus=b_mt, to_bus=b_cliente, length_km=comprimento_linha,
            r_ohm_per_km=0.17, x_ohm_per_km=0.38, c_nf_per_km=10.0, max_i_ka=0.53,
            r0_ohm_per_km=0.51, x0_ohm_per_km=1.14, c0_nf_per_km=5.0
        )

        # CÁLCULO 1: Curto Máximo (Trifásico Simétrico)
        sc.calc_sc(net, case="max", fault="3ph", ip=True, ith=True, branch_results=True)
        icc_max_sim = net.res_bus_sc.ikss_ka.at[b_cliente] * 1000

        # CÁLCULO 2: Curto Mínimo (Monofásico Fase-Terra Simétrico)
        sc.calc_sc(net, case="min", fault="1ph", ip=True, ith=True, branch_results=True)
        icc_min_sim = net.res_bus_sc.ikss_ka.at[b_cliente] * 1000

        # -----------------------------------------------------
        # CÁLCULO DE ASSIMETRIA
        # -----------------------------------------------------
        z_grid = (13.8**2) / 1000.0
        r_grid = z_grid * 0.1
        x_grid = z_grid * 0.995 
        
        z_base_trafo = (13.8**2) / 15.0
        r_trafo = z_base_trafo * 0.005
        x_trafo = z_base_trafo * 0.0998 
        
        r_linha = 0.17 * comprimento_linha
        x_linha = 0.38 * comprimento_linha
        
        r_total = r_grid + r_trafo + r_linha
        x_total = x_grid + x_trafo + x_linha
        rx_ratio = r_total / x_total if x_total > 0 else 0
        
        fa = math.sqrt(1 + 2 * math.exp(-2 * math.pi * rx_ratio))
        
        icc_max_assim = icc_max_sim * fa
        icc_min_assim = icc_min_sim * fa

        # O JSON agora envia as chaves corretas que o HTML espera
        return jsonify({
            "status": "sucesso",
            "icc_max_sim_a": round(icc_max_sim, 2),
            "icc_max_assim_a": round(icc_max_assim, 2),
            "icc_min_sim_a": round(icc_min_sim, 2),
            "icc_min_assim_a": round(icc_min_assim, 2),
            "fator_assimetria": round(fa, 3),
            "distancia_utilizada_km": comprimento_linha
        }), 200

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
