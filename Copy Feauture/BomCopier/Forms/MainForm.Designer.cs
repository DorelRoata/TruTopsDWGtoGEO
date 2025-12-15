namespace BomCopier.Forms
{
    partial class MainForm
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
            pnlTop = new Panel();
            lblFileCount = new Label();
            cmbMaterial = new ComboBox();
            lblMaterial = new Label();
            btnSettings = new Button();
            btnLoadBom = new Button();
            pnlDirectories = new Panel();
            btnBrowseTarget = new Button();
            txtTargetDirectory = new TextBox();
            lblTarget = new Label();
            btnBrowseSource = new Button();
            txtSourceDirectory = new TextBox();
            lblSource = new Label();
            pnlMain = new Panel();
            pnlAvailable = new Panel();
            lstAvailable = new ListView();
            colAvailableName = new ColumnHeader();
            colAvailableQty = new ColumnHeader();
            colAvailableFound = new ColumnHeader();
            txtSearchAvailable = new TextBox();
            lblAvailable = new Label();
            pnlButtons = new Panel();
            btnAddAll = new Button();
            btnAdd = new Button();
            btnRemove = new Button();
            btnClearQueue = new Button();
            pnlQueue = new Panel();
            lstQueue = new ListView();
            colQueueName = new ColumnHeader();
            colQueueQty = new ColumnHeader();
            colQueueFound = new ColumnHeader();
            txtSearchQueue = new TextBox();
            lblQueue = new Label();
            pnlBottom = new Panel();
            btnStartCopy = new Button();
            lblStatus = new Label();
            progressBar = new ProgressBar();
            pnlTop.SuspendLayout();
            pnlDirectories.SuspendLayout();
            pnlMain.SuspendLayout();
            pnlAvailable.SuspendLayout();
            pnlButtons.SuspendLayout();
            pnlQueue.SuspendLayout();
            pnlBottom.SuspendLayout();
            SuspendLayout();
            //
            // pnlTop - Header panel with smoky glass effect
            //
            pnlTop.BackColor = Color.FromArgb(25, 25, 30);
            pnlTop.Controls.Add(lblFileCount);
            pnlTop.Controls.Add(cmbMaterial);
            pnlTop.Controls.Add(lblMaterial);
            pnlTop.Controls.Add(btnSettings);
            pnlTop.Controls.Add(btnLoadBom);
            pnlTop.Dock = DockStyle.Top;
            pnlTop.Location = new Point(0, 0);
            pnlTop.Name = "pnlTop";
            pnlTop.Padding = new Padding(12);
            pnlTop.Size = new Size(950, 55);
            pnlTop.TabIndex = 0;
            //
            // lblFileCount
            //
            lblFileCount.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            lblFileCount.Font = new Font("Iosevka", 9F, FontStyle.Italic);
            lblFileCount.ForeColor = Color.FromArgb(140, 150, 160);
            lblFileCount.Location = new Point(720, 18);
            lblFileCount.Name = "lblFileCount";
            lblFileCount.Size = new Size(130, 20);
            lblFileCount.TabIndex = 4;
            lblFileCount.Text = "0 items";
            lblFileCount.TextAlign = ContentAlignment.MiddleRight;
            //
            // cmbMaterial
            //
            cmbMaterial.BackColor = Color.FromArgb(35, 38, 45);
            cmbMaterial.DropDownStyle = ComboBoxStyle.DropDownList;
            cmbMaterial.FlatStyle = FlatStyle.Flat;
            cmbMaterial.Font = new Font("Iosevka", 9F);
            cmbMaterial.ForeColor = Color.FromArgb(200, 210, 220);
            cmbMaterial.FormattingEnabled = true;
            cmbMaterial.Location = new Point(290, 14);
            cmbMaterial.Name = "cmbMaterial";
            cmbMaterial.Size = new Size(280, 28);
            cmbMaterial.TabIndex = 3;
            cmbMaterial.SelectedIndexChanged += cmbMaterial_SelectedIndexChanged;
            //
            // lblMaterial
            //
            lblMaterial.AutoSize = true;
            lblMaterial.Font = new Font("Iosevka", 9F);
            lblMaterial.ForeColor = Color.FromArgb(180, 190, 200);
            lblMaterial.Location = new Point(220, 17);
            lblMaterial.Name = "lblMaterial";
            lblMaterial.Size = new Size(64, 20);
            lblMaterial.TabIndex = 2;
            lblMaterial.Text = "Material:";
            //
            // btnSettings
            //
            btnSettings.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnSettings.BackColor = Color.FromArgb(50, 55, 65);
            btnSettings.Cursor = Cursors.Hand;
            btnSettings.FlatAppearance.BorderColor = Color.FromArgb(70, 80, 95);
            btnSettings.FlatAppearance.BorderSize = 1;
            btnSettings.FlatAppearance.MouseOverBackColor = Color.FromArgb(65, 70, 85);
            btnSettings.FlatStyle = FlatStyle.Flat;
            btnSettings.Font = new Font("Iosevka", 9F);
            btnSettings.ForeColor = Color.FromArgb(180, 190, 200);
            btnSettings.Location = new Point(856, 12);
            btnSettings.Name = "btnSettings";
            btnSettings.Size = new Size(80, 32);
            btnSettings.TabIndex = 1;
            btnSettings.Text = "Settings";
            btnSettings.UseVisualStyleBackColor = false;
            btnSettings.Click += btnSettings_Click;
            //
            // btnLoadBom
            //
            btnLoadBom.BackColor = Color.FromArgb(45, 90, 130);
            btnLoadBom.Cursor = Cursors.Hand;
            btnLoadBom.FlatAppearance.BorderColor = Color.FromArgb(60, 110, 155);
            btnLoadBom.FlatAppearance.BorderSize = 1;
            btnLoadBom.FlatAppearance.MouseOverBackColor = Color.FromArgb(55, 105, 150);
            btnLoadBom.FlatStyle = FlatStyle.Flat;
            btnLoadBom.Font = new Font("Iosevka", 9F, FontStyle.Bold);
            btnLoadBom.ForeColor = Color.FromArgb(220, 230, 240);
            btnLoadBom.Location = new Point(12, 12);
            btnLoadBom.Name = "btnLoadBom";
            btnLoadBom.Size = new Size(110, 32);
            btnLoadBom.TabIndex = 0;
            btnLoadBom.Text = "Load BOM";
            btnLoadBom.UseVisualStyleBackColor = false;
            btnLoadBom.Click += btnLoadBom_Click;
            //
            // pnlDirectories - Directory selection with glass border
            //
            pnlDirectories.BackColor = Color.FromArgb(28, 30, 35);
            pnlDirectories.Controls.Add(btnBrowseTarget);
            pnlDirectories.Controls.Add(txtTargetDirectory);
            pnlDirectories.Controls.Add(lblTarget);
            pnlDirectories.Controls.Add(btnBrowseSource);
            pnlDirectories.Controls.Add(txtSourceDirectory);
            pnlDirectories.Controls.Add(lblSource);
            pnlDirectories.Dock = DockStyle.Top;
            pnlDirectories.Location = new Point(0, 55);
            pnlDirectories.Name = "pnlDirectories";
            pnlDirectories.Padding = new Padding(12, 8, 12, 8);
            pnlDirectories.Size = new Size(950, 75);
            pnlDirectories.TabIndex = 1;
            //
            // btnBrowseTarget
            //
            btnBrowseTarget.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnBrowseTarget.BackColor = Color.FromArgb(50, 55, 65);
            btnBrowseTarget.Cursor = Cursors.Hand;
            btnBrowseTarget.FlatAppearance.BorderColor = Color.FromArgb(70, 80, 95);
            btnBrowseTarget.FlatAppearance.MouseOverBackColor = Color.FromArgb(65, 70, 85);
            btnBrowseTarget.FlatStyle = FlatStyle.Flat;
            btnBrowseTarget.Font = new Font("Iosevka", 9F);
            btnBrowseTarget.ForeColor = Color.FromArgb(180, 190, 200);
            btnBrowseTarget.Location = new Point(878, 40);
            btnBrowseTarget.Name = "btnBrowseTarget";
            btnBrowseTarget.Size = new Size(58, 27);
            btnBrowseTarget.TabIndex = 5;
            btnBrowseTarget.Text = "...";
            btnBrowseTarget.UseVisualStyleBackColor = false;
            btnBrowseTarget.Click += btnBrowseTarget_Click;
            //
            // txtTargetDirectory
            //
            txtTargetDirectory.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            txtTargetDirectory.BackColor = Color.FromArgb(35, 38, 45);
            txtTargetDirectory.BorderStyle = BorderStyle.FixedSingle;
            txtTargetDirectory.Font = new Font("Iosevka", 9F);
            txtTargetDirectory.ForeColor = Color.FromArgb(200, 210, 220);
            txtTargetDirectory.Location = new Point(120, 40);
            txtTargetDirectory.Name = "txtTargetDirectory";
            txtTargetDirectory.Size = new Size(752, 27);
            txtTargetDirectory.TabIndex = 4;
            //
            // lblTarget
            //
            lblTarget.AutoSize = true;
            lblTarget.Font = new Font("Iosevka", 9F);
            lblTarget.ForeColor = Color.FromArgb(180, 190, 200);
            lblTarget.Location = new Point(12, 43);
            lblTarget.Name = "lblTarget";
            lblTarget.Size = new Size(92, 20);
            lblTarget.TabIndex = 3;
            lblTarget.Text = "Copy Folder:";
            //
            // btnBrowseSource
            //
            btnBrowseSource.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnBrowseSource.BackColor = Color.FromArgb(50, 55, 65);
            btnBrowseSource.Cursor = Cursors.Hand;
            btnBrowseSource.FlatAppearance.BorderColor = Color.FromArgb(70, 80, 95);
            btnBrowseSource.FlatAppearance.MouseOverBackColor = Color.FromArgb(65, 70, 85);
            btnBrowseSource.FlatStyle = FlatStyle.Flat;
            btnBrowseSource.Font = new Font("Iosevka", 9F);
            btnBrowseSource.ForeColor = Color.FromArgb(180, 190, 200);
            btnBrowseSource.Location = new Point(878, 8);
            btnBrowseSource.Name = "btnBrowseSource";
            btnBrowseSource.Size = new Size(58, 27);
            btnBrowseSource.TabIndex = 2;
            btnBrowseSource.Text = "...";
            btnBrowseSource.UseVisualStyleBackColor = false;
            btnBrowseSource.Click += btnBrowseSource_Click;
            //
            // txtSourceDirectory
            //
            txtSourceDirectory.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            txtSourceDirectory.BackColor = Color.FromArgb(35, 38, 45);
            txtSourceDirectory.BorderStyle = BorderStyle.FixedSingle;
            txtSourceDirectory.Font = new Font("Iosevka", 9F);
            txtSourceDirectory.ForeColor = Color.FromArgb(200, 210, 220);
            txtSourceDirectory.Location = new Point(120, 8);
            txtSourceDirectory.Name = "txtSourceDirectory";
            txtSourceDirectory.Size = new Size(752, 27);
            txtSourceDirectory.TabIndex = 1;
            //
            // lblSource
            //
            lblSource.AutoSize = true;
            lblSource.Font = new Font("Iosevka", 9F);
            lblSource.ForeColor = Color.FromArgb(180, 190, 200);
            lblSource.Location = new Point(12, 11);
            lblSource.Name = "lblSource";
            lblSource.Size = new Size(100, 20);
            lblSource.TabIndex = 0;
            lblSource.Text = "Source Folder:";
            //
            // pnlMain - Main content area
            //
            pnlMain.BackColor = Color.FromArgb(20, 22, 26);
            pnlMain.Controls.Add(pnlQueue);
            pnlMain.Controls.Add(pnlButtons);
            pnlMain.Controls.Add(pnlAvailable);
            pnlMain.Dock = DockStyle.Fill;
            pnlMain.Location = new Point(0, 130);
            pnlMain.Name = "pnlMain";
            pnlMain.Padding = new Padding(8);
            pnlMain.Size = new Size(950, 390);
            pnlMain.TabIndex = 2;
            //
            // pnlAvailable - Left panel with glass effect
            //
            pnlAvailable.BackColor = Color.FromArgb(32, 36, 42);
            pnlAvailable.Controls.Add(lstAvailable);
            pnlAvailable.Controls.Add(txtSearchAvailable);
            pnlAvailable.Controls.Add(lblAvailable);
            pnlAvailable.Dock = DockStyle.Left;
            pnlAvailable.Location = new Point(8, 8);
            pnlAvailable.Name = "pnlAvailable";
            pnlAvailable.Padding = new Padding(12);
            pnlAvailable.Size = new Size(510, 374);
            pnlAvailable.TabIndex = 0;
            //
            // lstAvailable
            //
            lstAvailable.BackColor = Color.FromArgb(28, 31, 38);
            lstAvailable.BorderStyle = BorderStyle.None;
            lstAvailable.Columns.AddRange(new ColumnHeader[] { colAvailableName, colAvailableQty, colAvailableFound });
            lstAvailable.Dock = DockStyle.Fill;
            lstAvailable.ForeColor = Color.FromArgb(200, 210, 220);
            lstAvailable.FullRowSelect = true;
            lstAvailable.Location = new Point(12, 62);
            lstAvailable.Name = "lstAvailable";
            lstAvailable.Size = new Size(376, 300);
            lstAvailable.TabIndex = 2;
            lstAvailable.UseCompatibleStateImageBehavior = false;
            lstAvailable.View = View.Details;
            lstAvailable.Click += lstAvailable_Click;
            lstAvailable.KeyDown += lstAvailable_KeyDown;
            //
            // colAvailableName
            //
            colAvailableName.Text = "File Name";
            colAvailableName.Width = 350;
            //
            // colAvailableQty
            //
            colAvailableQty.Text = "Qty";
            colAvailableQty.Width = 50;
            //
            // colAvailableFound
            //
            colAvailableFound.Text = "Found";
            colAvailableFound.Width = 60;
            //
            // txtSearchAvailable
            //
            txtSearchAvailable.BackColor = Color.FromArgb(40, 44, 52);
            txtSearchAvailable.BorderStyle = BorderStyle.FixedSingle;
            txtSearchAvailable.Dock = DockStyle.Top;
            txtSearchAvailable.ForeColor = Color.FromArgb(180, 190, 200);
            txtSearchAvailable.Location = new Point(12, 38);
            txtSearchAvailable.Name = "txtSearchAvailable";
            txtSearchAvailable.PlaceholderText = "Search files...";
            txtSearchAvailable.Size = new Size(376, 27);
            txtSearchAvailable.TabIndex = 1;
            txtSearchAvailable.TextChanged += txtSearchAvailable_TextChanged;
            //
            // lblAvailable
            //
            lblAvailable.Dock = DockStyle.Top;
            lblAvailable.Font = new Font("Iosevka", 11F, FontStyle.Bold);
            lblAvailable.ForeColor = Color.FromArgb(100, 160, 220);
            lblAvailable.Location = new Point(12, 12);
            lblAvailable.Name = "lblAvailable";
            lblAvailable.Padding = new Padding(0, 0, 0, 6);
            lblAvailable.Size = new Size(376, 30);
            lblAvailable.TabIndex = 0;
            lblAvailable.Text = "Available Files";
            //
            // pnlButtons - Center buttons
            //
            pnlButtons.BackColor = Color.FromArgb(20, 22, 26);
            pnlButtons.Controls.Add(btnAddAll);
            pnlButtons.Controls.Add(btnAdd);
            pnlButtons.Controls.Add(btnRemove);
            pnlButtons.Controls.Add(btnClearQueue);
            pnlButtons.Dock = DockStyle.Left;
            pnlButtons.Location = new Point(408, 8);
            pnlButtons.Name = "pnlButtons";
            pnlButtons.Size = new Size(90, 374);
            pnlButtons.TabIndex = 1;
            //
            // btnAddAll
            //
            btnAddAll.BackColor = Color.FromArgb(50, 55, 65);
            btnAddAll.Cursor = Cursors.Hand;
            btnAddAll.FlatAppearance.BorderColor = Color.FromArgb(70, 80, 95);
            btnAddAll.FlatAppearance.MouseOverBackColor = Color.FromArgb(65, 70, 85);
            btnAddAll.FlatStyle = FlatStyle.Flat;
            btnAddAll.Font = new Font("Iosevka", 8F);
            btnAddAll.ForeColor = Color.FromArgb(180, 190, 200);
            btnAddAll.Location = new Point(10, 100);
            btnAddAll.Name = "btnAddAll";
            btnAddAll.Size = new Size(70, 28);
            btnAddAll.TabIndex = 1;
            btnAddAll.Text = "Add All";
            btnAddAll.UseVisualStyleBackColor = false;
            btnAddAll.Click += btnAddAll_Click;
            //
            // btnAdd
            //
            btnAdd.BackColor = Color.FromArgb(40, 100, 80);
            btnAdd.Cursor = Cursors.Hand;
            btnAdd.FlatAppearance.BorderColor = Color.FromArgb(50, 130, 100);
            btnAdd.FlatAppearance.MouseOverBackColor = Color.FromArgb(50, 120, 95);
            btnAdd.FlatStyle = FlatStyle.Flat;
            btnAdd.Font = new Font("Iosevka", 10F, FontStyle.Bold);
            btnAdd.ForeColor = Color.FromArgb(200, 230, 210);
            btnAdd.Location = new Point(10, 140);
            btnAdd.Name = "btnAdd";
            btnAdd.Size = new Size(70, 32);
            btnAdd.TabIndex = 0;
            btnAdd.Text = ">>";
            btnAdd.UseVisualStyleBackColor = false;
            btnAdd.Click += btnAdd_Click;
            //
            // btnRemove
            //
            btnRemove.BackColor = Color.FromArgb(120, 50, 50);
            btnRemove.Cursor = Cursors.Hand;
            btnRemove.FlatAppearance.BorderColor = Color.FromArgb(150, 60, 60);
            btnRemove.FlatAppearance.MouseOverBackColor = Color.FromArgb(140, 60, 60);
            btnRemove.FlatStyle = FlatStyle.Flat;
            btnRemove.Font = new Font("Iosevka", 10F, FontStyle.Bold);
            btnRemove.ForeColor = Color.FromArgb(230, 200, 200);
            btnRemove.Location = new Point(10, 200);
            btnRemove.Name = "btnRemove";
            btnRemove.Size = new Size(70, 32);
            btnRemove.TabIndex = 2;
            btnRemove.Text = "<<";
            btnRemove.UseVisualStyleBackColor = false;
            btnRemove.Click += btnRemove_Click;
            //
            // btnClearQueue
            //
            btnClearQueue.BackColor = Color.FromArgb(50, 55, 65);
            btnClearQueue.Cursor = Cursors.Hand;
            btnClearQueue.FlatAppearance.BorderColor = Color.FromArgb(70, 80, 95);
            btnClearQueue.FlatAppearance.MouseOverBackColor = Color.FromArgb(65, 70, 85);
            btnClearQueue.FlatStyle = FlatStyle.Flat;
            btnClearQueue.Font = new Font("Iosevka", 8F);
            btnClearQueue.ForeColor = Color.FromArgb(180, 190, 200);
            btnClearQueue.Location = new Point(10, 244);
            btnClearQueue.Name = "btnClearQueue";
            btnClearQueue.Size = new Size(70, 28);
            btnClearQueue.TabIndex = 3;
            btnClearQueue.Text = "Clear";
            btnClearQueue.UseVisualStyleBackColor = false;
            btnClearQueue.Click += btnClearQueue_Click;
            //
            // pnlQueue - Right panel with glass effect
            //
            pnlQueue.BackColor = Color.FromArgb(32, 36, 42);
            pnlQueue.Controls.Add(lstQueue);
            pnlQueue.Controls.Add(txtSearchQueue);
            pnlQueue.Controls.Add(lblQueue);
            pnlQueue.Dock = DockStyle.Fill;
            pnlQueue.Location = new Point(498, 8);
            pnlQueue.Name = "pnlQueue";
            pnlQueue.Padding = new Padding(12);
            pnlQueue.Size = new Size(444, 374);
            pnlQueue.TabIndex = 2;
            //
            // lstQueue
            //
            lstQueue.BackColor = Color.FromArgb(28, 31, 38);
            lstQueue.BorderStyle = BorderStyle.None;
            lstQueue.Columns.AddRange(new ColumnHeader[] { colQueueName, colQueueQty, colQueueFound });
            lstQueue.Dock = DockStyle.Fill;
            lstQueue.ForeColor = Color.FromArgb(200, 210, 220);
            lstQueue.FullRowSelect = true;
            lstQueue.Location = new Point(12, 62);
            lstQueue.Name = "lstQueue";
            lstQueue.Size = new Size(420, 300);
            lstQueue.TabIndex = 2;
            lstQueue.UseCompatibleStateImageBehavior = false;
            lstQueue.View = View.Details;
            lstQueue.Click += lstQueue_Click;
            lstQueue.KeyDown += lstQueue_KeyDown;
            //
            // colQueueName
            //
            colQueueName.Text = "File Name";
            colQueueName.Width = 350;
            //
            // colQueueQty
            //
            colQueueQty.Text = "Qty";
            colQueueQty.Width = 50;
            //
            // colQueueFound
            //
            colQueueFound.Text = "Found";
            colQueueFound.Width = 60;
            //
            // txtSearchQueue
            //
            txtSearchQueue.BackColor = Color.FromArgb(40, 44, 52);
            txtSearchQueue.BorderStyle = BorderStyle.FixedSingle;
            txtSearchQueue.Dock = DockStyle.Top;
            txtSearchQueue.ForeColor = Color.FromArgb(180, 190, 200);
            txtSearchQueue.Location = new Point(12, 38);
            txtSearchQueue.Name = "txtSearchQueue";
            txtSearchQueue.PlaceholderText = "Search queue...";
            txtSearchQueue.Size = new Size(420, 27);
            txtSearchQueue.TabIndex = 1;
            txtSearchQueue.TextChanged += txtSearchQueue_TextChanged;
            //
            // lblQueue
            //
            lblQueue.Dock = DockStyle.Top;
            lblQueue.Font = new Font("Iosevka", 11F, FontStyle.Bold);
            lblQueue.ForeColor = Color.FromArgb(80, 180, 140);
            lblQueue.Location = new Point(12, 12);
            lblQueue.Name = "lblQueue";
            lblQueue.Padding = new Padding(0, 0, 0, 6);
            lblQueue.Size = new Size(420, 30);
            lblQueue.TabIndex = 0;
            lblQueue.Text = "Copy Queue";
            //
            // pnlBottom - Status bar with glass effect
            //
            pnlBottom.BackColor = Color.FromArgb(25, 25, 30);
            pnlBottom.Controls.Add(btnStartCopy);
            pnlBottom.Controls.Add(lblStatus);
            pnlBottom.Controls.Add(progressBar);
            pnlBottom.Dock = DockStyle.Bottom;
            pnlBottom.Location = new Point(0, 520);
            pnlBottom.Name = "pnlBottom";
            pnlBottom.Padding = new Padding(12);
            pnlBottom.Size = new Size(950, 80);
            pnlBottom.TabIndex = 3;
            //
            // btnStartCopy
            //
            btnStartCopy.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            btnStartCopy.BackColor = Color.FromArgb(40, 100, 80);
            btnStartCopy.Cursor = Cursors.Hand;
            btnStartCopy.Enabled = false;
            btnStartCopy.FlatAppearance.BorderColor = Color.FromArgb(50, 130, 100);
            btnStartCopy.FlatAppearance.MouseOverBackColor = Color.FromArgb(50, 120, 95);
            btnStartCopy.FlatStyle = FlatStyle.Flat;
            btnStartCopy.Font = new Font("Iosevka", 10F, FontStyle.Bold);
            btnStartCopy.ForeColor = Color.FromArgb(200, 230, 210);
            btnStartCopy.Location = new Point(820, 35);
            btnStartCopy.Name = "btnStartCopy";
            btnStartCopy.Size = new Size(115, 38);
            btnStartCopy.TabIndex = 2;
            btnStartCopy.Text = "Start Copy";
            btnStartCopy.UseVisualStyleBackColor = false;
            btnStartCopy.Click += btnStartCopy_Click;
            //
            // lblStatus
            //
            lblStatus.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            lblStatus.Font = new Font("Iosevka", 9F);
            lblStatus.ForeColor = Color.FromArgb(140, 150, 160);
            lblStatus.Location = new Point(12, 12);
            lblStatus.Name = "lblStatus";
            lblStatus.Size = new Size(800, 20);
            lblStatus.TabIndex = 1;
            lblStatus.Text = "Ready - Load a BOM file to begin";
            //
            // progressBar
            //
            progressBar.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            progressBar.Location = new Point(12, 38);
            progressBar.Name = "progressBar";
            progressBar.Size = new Size(800, 28);
            progressBar.TabIndex = 0;
            //
            // MainForm
            //
            AllowDrop = true;
            AutoScaleDimensions = new SizeF(8F, 20F);
            AutoScaleMode = AutoScaleMode.Font;
            BackColor = Color.FromArgb(18, 20, 24);
            ClientSize = new Size(1140, 936);
            Controls.Add(pnlMain);
            Controls.Add(pnlBottom);
            Controls.Add(pnlDirectories);
            Controls.Add(pnlTop);
            Font = new Font("Iosevka", 9F, FontStyle.Regular, GraphicsUnit.Point);
            MinimumSize = new Size(1080, 900);
            Name = "MainForm";
            StartPosition = FormStartPosition.CenterScreen;
            Text = "BOM Copier";
            DragDrop += MainForm_DragDrop;
            DragEnter += MainForm_DragEnter;
            pnlTop.ResumeLayout(false);
            pnlTop.PerformLayout();
            pnlDirectories.ResumeLayout(false);
            pnlDirectories.PerformLayout();
            pnlMain.ResumeLayout(false);
            pnlAvailable.ResumeLayout(false);
            pnlAvailable.PerformLayout();
            pnlButtons.ResumeLayout(false);
            pnlQueue.ResumeLayout(false);
            pnlQueue.PerformLayout();
            pnlBottom.ResumeLayout(false);
            ResumeLayout(false);
        }

        #endregion

        private Panel pnlTop;
        private Button btnLoadBom;
        private Button btnSettings;
        private Label lblMaterial;
        private ComboBox cmbMaterial;
        private Label lblFileCount;
        private Panel pnlDirectories;
        private Label lblSource;
        private TextBox txtSourceDirectory;
        private Button btnBrowseSource;
        private Label lblTarget;
        private TextBox txtTargetDirectory;
        private Button btnBrowseTarget;
        private Panel pnlMain;
        private Panel pnlAvailable;
        private Label lblAvailable;
        private TextBox txtSearchAvailable;
        private ListView lstAvailable;
        private ColumnHeader colAvailableName;
        private ColumnHeader colAvailableQty;
        private ColumnHeader colAvailableFound;
        private Panel pnlButtons;
        private Button btnAdd;
        private Button btnAddAll;
        private Button btnRemove;
        private Button btnClearQueue;
        private Panel pnlQueue;
        private Label lblQueue;
        private TextBox txtSearchQueue;
        private ListView lstQueue;
        private ColumnHeader colQueueName;
        private ColumnHeader colQueueQty;
        private ColumnHeader colQueueFound;
        private Panel pnlBottom;
        private ProgressBar progressBar;
        private Label lblStatus;
        private Button btnStartCopy;
    }
}
