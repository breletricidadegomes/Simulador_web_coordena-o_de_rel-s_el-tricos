from flask import Flask, request, jsonify
from flask_cors import CORS
import pandapower as pp
import pandapower.shortcircuit as sc

app = Flask(__name__)
# Habilita o CORS para permitir requisições do seu index.html
CORS(app) 

@app.route('/calcular_curto', methods=['POST'])
def calcular_curto():
    try:
        # Recebe os dados enviados pelo frontend
        dados = request.get_json()
        
        # Pega a distância da linha enviada pelo usuário (padrão 5.0 se não vier nada)
        comprimento_linha = float(dados.get('distancia_km', 5.0))

        # 1. Cria a rede vazia
        net = pp.create_empty_network()

        # 2. Barramentos
        b_at = pp.create_bus(net, vn_kv=69.0, name="Barra 69kV (SE)")
        b_mt = pp.create_bus(net, vn_kv=13.8, name="Barra 13.8kV (Alimentador)")
        b_cliente = pp.create_bus(net, vn_kv=13.8, name="Ponto de Falta (Cliente)")

        # 3. Grid Externo
        pp.create_ext_grid(net, bus=b_at, s_sc_max_mva=1000, rx_max=0.1)

        # 4. Transformador
        pp.create_transformer_from_parameters(
            net, hv_bus=b_at, lv_bus=b_mt, sn_mva=15.0, vn_hv_kv=69.0, vn_lv_kv=13.8,
            vk_percent=10.0, vkr_percent=0.5, pfe_kw=10.0, i0_percent=0.1
        )

        # 5. Linha de Distribuição (usando a distância dinâmica que veio do frontend)
        pp.create_line_from_parameters(
            net, from_bus=b_mt, to_bus=b_cliente, length_km=comprimento_linha,
            r_ohm_per_km=0.17, x_ohm_per_km=0.38, c_nf_per_km=10.0, max_i_ka=0.53
        )

        # 6. Cálculo IEC 60909
        sc.calc_sc(net, case="max", ip=True, ith=True, branch_results=True)

        # 7. Extrai o Icc do Cliente em Amperes
        icc_cliente = net.res_bus_sc.ikss_ka.at[b_cliente] * 1000

        # Retorna o resultado empacotado em JSON
        return jsonify({
            "status": "sucesso",
            "icc_cliente_a": round(icc_cliente, 2),
            "distancia_utilizada_km": comprimento_linha
        }), 200

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(debug=True, port=5000)