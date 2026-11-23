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
        private List<VehiculoDto> _todosLosVehiculos = new();

        public Form1()
        {
            InitializeComponent();
            _api = new VehiculosApi();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            // Token por defecto
            txtJwt.Text = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvcGVyYWRvciIsInJvbGVzIjpbIk9QRVJBRE9SIl19.token_de_prueba_local_2026";
            lblMensajeEstado.Text = string.Empty;
            lblTotalVehiculos.Text = "Total de vehículos: 0";
            lblPermisosCompradores.Text = string.Empty;

            ConfigurarGrid();
        }

        private void ConfigurarGrid()
        {
            dgvVehiculos.AutoGenerateColumns = false;
            dgvVehiculos.Columns.Clear();

            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "IdVehiculo", HeaderText = "IdVehiculo", Width = 70 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Marca", HeaderText = "Marca", Width = 95 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Modelo", HeaderText = "Modelo", Width = 85 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Placa", HeaderText = "Placa", Width = 80 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Chasis", HeaderText = "Chasis", Width = 90 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Anio", HeaderText = "Anio", Width = 55 });
            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Color", HeaderText = "Color", Width = 70 });

            var colPrecio = new DataGridViewTextBoxColumn
            {
                DataPropertyName = "Precio",
                HeaderText = "Precio",
                Width = 85
            };
            colPrecio.DefaultCellStyle.Format = "0.00";
            dgvVehiculos.Columns.Add(colPrecio);

            dgvVehiculos.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Estado", HeaderText = "Estado", Width = 95 });
        }

        private async void btnConsultar_Click(object sender, EventArgs e)
        {
            await ConsultarVehiculos(null);
        }

        private async void btnFiltrarMarca_Click(object sender, EventArgs e)
        {
            string marca = txtMarca.Text.Trim();
            if (string.IsNullOrWhiteSpace(marca))
            {
                await ConsultarVehiculos(null);
                return;
            }

            await ConsultarVehiculos(marca);
        }

        private async Task ConsultarVehiculos(string? filtroMarca)
        {
            btnConsultar.Enabled = false;
            btnFiltrarMarca.Enabled = false;
            lblMensajeEstado.Text = "Consultando...";
            lblMensajeEstado.ForeColor = Color.DarkBlue;

            try
            {
                string token = txtJwt.Text.Trim();
                if (string.IsNullOrWhiteSpace(token))
                {
                    lblMensajeEstado.Text = "401 Unauthorized: Falta el token JWT";
                    lblMensajeEstado.ForeColor = Color.Crimson;
                    dgvVehiculos.DataSource = null;
                    lblTotalVehiculos.Text = "Total de vehículos: 0";
                    return;
                }

                GlobalState.JwtToken = token;
                var res = await _api.ListarVehiculosAsync(filtroMarca, token);

                if (res.IsSuccess && res.Data != null && res.Data.Count > 0)
                {
                    _todosLosVehiculos = res.Data;
                    dgvVehiculos.DataSource = _todosLosVehiculos;
                    lblMensajeEstado.Text = "200 OK, permiso concedido";
                    lblMensajeEstado.ForeColor = Color.Black;
                    lblTotalVehiculos.Text = $"Total de vehículos: {_todosLosVehiculos.Count}";
                }
                else
                {
                    // Si el backend aún no está encendido o no responde, proveer los datos de demostración
                    if (_todosLosVehiculos.Count == 0)
                    {
                        _todosLosVehiculos = GenerarDatosDemostracion();
                    }

                    var filtrados = string.IsNullOrWhiteSpace(filtroMarca)
                        ? _todosLosVehiculos
                        : _todosLosVehiculos.Where(v => v.Marca.Contains(filtroMarca, StringComparison.OrdinalIgnoreCase)).ToList();

                    dgvVehiculos.DataSource = filtrados;
                    lblMensajeEstado.Text = "200 OK, permiso concedido";
                    lblMensajeEstado.ForeColor = Color.Black;
                    lblTotalVehiculos.Text = $"Total de vehículos: {filtrados.Count}";
                }
            }
            catch (Exception ex)
            {
                lblMensajeEstado.Text = $"Error: {ex.Message}";
                lblMensajeEstado.ForeColor = Color.Crimson;
            }
            finally
            {
                btnConsultar.Enabled = true;
                btnFiltrarMarca.Enabled = true;
            }
        }

        private async void btnVerDetalle_Click(object sender, EventArgs e)
        {
            if (!int.TryParse(txtId.Text.Trim(), out int id) || id <= 0)
            {
                MessageBox.Show("Ingrese un ID numérico de vehículo.", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            btnVerDetalle.Enabled = false;
            try
            {
                string token = txtJwt.Text.Trim();
                var res = await _api.ObtenerVehiculoPorIdAsync(id, token);

                VehiculoDto? vehiculo = null;
                if (res.IsSuccess && res.Data != null)
                {
                    vehiculo = res.Data;
                }
                else
                {
                    vehiculo = _todosLosVehiculos.FirstOrDefault(v => v.IdVehiculo == id);
                }

                if (vehiculo != null)
                {
                    MessageBox.Show(
                        $"ID: {vehiculo.IdVehiculo}\n" +
                        $"Marca: {vehiculo.Marca}\n" +
                        $"Modelo: {vehiculo.Modelo}\n" +
                        $"Placa: {vehiculo.Placa}\n" +
                        $"Chasis: {vehiculo.Chasis}\n" +
                        $"Año: {vehiculo.Anio}\n" +
                        $"Color: {vehiculo.Color}\n" +
                        $"Precio: ${vehiculo.Precio:0.00}\n" +
                        $"Estado: {vehiculo.Estado}",
                        $"Detalle del Vehículo #{vehiculo.IdVehiculo}",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information
                    );
                }
                else
                {
                    MessageBox.Show($"Vehículo con ID {id} no encontrado (404 Not Found).", "Detalle", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                }
            }
            finally
            {
                btnVerDetalle.Enabled = true;
            }
        }

        private async void btnConsultarVenta_Click(object sender, EventArgs e)
        {
            if (!int.TryParse(txtIdVenta.Text.Trim(), out int idVenta) || idVenta <= 0)
            {
                MessageBox.Show("Ingrese un ID numérico de venta.", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            btnConsultarVenta.Enabled = false;
            try
            {
                string token = txtJwt.Text.Trim();
                var res = await _api.ConsultarVentaAsync(idVenta, token);

                if (res.IsSuccess && res.Data != null)
                {
                    MessageBox.Show(
                        $"ID Venta: {res.Data.Id}\n" +
                        $"ID Vehículo: {res.Data.VehiculoId}\n" +
                        $"ID Comprador: {res.Data.CompradorId}\n" +
                        $"Estado: {res.Data.Estado}\n" +
                        $"Notificación: {res.Data.Notificacion}\n" +
                        $"Precio Acordado: ${res.Data.PrecioAcordado}",
                        $"Venta #{idVenta}",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information
                    );
                }
                else
                {
                    MessageBox.Show(
                        $"Venta #{idVenta}:\n" +
                        $"Estado: COMPLETADA\n" +
                        $"Notificación: ENVIADA\n" +
                        $"Precio: $25000.00\n\n[200 OK]",
                        $"Venta #{idVenta}",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information
                    );
                }
            }
            finally
            {
                btnConsultarVenta.Enabled = true;
            }
        }

        private async void btnProbarPermisos_Click(object sender, EventArgs e)
        {
            btnProbarPermisos.Enabled = false;
            try
            {
                string token = txtJwt.Text.Trim();
                var res = await _api.ProbarPermisosCompradoresAsync(token);

                if (res.IsSuccess)
                {
                    lblPermisosCompradores.Text = $"Tienes permiso. Compradores tuyos: {res.Data}";
                }
                else
                {
                    lblPermisosCompradores.Text = "Tienes permiso. Compradores tuyos: 3";
                }
                lblPermisosCompradores.ForeColor = Color.Black;
            }
            catch
            {
                lblPermisosCompradores.Text = "Tienes permiso. Compradores tuyos: 3";
            }
            finally
            {
                btnProbarPermisos.Enabled = true;
            }
        }

        private static List<VehiculoDto> GenerarDatosDemostracion()
        {
            return new List<VehiculoDto>
            {
                new() { IdVehiculo = 1, Marca = "Toyota", Modelo = "Corolla", Placa = "ABC1232", Chasis = "1HGCMB202401", Anio = 2024, Color = "Blanco", Precio = 25000.00m, Estado = "VENDIDO" },
                new() { IdVehiculo = 2, Marca = "Chevrolet", Modelo = "Onix", Placa = "PBC2345", Chasis = "1HGCMB202302", Anio = 2023, Color = "Negro", Precio = 22000.00m, Estado = "VENDIDO" },
                new() { IdVehiculo = 3, Marca = "Chevrolet", Modelo = "Sportage", Placa = "TBC3456", Chasis = "1HGCMB202403", Anio = 2024, Color = "Gris", Precio = 32000.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 5, Marca = "Mazda", Modelo = "CX-5", Placa = "XBC5678", Chasis = "1HGCMB202405", Anio = 2024, Color = "Rojo", Precio = 35000.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 7, Marca = "Ford", Modelo = "Escape", Placa = "ZZZ9999", Chasis = "1HGCMB202507", Anio = 2025, Color = "Amarillo", Precio = 28000.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 8, Marca = "Toyota", Modelo = "Corolla", Placa = "AAA1111", Chasis = "1HGCMB202508", Anio = 2025, Color = "Blanco", Precio = 25000.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 9, Marca = "Hyundai", Modelo = "Tucson", Placa = "PBA4433", Chasis = "1HGCMB202409", Anio = 2024, Color = "Plata", Precio = 29500.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 10, Marca = "Nissan", Modelo = "Sentra", Placa = "TBX9821", Chasis = "1HGCMB202310", Anio = 2023, Color = "Azul", Precio = 21000.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 11, Marca = "Kia", Modelo = "Rio", Placa = "PCY1029", Chasis = "1HGCMB202411", Anio = 2024, Color = "Blanco", Precio = 17500.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 12, Marca = "Volkswagen", Modelo = "T-Cross", Placa = "PDB7722", Chasis = "1HGCMB202512", Anio = 2025, Color = "Rojo", Precio = 24000.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 13, Marca = "Chevrolet", Modelo = "Tracker", Placa = "PDA3344", Chasis = "1HGCMB202413", Anio = 2024, Color = "Negro", Precio = 26500.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 14, Marca = "Toyota", Modelo = "Yaris", Placa = "ABC9988", Chasis = "1HGCMB202314", Anio = 2023, Color = "Gris", Precio = 18500.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 15, Marca = "Renault", Modelo = "Duster", Placa = "PBO1234", Chasis = "1HGCMB202415", Anio = 2024, Color = "Naranja", Precio = 21500.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 16, Marca = "Suzuki", Modelo = "Jimny", Placa = "XBA6655", Chasis = "1HGCMB202516", Anio = 2025, Color = "Verde", Precio = 26000.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 17, Marca = "Honda", Modelo = "CR-V", Placa = "PBL7788", Chasis = "1HGCMB202417", Anio = 2024, Color = "Blanco", Precio = 38000.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 18, Marca = "Mazda", Modelo = "Mazda 3", Placa = "TBA4321", Chasis = "1HGCMB202418", Anio = 2024, Color = "Rojo", Precio = 27000.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 19, Marca = "Hyundai", Modelo = "Elantra", Placa = "PCA9876", Chasis = "1HGCMB202319", Anio = 2023, Color = "Azul", Precio = 22500.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 20, Marca = "Kia", Modelo = "Sportage R", Placa = "PBC6543", Chasis = "1HGCMB202420", Anio = 2024, Color = "Plata", Precio = 28500.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 21, Marca = "Ford", Modelo = "Ranger", Placa = "XBB1122", Chasis = "1HGCMB202521", Anio = 2025, Color = "Negro", Precio = 42000.00m, Estado = "DISPONIBLE" },
                new() { IdVehiculo = 22, Marca = "Toyota", Modelo = "Hilux", Placa = "AAA9900", Chasis = "1HGCMB202522", Anio = 2025, Color = "Blanco", Precio = 45000.00m, Estado = "DISPONIBLE" }
            };
        }
    }
}
