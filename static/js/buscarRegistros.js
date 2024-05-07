function buscarRegistros() {
    var fecha_inicio = $('#date1').val();
    var fecha_fin = $('#date2').val();

    $.ajax({
        url: '/registros_sede',
        type: 'POST',
        data: {
            fecha_inicio: fecha_inicio,
            fecha_fin: fecha_fin
        },
        success: function(response) {
            // Limpiar el contenido existente del tbody
            $('#tablaRegistros tbody').empty();
            
            // Insertar las nuevas filas en el tbody
            for (var i = 0; i < response.length; i++) {
                var row = response[i];
                var newRow = '<tr>' +
                    '<td align="center">' + row[0] + '</td>' + // Cédula
                    '<td align="center">' + row[1] + '</td>' + // Nombre
                    '<td align="center">' + row[2] + '</td>' + // Registros
                    '<td align="center">' + row[3] + '%</td>' +
                    '</tr>';
                $('#tablaRegistros tbody').append(newRow);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error al buscar registros:', error);
        }
    });
}
function exportToExcel() {
    // Generar la solicitud para exportar a CSV
    $.ajax({
        url: '/exportar_csv',
        type: 'POST',
        data: {
            fecha_inicio: $('#date1').val(),
            fecha_fin: $('#date2').val()
        },
        success: function(data) {
            // Redirigir al usuario para descargar el archivo CSV
            var blob = new Blob([data], { type: 'text/csv' });
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'registros.csv';
            link.click();
        },
        error: function(xhr, status, error) {
            console.error('Error al exportar a CSV:', error);
        }
    });
}
