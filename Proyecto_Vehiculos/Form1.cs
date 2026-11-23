using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
using Proyecto_Vehiculos.apiClient;
using Proyecto_Vehiculos.appState;
using Proyecto_Vehiculos.DTO;

namespace Proyecto_Vehiculos
{
    public partial class Form1 : Form
    {
        private readonly VehiculosApi _api;
        private List<VehiculoDto> _vehiculos = new();
        private List<CompradorDto> _compradores = new();
        private List<VentaResponseDto> _ventas = new();

        public Form1()
        {
            InitializeComponent();
            _api = new VehiculosApi();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            lblMensajeEstado.Text = "Listo. Ingrese JWT o consulte servicios.";
            lblEndpointGateway.Text = $"Gateway NGINX: {GlobalState.BaseUrl}";
            ConfigurarGrids();
        }

        private void ConfigurarGrids()
        {
            // Grid Vehículos
            dgvVehiculos.AutoGenerateColumns = false;
            dgvVehiculos.Columns.Clear();
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "IdVehiculo", HeaderText = "ID", Width = 60 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Marca", HeaderText = "Marca", Width = 110 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Modelo", HeaderText = "Modelo", Width = 110 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Placa", HeaderText = "Placa", Width = 90 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Chasis", HeaderText = "Chasis", Width = 110 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Anio", HeaderText = "Año", Width = 60 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Color", HeaderText = "Color", Width = 80 });
            var colPrecio = new DataGridViewTextBoxColumn { DataPropertyName = "Precio", HeaderText = "Precio ($)", Width = 90 };
            colPrecio.DefaultCellStyle.Format = "0.00";
            dgvVehiculos.Columns.Add(colPrecio);
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Estado", HeaderText = "Estado", Width = 100 });

            // Grid Compradores
            dgvCompradores.AutoGenerateColumns = false;
            dgvCompradores.Columns.Clear();
            dgvCompradores.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Id", HeaderText = "ID", Width = 60 });
            dgvCompradores.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Documento", HeaderText = "Documento / Cédula", Width = 150 });
            dgvCompradores.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Nombre", HeaderText = "Nombre Completo", Width = 220 });
            dgvCompradores.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Correo", HeaderText = "Correo Electrónico", Width = 220 });

            // Grid Ventas
            dgvVentas.AutoGenerateColumns = false;
            dgvVentas.Columns.Clear();
            dgvVentas.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Id", HeaderText = "ID Venta", Width = 80 });
            dgvVentas.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "VehiculoId", HeaderText = "ID Vehículo", Width = 90 });
            dgvVentas.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "CompradorId", HeaderText = "ID Comprador", Width = 100 });
            dgvVentas.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Estado", HeaderText = "Estado", Width = 110 });
            dgvVentas.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Notificacion", HeaderText = "Notificación", Width = 110 });
            dgvVentas.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "PrecioAcordado", HeaderText = "Precio Acordado ($)", Width = 130 });
        }

        private string ObtenerToken() => txtJwt.Text.Trim();

        // OPERACIÓN 1: LISTAR VEHÍCULOS (GET /api/vehiculos)
        private async void btnConsultarVehiculos_Click(object sender, EventArgs e)
        {
            await ConsultarVehiculos(txtMarcaFiltro.Text.Trim());
        }

        private async Task ConsultarVehiculos(string? marca)
        {
            lblMensajeEstado.Text = "Consultando catálogo de vehículos...";
            lblMensajeEstado.ForeColor = Color.DarkBlue;

            var res = await _api.ListarVehiculosAsync(marca, ObtenerToken());
            if (res.IsSuccess)
            {
                _vehiculos = res.Data ?? new List<VehiculoDto>();
                dgvVehiculos.DataSource = _vehiculos;
                lblTotalVehiculos.Text = $"Total: {_vehiculos.Count} vehículos";
                lblMensajeEstado.Text = $"HTTP {(int)res.StatusCode}: Catálogo obtenido exitosamente.";
                lblMensajeEstado.ForeColor = Color.Green;
            }
            else
            {
                dgvVehiculos.DataSource = null;
                lblMensajeEstado.Text = $"HTTP {(int)res.StatusCode}: {res.ErrorMessage}";
                lblMensajeEstado.ForeColor = Color.Crimson;
            }
        }

        // OPERACIÓN 2: CREAR VEHÍCULO (POST /api/vehiculos)
        private async void btnCrearVehiculo_Click(object sender, EventArgs e)
        {
            using var dialogo = new FormNuevoVehiculo();
            if (dialogo.ShowDialog(this) == DialogResult.OK && dialogo.VehiculoCreado != null)
            {
                lblMensajeEstado.Text = "Creando vehículo mediante POST /api/vehiculos...";
                var res = await _api.CrearVehiculoAsync(dialogo.VehiculoCreado, ObtenerToken());
                if (res.IsSuccess)
                {
                    MessageBox.Show($"Vehículo creado con éxito!\nID generado: {res.Data?.IdVehiculo}\nMarca: {res.Data?.Marca}", "Éxito", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    await ConsultarVehiculos(null);
                }
                else
                {
                    MessageBox.Show($"Error HTTP {(int)res.StatusCode}:\n{res.ErrorMessage}\n{res.RawJson}", "Error al crear vehículo", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        // OPERACIÓN 3: LISTAR COMPRADORES (GET /api/compradores)
        private async void btnConsultarCompradores_Click(object sender, EventArgs e)
        {
            lblMensajeEstado.Text = "Consultando compradores mediante GET /api/compradores...";
            lblMensajeEstado.ForeColor = Color.DarkBlue;

            var res = await _api.ListarCompradoresAsync(ObtenerToken());
            if (res.IsSuccess)
            {
                _compradores = res.Data ?? new List<CompradorDto>();
                dgvCompradores.DataSource = _compradores;
                lblTotalCompradores.Text = $"Total: {_compradores.Count} compradores";
                lblMensajeEstado.Text = $"HTTP {(int)res.StatusCode}: Compradores obtenidos exitosamente.";
                lblMensajeEstado.ForeColor = Color.Green;
            }
            else
            {
                dgvCompradores.DataSource = null;
                lblMensajeEstado.Text = $"HTTP {(int)res.StatusCode}: {res.ErrorMessage}";
                lblMensajeEstado.ForeColor = Color.Crimson;
            }
        }

        // OPERACIÓN 4: CREAR COMPRADOR (POST /api/compradores)
        private async void btnCrearComprador_Click(object sender, EventArgs e)
        {
            using var dialogo = new FormNuevoComprador();
            if (dialogo.ShowDialog(this) == DialogResult.OK && dialogo.CompradorCreado != null)
            {
                lblMensajeEstado.Text = "Registrando comprador mediante POST /api/compradores...";
                var res = await _api.CrearCompradorAsync(dialogo.CompradorCreado, ObtenerToken());
                if (res.IsSuccess)
                {
                    MessageBox.Show($"Comprador registrado con éxito!\nID generado: {res.Data?.Id}\nNombre: {res.Data?.Nombre}", "Éxito", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    btnConsultarCompradores_Click(sender, e);
                }
                else
                {
                    MessageBox.Show($"Error HTTP {(int)res.StatusCode}:\n{res.ErrorMessage}\n{res.RawJson}", "Error al registrar comprador", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        // OPERACIÓN 5: LISTAR VENTAS (GET /api/ventas)
        private async void btnConsultarVentas_Click(object sender, EventArgs e)
        {
            lblMensajeEstado.Text = "Consultando ventas mediante GET /api/ventas...";
            lblMensajeEstado.ForeColor = Color.DarkBlue;

            var res = await _api.ListarVentasAsync(ObtenerToken());
            if (res.IsSuccess)
            {
                _ventas = res.Data ?? new List<VentaResponseDto>();
                dgvVentas.DataSource = _ventas;
                lblTotalVentas.Text = $"Total: {_ventas.Count} ventas";
                lblMensajeEstado.Text = $"HTTP {(int)res.StatusCode}: Ventas obtenidas exitosamente.";
                lblMensajeEstado.ForeColor = Color.Green;
            }
            else
            {
                dgvVentas.DataSource = null;
                lblMensajeEstado.Text = $"HTTP {(int)res.StatusCode}: {res.ErrorMessage}";
                lblMensajeEstado.ForeColor = Color.Crimson;
            }
        }

        // CONSULTA INDIVIDUAL POR ID DE VENTA (GET /api/ventas/{id})
        private async void btnConsultarVentaId_Click(object sender, EventArgs e)
        {
            if (!int.TryParse(txtVentaIdConsulta.Text.Trim(), out int id) || id <= 0)
            {
                MessageBox.Show("Ingrese un ID numérico válido de venta.", "Validación", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            var res = await _api.ConsultarVentaAsync(id, ObtenerToken());
            if (res.IsSuccess && res.Data != null)
            {
                MessageBox.Show(
                    $"Venta #{res.Data.Id}\n" +
                    $"Vehículo ID: {res.Data.VehiculoId}\n" +
                    $"Comprador ID: {res.Data.CompradorId}\n" +
                    $"Estado: {res.Data.Estado}\n" +
                    $"Notificación: {res.Data.Notificacion}\n" +
                    $"Precio: ${res.Data.PrecioAcordado}",
                    $"Detalle de Venta #{id}",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
            }
            else
            {
                MessageBox.Show($"HTTP {(int)res.StatusCode}: {res.ErrorMessage}\n{res.RawJson}", "Error al consultar venta", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }
    }
}
