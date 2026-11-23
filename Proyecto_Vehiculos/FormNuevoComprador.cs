using System;
using System.Drawing;
using System.Windows.Forms;
using Proyecto_Vehiculos.DTO;

namespace Proyecto_Vehiculos
{
    public class FormNuevoComprador : Form
    {
        public CompradorCrearDto? CompradorCreado { get; private set; }

        private readonly TextBox txtDocumento = new() { Width = 220 };
        private readonly TextBox txtNombre = new() { Width = 220 };
        private readonly TextBox txtCorreo = new() { Width = 220 };
        private readonly Button btnGuardar = new() { Text = "Registrar Comprador", DialogResult = DialogResult.OK, Width = 140, Height = 32 };
        private readonly Button btnCancelar = new() { Text = "Cancelar", DialogResult = DialogResult.Cancel, Width = 100, Height = 32 };

        public FormNuevoComprador()
        {
            Text = "Administración: Registrar Nuevo Comprador";
            Size = new Size(380, 260);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;
            StartPosition = FormStartPosition.CenterParent;

            var panel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                Padding = new Padding(20),
                ColumnCount = 2,
                RowCount = 5
            };

            void AgregarFila(string etiqueta, Control control)
            {
                panel.Controls.Add(new Label { Text = etiqueta, AutoSize = true, Anchor = AnchorStyles.Left });
                panel.Controls.Add(control);
            }

            AgregarFila("Documento:", txtDocumento);
            AgregarFila("Nombre:", txtNombre);
            AgregarFila("Correo:", txtCorreo);

            var panelBotones = new FlowLayoutPanel { FlowDirection = FlowDirection.RightToLeft, Dock = DockStyle.Fill };
            panelBotones.Controls.Add(btnCancelar);
            panelBotones.Controls.Add(btnGuardar);
            panel.Controls.Add(new Label(), 0, 4);
            panel.Controls.Add(panelBotones, 1, 4);

            Controls.Add(panel);

            btnGuardar.Click += (s, e) =>
            {
                if (string.IsNullOrWhiteSpace(txtDocumento.Text) || string.IsNullOrWhiteSpace(txtNombre.Text) || string.IsNullOrWhiteSpace(txtCorreo.Text))
                {
                    MessageBox.Show("Documento, Nombre y Correo son obligatorios.", "Validación", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    DialogResult = DialogResult.None;
                    return;
                }

                CompradorCreado = new CompradorCrearDto
                {
                    Documento = txtDocumento.Text.Trim(),
                    Nombre = txtNombre.Text.Trim(),
                    Correo = txtCorreo.Text.Trim()
                };
            };
        }
    }
}
