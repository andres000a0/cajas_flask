import json

def generate_chart_data():
    # Datos de ejemplo
    data = {
        'Cajas': ["Caja 1", "Caja 2", "Caja 3", "Caja 4", "Caja 5", "Caja 6", "Caja 7", "Caja 8", "Caja 9", "Caja 10"],
        'Productividad': [150, 200, 180, 220, 190, 210, 170, 230, 200, 190],
        'Inactividad': [30, 45, 20, 60, 35, 40, 25, 50, 30, 40]
    }

    # Crear datos en el formato adecuado para Chart.js para productividad por registros
    productividad_data = {
        'labels': data['Cajas'],
        'datasets': [
            {
                'label': 'Productividad por Registros',
                'data': data['Productividad'],
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1,
                'type': 'bar'
            }
        ]
    }

    # Crear datos en el formato adecuado para Chart.js para tiempo de inactividad
    inactividad_data = {
        'labels': data['Cajas'],
        'datasets': [
            {
                'label': 'Tiempo de Inactividad de las Cajas',
                'data': data['Inactividad'],
                'fill': False,
                'borderColor': 'rgba(255, 99, 132, 0.8)',
                'type': 'line'
            }
        ]
    }

    # Convertir los datos a JSON
    productividad_data_json = json.dumps(productividad_data)
    inactividad_data_json = json.dumps(inactividad_data)

    return productividad_data_json, inactividad_data_json

