namespace Proyecto_Vehiculos
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            lblTitulo = new Label();
            lblJwt = new Label();
            txtJwt = new TextBox();
            lblEndpointGateway = new Label();
            lblMensajeEstado = new Label();
            tabControlPrincipal = new TabControl();
            tabVehiculos = new TabPage();
            dgvVehiculos = new DataGridView();
            pnlVehiculosTop = new Panel();
            lblMarcaFiltro = new Label();
            txtMarcaFiltro = new TextBox();
            btnConsultarVehiculos = new Button();
            btnCrearVehiculo = new Button();
            lblTotalVehiculos = new Label();
            tabCompradores = new TabPage();
            dgvCompradores = new DataGridView();
            pnlCompradoresTop = new Panel();
            btnConsultarCompradores = new Button();
            btnCrearComprador = new Button();
            lblTotalCompradores = new Label();
            tabVentas = new TabPage();
            dgvVentas = new DataGridView();
            pnlVentasTop = new Panel();
            btnConsultarVentas = new Button();
            lblTotalVentas = new Label();
            lblVentaIdConsulta = new Label();
            txtVentaIdConsulta = new TextBox();
            btnConsultarVentaId = new Button();

            tabControlPrincipal.SuspendLayout();
            tabVehiculos.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)dgvVehiculos).BeginInit();
            pnlVehiculosTop.SuspendLayout();
            tabCompradores.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)dgvCompradores).BeginInit();
            pnlCompradoresTop.SuspendLayout();
            tabVentas.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)dgvVentas).BeginInit();
            pnlVentasTop.SuspendLayout();
            SuspendLayout();

            // lblTitulo
            lblTitulo.AutoSize = true;
            lblTitulo.Font = new Font("Segoe UI", 15F, FontStyle.Bold);
            lblTitulo.Location = new Point(20, 15);
            lblTitulo.Name = "lblTitulo";
            lblTitulo.Size = new Size(420, 28);
            lblTitulo.TabIndex = 0;
            lblTitulo.Text = "Panel de Administración · Windows Forms";

            // lblEndpointGateway
            lblEndpointGateway.AutoSize = true;
            lblEndpointGateway.Font = new Font("Segoe UI", 8.5F, FontStyle.Italic);
            lblEndpointGateway.ForeColor = Color.DarkSlateGray;
            lblEndpointGateway.Location = new Point(500, 22);
            lblEndpointGateway.Name = "lblEndpointGateway";
            lblEndpointGateway.Size = new Size(240, 15);
            lblEndpointGateway.TabIndex = 1;
            lblEndpointGateway.Text = "Gateway NGINX: http://127.0.0.1:8090";

            // lblJwt
            lblJwt.AutoSize = true;
            lblJwt.Font = new Font("Segoe UI", 9F, FontStyle.Bold);
            lblJwt.Location = new Point(22, 55);
            lblJwt.Name = "lblJwt";
            lblJwt.Size = new Size(68, 15);
            lblJwt.TabIndex = 2;
            lblJwt.Text = "Token JWT:";

            // txtJwt
            txtJwt.Location = new Point(95, 52);
            txtJwt.Name = "txtJwt";
            txtJwt.PasswordChar = '•';
            txtJwt.Size = new Size(760, 23);
            txtJwt.TabIndex = 3;

            // lblMensajeEstado
            lblMensajeEstado.AutoSize = true;
            lblMensajeEstado.Font = new Font("Segoe UI", 9F, FontStyle.Bold);
            lblMensajeEstado.Location = new Point(22, 85);
            lblMensajeEstado.Name = "lblMensajeEstado";
            lblMensajeEstado.Size = new Size(38, 15);
            lblMensajeEstado.TabIndex = 4;
            lblMensajeEstado.Text = "Estado";

            // tabControlPrincipal
            tabControlPrincipal.Controls.Add(tabVehiculos);
            tabControlPrincipal.Controls.Add(tabCompradores);
            tabControlPrincipal.Controls.Add(tabVentas);
            tabControlPrincipal.Location = new Point(20, 115);
            tabControlPrincipal.Name = "tabControlPrincipal";
            tabControlPrincipal.SelectedIndex = 0;
            tabControlPrincipal.Size = new Size(840, 480);
            tabControlPrincipal.TabIndex = 5;

            // tabVehiculos
            tabVehiculos.Controls.Add(dgvVehiculos);
            tabVehiculos.Controls.Add(pnlVehiculosTop);
            tabVehiculos.Location = new Point(4, 24);
            tabVehiculos.Name = "tabVehiculos";
            tabVehiculos.Padding = new Padding(10);
            tabVehiculos.Size = new Size(832, 452);
            tabVehiculos.TabIndex = 0;
            tabVehiculos.Text = "🚗 Catálogo de Vehículos";
            tabVehiculos.UseVisualStyleBackColor = true;

            // pnlVehiculosTop
            pnlVehiculosTop.Dock = DockStyle.Top;
            pnlVehiculosTop.Height = 45;
            pnlVehiculosTop.Controls.Add(lblMarcaFiltro);
            pnlVehiculosTop.Controls.Add(txtMarcaFiltro);
            pnlVehiculosTop.Controls.Add(btnConsultarVehiculos);
            pnlVehiculosTop.Controls.Add(btnCrearVehiculo);
            pnlVehiculosTop.Controls.Add(lblTotalVehiculos);

            lblMarcaFiltro.Text = "Marca:";
            lblMarcaFiltro.Location = new Point(5, 12);
            lblMarcaFiltro.AutoSize = true;

            txtMarcaFiltro.Location = new Point(55, 9);
            txtMarcaFiltro.Size = new Size(130, 23);

            btnConsultarVehiculos.Text = "Listar Vehículos";
            btnConsultarVehiculos.Location = new Point(195, 7);
            btnConsultarVehiculos.Size = new Size(120, 28);
            btnConsultarVehiculos.Click += btnConsultarVehiculos_Click;

            btnCrearVehiculo.Text = "+ Crear Vehículo";
            btnCrearVehiculo.Location = new Point(325, 7);
            btnCrearVehiculo.Size = new Size(130, 28);
            btnCrearVehiculo.BackColor = Color.FromArgb(230, 245, 235);
            btnCrearVehiculo.Click += btnCrearVehiculo_Click;

            lblTotalVehiculos.Text = "Total: 0";
            lblTotalVehiculos.Location = new Point(470, 12);
            lblTotalVehiculos.AutoSize = true;

            // dgvVehiculos
            dgvVehiculos.Dock = DockStyle.Fill;
            dgvVehiculos.ReadOnly = true;
            dgvVehiculos.AllowUserToAddRows = false;
            dgvVehiculos.SelectionMode = DataGridViewSelectionMode.FullRowSelect;

            // tabCompradores
            tabCompradores.Controls.Add(dgvCompradores);
            tabCompradores.Controls.Add(pnlCompradoresTop);
            tabCompradores.Location = new Point(4, 24);
            tabCompradores.Name = "tabCompradores";
            tabCompradores.Padding = new Padding(10);
            tabCompradores.Size = new Size(832, 452);
            tabCompradores.TabIndex = 1;
            tabCompradores.Text = "👤 Compradores";
            tabCompradores.UseVisualStyleBackColor = true;

            // pnlCompradoresTop
            pnlCompradoresTop.Dock = DockStyle.Top;
            pnlCompradoresTop.Height = 45;
            pnlCompradoresTop.Controls.Add(btnConsultarCompradores);
            pnlCompradoresTop.Controls.Add(btnCrearComprador);
            pnlCompradoresTop.Controls.Add(lblTotalCompradores);

            btnConsultarCompradores.Text = "Listar Compradores";
            btnConsultarCompradores.Location = new Point(5, 7);
            btnConsultarCompradores.Size = new Size(140, 28);
            btnConsultarCompradores.Click += btnConsultarCompradores_Click;

            btnCrearComprador.Text = "+ Crear Comprador";
            btnCrearComprador.Location = new Point(155, 7);
            btnCrearComprador.Size = new Size(140, 28);
            btnCrearComprador.BackColor = Color.FromArgb(230, 245, 235);
            btnCrearComprador.Click += btnCrearComprador_Click;

            lblTotalCompradores.Text = "Total: 0";
            lblTotalCompradores.Location = new Point(310, 12);
            lblTotalCompradores.AutoSize = true;

            // dgvCompradores
            dgvCompradores.Dock = DockStyle.Fill;
            dgvCompradores.ReadOnly = true;
            dgvCompradores.AllowUserToAddRows = false;
            dgvCompradores.SelectionMode = DataGridViewSelectionMode.FullRowSelect;

            // tabVentas
            tabVentas.Controls.Add(dgvVentas);
            tabVentas.Controls.Add(pnlVentasTop);
            tabVentas.Location = new Point(4, 24);
            tabVentas.Name = "tabVentas";
            tabVentas.Padding = new Padding(10);
            tabVentas.Size = new Size(832, 452);
            tabVentas.TabIndex = 2;
            tabVentas.Text = "📋 Ventas Realizadas (Solo Consulta)";
            tabVentas.UseVisualStyleBackColor = true;

            // pnlVentasTop
            pnlVentasTop.Dock = DockStyle.Top;
            pnlVentasTop.Height = 45;
            pnlVentasTop.Controls.Add(btnConsultarVentas);
            pnlVentasTop.Controls.Add(lblTotalVentas);
            pnlVentasTop.Controls.Add(lblVentaIdConsulta);
            pnlVentasTop.Controls.Add(txtVentaIdConsulta);
            pnlVentasTop.Controls.Add(btnConsultarVentaId);

            btnConsultarVentas.Text = "Listar Ventas";
            btnConsultarVentas.Location = new Point(5, 7);
            btnConsultarVentas.Size = new Size(120, 28);
            btnConsultarVentas.Click += btnConsultarVentas_Click;

            lblTotalVentas.Text = "Total: 0";
            lblTotalVentas.Location = new Point(135, 12);
            lblTotalVentas.AutoSize = true;

            lblVentaIdConsulta.Text = "ID Venta:";
            lblVentaIdConsulta.Location = new Point(250, 12);
            lblVentaIdConsulta.AutoSize = true;

            txtVentaIdConsulta.Location = new Point(310, 9);
            txtVentaIdConsulta.Size = new Size(70, 23);

            btnConsultarVentaId.Text = "Ver Detalle";
            btnConsultarVentaId.Location = new Point(390, 7);
            btnConsultarVentaId.Size = new Size(100, 28);
            btnConsultarVentaId.Click += btnConsultarVentaId_Click;

            // dgvVentas
            dgvVentas.Dock = DockStyle.Fill;
            dgvVentas.ReadOnly = true;
            dgvVentas.AllowUserToAddRows = false;
            dgvVentas.SelectionMode = DataGridViewSelectionMode.FullRowSelect;

            // Form1
            AutoScaleDimensions = new SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(880, 610);
            Controls.Add(tabControlPrincipal);
            Controls.Add(lblMensajeEstado);
            Controls.Add(txtJwt);
            Controls.Add(lblJwt);
            Controls.Add(lblEndpointGateway);
            Controls.Add(lblTitulo);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;
            Name = "Form1";
            StartPosition = FormStartPosition.CenterScreen;
            Text = "Sistema de Administración de Vehículos · Windows Forms";
            Load += Form1_Load;

            tabControlPrincipal.ResumeLayout(false);
            tabVehiculos.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)dgvVehiculos).EndInit();
            pnlVehiculosTop.ResumeLayout(false);
            pnlVehiculosTop.PerformLayout();
            tabCompradores.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)dgvCompradores).EndInit();
            pnlCompradoresTop.ResumeLayout(false);
            pnlCompradoresTop.PerformLayout();
            tabVentas.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)dgvVentas).EndInit();
            pnlVentasTop.ResumeLayout(false);
            pnlVentasTop.PerformLayout();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private Label lblTitulo;
        private Label lblJwt;
        private TextBox txtJwt;
        private Label lblEndpointGateway;
        private Label lblMensajeEstado;
        private TabControl tabControlPrincipal;
        private TabPage tabVehiculos;
        private DataGridView dgvVehiculos;
        private Panel pnlVehiculosTop;
        private Label lblMarcaFiltro;
        private TextBox txtMarcaFiltro;
        private Button btnConsultarVehiculos;
        private Button btnCrearVehiculo;
        private Label lblTotalVehiculos;

        private TabPage tabCompradores;
        private DataGridView dgvCompradores;
        private Panel pnlCompradoresTop;
        private Button btnConsultarCompradores;
        private Button btnCrearComprador;
        private Label lblTotalCompradores;

        private TabPage tabVentas;
        private DataGridView dgvVentas;
        private Panel pnlVentasTop;
        private Button btnConsultarVentas;
        private Label lblTotalVentas;
        private Label lblVentaIdConsulta;
        private TextBox txtVentaIdConsulta;
        private Button btnConsultarVentaId;
    }
}
