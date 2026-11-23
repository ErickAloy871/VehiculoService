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
            btnConsultar = new Button();
            lblMarca = new Label();
            txtMarca = new TextBox();
            btnFiltrarMarca = new Button();
            lblId = new Label();
            txtId = new TextBox();
            btnVerDetalle = new Button();
            lblMensajeEstado = new Label();
            dgvVehiculos = new DataGridView();
            lblTotalVehiculos = new Label();
            lblIdVenta = new Label();
            txtIdVenta = new TextBox();
            btnConsultarVenta = new Button();
            btnProbarPermisos = new Button();
            lblPermisosCompradores = new Label();
            ((System.ComponentModel.ISupportInitialize)dgvVehiculos).BeginInit();
            SuspendLayout();
            // 
            // lblTitulo
            // 
            lblTitulo.AutoSize = true;
            lblTitulo.Font = new Font("Segoe UI", 16F, FontStyle.Bold, GraphicsUnit.Point, 0);
            lblTitulo.Location = new Point(25, 20);
            lblTitulo.Name = "lblTitulo";
            lblTitulo.Size = new Size(236, 30);
            lblTitulo.TabIndex = 0;
            lblTitulo.Text = "Vehículos registrados";
            // 
            // lblJwt
            // 
            lblJwt.AutoSize = true;
            lblJwt.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point, 0);
            lblJwt.Location = new Point(28, 65);
            lblJwt.Name = "lblJwt";
            lblJwt.Size = new Size(27, 15);
            lblJwt.TabIndex = 1;
            lblJwt.Text = "JWT";
            // 
            // txtJwt
            // 
            txtJwt.Font = new Font("Segoe UI", 9F);
            txtJwt.Location = new Point(65, 62);
            txtJwt.Name = "txtJwt";
            txtJwt.PasswordChar = '•';
            txtJwt.Size = new Size(520, 23);
            txtJwt.TabIndex = 2;
            // 
            // btnConsultar
            // 
            btnConsultar.Font = new Font("Segoe UI", 9F);
            btnConsultar.Location = new Point(598, 60);
            btnConsultar.Name = "btnConsultar";
            btnConsultar.Size = new Size(115, 27);
            btnConsultar.TabIndex = 3;
            btnConsultar.Text = "Consultar";
            btnConsultar.UseVisualStyleBackColor = true;
            btnConsultar.Click += btnConsultar_Click;
            // 
            // lblMarca
            // 
            lblMarca.AutoSize = true;
            lblMarca.Font = new Font("Segoe UI", 9F);
            lblMarca.Location = new Point(28, 105);
            lblMarca.Name = "lblMarca";
            lblMarca.Size = new Size(40, 15);
            lblMarca.TabIndex = 4;
            lblMarca.Text = "Marca";
            // 
            // txtMarca
            // 
            txtMarca.Font = new Font("Segoe UI", 9F);
            txtMarca.Location = new Point(75, 102);
            txtMarca.Name = "txtMarca";
            txtMarca.Size = new Size(160, 23);
            txtMarca.TabIndex = 5;
            // 
            // btnFiltrarMarca
            // 
            btnFiltrarMarca.Font = new Font("Segoe UI", 9F);
            btnFiltrarMarca.Location = new Point(245, 100);
            btnFiltrarMarca.Name = "btnFiltrarMarca";
            btnFiltrarMarca.Size = new Size(125, 27);
            btnFiltrarMarca.TabIndex = 6;
            btnFiltrarMarca.Text = "Filtrar por marca";
            btnFiltrarMarca.UseVisualStyleBackColor = true;
            btnFiltrarMarca.Click += btnFiltrarMarca_Click;
            // 
            // lblId
            // 
            lblId.AutoSize = true;
            lblId.Font = new Font("Segoe UI", 9F);
            lblId.Location = new Point(390, 105);
            lblId.Name = "lblId";
            lblId.Size = new Size(18, 15);
            lblId.TabIndex = 7;
            lblId.Text = "ID";
            // 
            // txtId
            // 
            txtId.Font = new Font("Segoe UI", 9F);
            txtId.Location = new Point(415, 102);
            txtId.Name = "txtId";
            txtId.Size = new Size(65, 23);
            txtId.TabIndex = 8;
            // 
            // btnVerDetalle
            // 
            btnVerDetalle.Font = new Font("Segoe UI", 9F);
            btnVerDetalle.Location = new Point(490, 100);
            btnVerDetalle.Name = "btnVerDetalle";
            btnVerDetalle.Size = new Size(115, 27);
            btnVerDetalle.TabIndex = 9;
            btnVerDetalle.Text = "Ver detalle";
            btnVerDetalle.UseVisualStyleBackColor = true;
            btnVerDetalle.Click += btnVerDetalle_Click;
            // 
            // lblMensajeEstado
            // 
            lblMensajeEstado.AutoSize = true;
            lblMensajeEstado.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point, 0);
            lblMensajeEstado.ForeColor = Color.Black;
            lblMensajeEstado.Location = new Point(28, 140);
            lblMensajeEstado.Name = "lblMensajeEstado";
            lblMensajeEstado.Size = new Size(150, 15);
            lblMensajeEstado.TabIndex = 10;
            lblMensajeEstado.Text = "200 OK, permiso concedido";
            // 
            // dgvVehiculos
            // 
            dgvVehiculos.AllowUserToAddRows = false;
            dgvVehiculos.AllowUserToDeleteRows = false;
            dgvVehiculos.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
            dgvVehiculos.BackgroundColor = Color.White;
            dgvVehiculos.BorderStyle = BorderStyle.Fixed3D;
            dgvVehiculos.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            dgvVehiculos.Location = new Point(28, 165);
            dgvVehiculos.MultiSelect = false;
            dgvVehiculos.Name = "dgvVehiculos";
            dgvVehiculos.ReadOnly = true;
            dgvVehiculos.RowHeadersWidth = 25;
            dgvVehiculos.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            dgvVehiculos.Size = new Size(685, 230);
            dgvVehiculos.TabIndex = 11;
            // 
            // lblTotalVehiculos
            // 
            lblTotalVehiculos.AutoSize = true;
            lblTotalVehiculos.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point, 0);
            lblTotalVehiculos.Location = new Point(28, 405);
            lblTotalVehiculos.Name = "lblTotalVehiculos";
            lblTotalVehiculos.Size = new Size(118, 15);
            lblTotalVehiculos.TabIndex = 12;
            lblTotalVehiculos.Text = "Total de vehículos: 0";
            // 
            // lblIdVenta
            // 
            lblIdVenta.AutoSize = true;
            lblIdVenta.Font = new Font("Segoe UI", 9F);
            lblIdVenta.Location = new Point(28, 442);
            lblIdVenta.Name = "lblIdVenta";
            lblIdVenta.Size = new Size(51, 15);
            lblIdVenta.TabIndex = 13;
            lblIdVenta.Text = "ID venta";
            // 
            // txtIdVenta
            // 
            txtIdVenta.Font = new Font("Segoe UI", 9F);
            txtIdVenta.Location = new Point(85, 439);
            txtIdVenta.Name = "txtIdVenta";
            txtIdVenta.Size = new Size(60, 23);
            txtIdVenta.TabIndex = 14;
            // 
            // btnConsultarVenta
            // 
            btnConsultarVenta.Font = new Font("Segoe UI", 9F);
            btnConsultarVenta.Location = new Point(155, 437);
            btnConsultarVenta.Name = "btnConsultarVenta";
            btnConsultarVenta.Size = new Size(125, 27);
            btnConsultarVenta.TabIndex = 15;
            btnConsultarVenta.Text = "Consultar venta";
            btnConsultarVenta.UseVisualStyleBackColor = true;
            btnConsultarVenta.Click += btnConsultarVenta_Click;
            // 
            // btnProbarPermisos
            // 
            btnProbarPermisos.Font = new Font("Segoe UI", 9F);
            btnProbarPermisos.Location = new Point(290, 437);
            btnProbarPermisos.Name = "btnProbarPermisos";
            btnProbarPermisos.Size = new Size(190, 27);
            btnProbarPermisos.TabIndex = 16;
            btnProbarPermisos.Text = "Probar permisos compradores";
            btnProbarPermisos.UseVisualStyleBackColor = true;
            btnProbarPermisos.Click += btnProbarPermisos_Click;
            // 
            // lblPermisosCompradores
            // 
            lblPermisosCompradores.AutoSize = true;
            lblPermisosCompradores.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point, 0);
            lblPermisosCompradores.Location = new Point(28, 475);
            lblPermisosCompradores.Name = "lblPermisosCompradores";
            lblPermisosCompradores.Size = new Size(207, 15);
            lblPermisosCompradores.TabIndex = 17;
            lblPermisosCompradores.Text = "Tienes permiso. Compradores tuyos: 3";
            // 
            // Form1
            // 
            AutoScaleDimensions = new SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            BackColor = SystemColors.Control;
            ClientSize = new Size(744, 520);
            Controls.Add(lblPermisosCompradores);
            Controls.Add(btnProbarPermisos);
            Controls.Add(btnConsultarVenta);
            Controls.Add(txtIdVenta);
            Controls.Add(lblIdVenta);
            Controls.Add(lblTotalVehiculos);
            Controls.Add(dgvVehiculos);
            Controls.Add(lblMensajeEstado);
            Controls.Add(btnVerDetalle);
            Controls.Add(txtId);
            Controls.Add(lblId);
            Controls.Add(btnFiltrarMarca);
            Controls.Add(txtMarca);
            Controls.Add(lblMarca);
            Controls.Add(btnConsultar);
            Controls.Add(txtJwt);
            Controls.Add(lblJwt);
            Controls.Add(lblTitulo);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;
            Name = "Form1";
            StartPosition = FormStartPosition.CenterScreen;
            Text = "Consulta de vehículos";
            Load += Form1_Load;
            ((System.ComponentModel.ISupportInitialize)dgvVehiculos).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private Label lblTitulo;
        private Label lblJwt;
        private TextBox txtJwt;
        private Button btnConsultar;
        private Label lblMarca;
        private TextBox txtMarca;
        private Button btnFiltrarMarca;
        private Label lblId;
        private TextBox txtId;
        private Button btnVerDetalle;
        private Label lblMensajeEstado;
        private DataGridView dgvVehiculos;
        private Label lblTotalVehiculos;
        private Label lblIdVenta;
        private TextBox txtIdVenta;
        private Button btnConsultarVenta;
        private Button btnProbarPermisos;
        private Label lblPermisosCompradores;
    }
}
