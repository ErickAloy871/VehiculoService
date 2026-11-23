using System;
using System.Drawing;
using System.Windows.Forms;
using Proyecto_Vehiculos.DTO;

namespace Proyecto_Vehiculos
{
    public class FormNuevoVehiculo : Form
    {
        public VehiculoCrearDto? VehiculoCreado { get; private set; }

        private readonly TextBox txtMarca = new() { Width = 220 };
        private readonly TextBox txtModelo = new() { Width = 220 };
        private readonly TextBox txtPlaca = new() { Width = 220 };
        private readonly TextBox txtChasis = new() { Width = 220 };
        private readonly NumericUpDown numAnio = new() { Width = 220, Minimum = 1990, Maximum = 2030, Value = 2025 };
        private readonly TextBox txtColor = new() { Width = 220 };
        private readonly NumericUpDown numPrecio = new() { Width = 220, Minimum = 100, Maximum = 500000, DecimalPlaces = 2, Value = 25000 };
        private readonly Button btnGuardar = new() { Text = "Registrar Vehículo", DialogResult = DialogResult.OK, Width = 140, Height = 32 };
        private readonly Button btnCancelar = new() { Text = "Cancelar", DialogResult = DialogResult.Cancel, Width = 100, Height = 32 };

        public FormNuevoVehiculo()
        {
            Text = "Administración: Registrar Nuevo Vehículo";
            Size = new Size(380, 420);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;
            StartPosition = FormStartPosition.CenterParent;

            var panel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                Padding = new Padding(20),
                ColumnCount = 2,
                RowCount = 9
            };

            void AgregarFila(string etiqueta, Control control)
            {
                panel.Controls.Add(new Label { Text = etiqueta, AutoSize = true, Anchor = AnchorStyles.Left });
                panel.Controls.Add(control);
            }

            AgregarFila("Marca:", txtMarca);
            AgregarFila("Modelo:", txtModelo);
            AgregarFila("Placa:", txtPlaca);
            AgregarFila("Chasis:", txtChasis);
            AgregarFila("Año:", numAnio);
            AgregarFila("Color:", txtColor);
            AgregarFila("Precio ($):", numPrecio);

            var panelBotones = new FlowLayoutPanel { FlowDirection = FlowDirection.RightToLeft, Dock = DockStyle.Fill };
            panelBotones.Controls.Add(btnCancelar);
            panelBotones.Controls.Add(btnGuardar);
            panel.Controls.Add(new Label(), 0, 8);
            panel.Controls.Add(panelBotones, 1, 8);

            Controls.Add(panel);

            btnGuardar.Click += (s, e) =>
            {
                if (string.IsNullOrWhiteSpace(txtMarca.Text) || string.IsNullOrWhiteSpace(txtModelo.Text) || string.IsNullOrWhiteSpace(txtPlaca.Text))
                {
                    MessageBox.Show("Marca, Modelo y Placa son obligatorios.", "Validación", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    DialogResult = DialogResult.None;
                    return;
                }

                VehiculoCreado = new VehiculoCrearDto
                {
                    Marca = txtMarca.Text.Trim(),
                    Modelo = txtModelo.Text.Trim(),
                    Placa = txtPlaca.Text.Trim().ToUpper(),
                    Chasis = string.IsNullOrWhiteSpace(txtChasis.Text) ? "CH-" + Guid.NewGuid().ToString("N")[..8].ToUpper() : txtChasis.Text.Trim(),
                    Anio = (int)numAnio.Value,
                    Color = string.IsNullOrWhiteSpace(txtColor.Text) ? "Blanco" : txtColor.Text.Trim(),
                    Precio = numPrecio.Value
                };
            };
        }
    }
}
