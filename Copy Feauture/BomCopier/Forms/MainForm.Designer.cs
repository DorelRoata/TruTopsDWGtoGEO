namespace BomCopier.Forms
{
    partial class MainForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && components != null)
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            pnlTop = new Panel();
            btnLoadBom = new Button();
            lblMaterial = new Label();
            cmbMaterial = new ComboBox();
            lblVariant = new Label();
            cmbVariant = new ComboBox();
            lblVersion = new Label();
            lblFileCount = new Label();
            btnSettings = new Button();
            pnlDirectories = new Panel();
            lblSource = new Label();
            txtSourceDirectory = new TextBox();
            btnBrowseSource = new Button();
            btnScanSource = new Button();
            lblTarget = new Label();
            txtTargetDirectory = new TextBox();
            btnBrowseTarget = new Button();
            pnlMain = new Panel();
            tableMain = new TableLayoutPanel();
            pnlAvailable = new Panel();
            tableAvailable = new TableLayoutPanel();
            lblAvailable = new Label();
            lblAvailableHelp = new Label();
            txtSearchAvailable = new TextBox();
            lstAvailable = new ListView();
            colAvailableName = new ColumnHeader();
            colAvailableQty = new ColumnHeader();
            colAvailableVariant = new ColumnHeader();
            colAvailableStatus = new ColumnHeader();
            pnlButtons = new FlowLayoutPanel();
            btnAdd = new Button();
            btnAddAll = new Button();
            btnRemove = new Button();
            btnClearQueue = new Button();
            pnlQueue = new Panel();
            tableQueue = new TableLayoutPanel();
            lblQueue = new Label();
            lblQueueHelp = new Label();
            txtSearchQueue = new TextBox();
            lstQueue = new ListView();
            colQueueName = new ColumnHeader();
            colQueueQty = new ColumnHeader();
            colQueueVariant = new ColumnHeader();
            colQueueStatus = new ColumnHeader();
            pnlBottom = new Panel();
            progressBar = new ProgressBar();
            lblStatus = new Label();
            btnStartCopy = new Button();
            pnlTop.SuspendLayout();
            pnlDirectories.SuspendLayout();
            pnlMain.SuspendLayout();
            tableMain.SuspendLayout();
            pnlAvailable.SuspendLayout();
            tableAvailable.SuspendLayout();
            pnlButtons.SuspendLayout();
            pnlQueue.SuspendLayout();
            tableQueue.SuspendLayout();
            pnlBottom.SuspendLayout();
            SuspendLayout();

            // Header
            pnlTop.BackColor = Color.FromArgb(25, 25, 30);
            pnlTop.Controls.Add(btnLoadBom);
            pnlTop.Controls.Add(lblMaterial);
            pnlTop.Controls.Add(cmbMaterial);
            pnlTop.Controls.Add(lblVariant);
            pnlTop.Controls.Add(cmbVariant);
            pnlTop.Controls.Add(lblFileCount);
            pnlTop.Controls.Add(btnSettings);
            pnlTop.Dock = DockStyle.Top;
            pnlTop.Padding = new Padding(12);
            pnlTop.Size = new Size(1180, 62);

            ConfigureButton(btnLoadBom, Color.FromArgb(45, 90, 130), Color.FromArgb(220, 230, 240));
            btnLoadBom.Font = new Font("Segoe UI", 9F, FontStyle.Bold);
            btnLoadBom.Location = new Point(12, 14);
            btnLoadBom.Size = new Size(120, 34);
            btnLoadBom.Text = "Load BOM";
            btnLoadBom.Click += btnLoadBom_Click;

            ConfigureLabel(lblMaterial, "Material:");
            lblMaterial.Location = new Point(152, 21);
            lblMaterial.AutoSize = true;

            ConfigureComboBox(cmbMaterial);
            cmbMaterial.Location = new Point(220, 17);
            cmbMaterial.Size = new Size(215, 28);
            cmbMaterial.SelectedIndexChanged += cmbMaterial_SelectedIndexChanged;

            ConfigureLabel(lblVariant, "Variant:");
            lblVariant.Location = new Point(455, 21);
            lblVariant.AutoSize = true;

            ConfigureComboBox(cmbVariant);
            cmbVariant.Location = new Point(515, 17);
            cmbVariant.Size = new Size(165, 28);
            cmbVariant.SelectedIndexChanged += cmbVariant_SelectedIndexChanged;

            lblVersion.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            lblVersion.Font = new Font("Segoe UI", 9F, FontStyle.Bold);
            lblVersion.ForeColor = Color.FromArgb(100, 160, 220);
            lblVersion.Location = new Point(1012, 12);
            lblVersion.Size = new Size(154, 20);
            lblVersion.Text = "Version";
            lblVersion.TextAlign = ContentAlignment.MiddleRight;

            lblFileCount.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            lblFileCount.Font = new Font("Segoe UI", 9F, FontStyle.Italic);
            lblFileCount.ForeColor = Color.FromArgb(140, 150, 160);
            lblFileCount.Location = new Point(836, 21);
            lblFileCount.Size = new Size(220, 20);
            lblFileCount.Text = "0 available | 0 queued";
            lblFileCount.TextAlign = ContentAlignment.MiddleRight;

            ConfigureButton(btnSettings, Color.FromArgb(50, 55, 65), Color.FromArgb(190, 200, 210));
            btnSettings.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnSettings.Location = new Point(1070, 14);
            btnSettings.Size = new Size(96, 34);
            btnSettings.Text = "Settings";
            btnSettings.Click += btnSettings_Click;

            // Directories
            pnlDirectories.BackColor = Color.FromArgb(28, 30, 35);
            pnlDirectories.Controls.Add(lblSource);
            pnlDirectories.Controls.Add(txtSourceDirectory);
            pnlDirectories.Controls.Add(btnBrowseSource);
            pnlDirectories.Controls.Add(btnScanSource);
            pnlDirectories.Controls.Add(lblTarget);
            pnlDirectories.Controls.Add(txtTargetDirectory);
            pnlDirectories.Controls.Add(btnBrowseTarget);
            pnlDirectories.Dock = DockStyle.Top;
            pnlDirectories.Size = new Size(1180, 88);

            ConfigureLabel(lblSource, "Source folder:");
            lblSource.Location = new Point(12, 15);
            lblSource.AutoSize = true;

            ConfigurePathTextBox(txtSourceDirectory);
            txtSourceDirectory.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            txtSourceDirectory.Location = new Point(120, 11);
            txtSourceDirectory.Size = new Size(842, 27);

            ConfigureButton(btnBrowseSource, Color.FromArgb(50, 55, 65), Color.FromArgb(190, 200, 210));
            btnBrowseSource.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnBrowseSource.Location = new Point(970, 10);
            btnBrowseSource.Size = new Size(92, 30);
            btnBrowseSource.Text = "Browse...";
            btnBrowseSource.Click += btnBrowseSource_Click;

            ConfigureButton(btnScanSource, Color.FromArgb(50, 75, 95), Color.FromArgb(205, 220, 230));
            btnScanSource.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnScanSource.Location = new Point(1070, 10);
            btnScanSource.Size = new Size(96, 30);
            btnScanSource.Text = "Scan";
            btnScanSource.Click += btnScanSource_Click;

            ConfigureLabel(lblTarget, "Copy folder:");
            lblTarget.Location = new Point(12, 52);
            lblTarget.AutoSize = true;

            ConfigurePathTextBox(txtTargetDirectory);
            txtTargetDirectory.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            txtTargetDirectory.Location = new Point(120, 48);
            txtTargetDirectory.Size = new Size(942, 27);

            ConfigureButton(btnBrowseTarget, Color.FromArgb(50, 55, 65), Color.FromArgb(190, 200, 210));
            btnBrowseTarget.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnBrowseTarget.Location = new Point(1070, 47);
            btnBrowseTarget.Size = new Size(96, 30);
            btnBrowseTarget.Text = "Browse...";
            btnBrowseTarget.Click += btnBrowseTarget_Click;

            // Main area
            pnlMain.BackColor = Color.FromArgb(18, 20, 24);
            pnlMain.Controls.Add(tableMain);
            pnlMain.Dock = DockStyle.Fill;
            pnlMain.Padding = new Padding(10);

            tableMain.ColumnCount = 3;
            tableMain.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            tableMain.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 180F));
            tableMain.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            tableMain.Controls.Add(pnlAvailable, 0, 0);
            tableMain.Controls.Add(pnlButtons, 1, 0);
            tableMain.Controls.Add(pnlQueue, 2, 0);
            tableMain.Dock = DockStyle.Fill;
            tableMain.RowCount = 1;
            tableMain.RowStyles.Add(new RowStyle(SizeType.Percent, 100F));

            ConfigureListPanel(pnlAvailable);
            pnlAvailable.Controls.Add(tableAvailable);
            tableAvailable.ColumnCount = 1;
            tableAvailable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100F));
            tableAvailable.Controls.Add(lblAvailable, 0, 0);
            tableAvailable.Controls.Add(lblAvailableHelp, 0, 1);
            tableAvailable.Controls.Add(txtSearchAvailable, 0, 2);
            tableAvailable.Controls.Add(lstAvailable, 0, 3);
            tableAvailable.Dock = DockStyle.Fill;
            tableAvailable.Padding = new Padding(10);
            tableAvailable.RowCount = 4;
            tableAvailable.RowStyles.Add(new RowStyle(SizeType.Absolute, 32F));
            tableAvailable.RowStyles.Add(new RowStyle(SizeType.Absolute, 26F));
            tableAvailable.RowStyles.Add(new RowStyle(SizeType.Absolute, 36F));
            tableAvailable.RowStyles.Add(new RowStyle(SizeType.Percent, 100F));

            ConfigureSectionLabel(lblAvailable, "Available Files", Color.FromArgb(100, 160, 220));
            ConfigureHelpLabel(lblAvailableHelp, "Ctrl/Shift-click selects multiple; double-click adds");
            ConfigureSearchBox(txtSearchAvailable, "Search available files...");
            txtSearchAvailable.TextChanged += txtSearchAvailable_TextChanged;
            ConfigureListView(lstAvailable);
            lstAvailable.Columns.AddRange(new ColumnHeader[]
            {
                colAvailableName,
                colAvailableQty,
                colAvailableVariant,
                colAvailableStatus
            });
            ConfigureColumns(colAvailableName, colAvailableQty, colAvailableVariant, colAvailableStatus);
            lstAvailable.SelectedIndexChanged += lstAvailable_SelectedIndexChanged;
            lstAvailable.DoubleClick += lstAvailable_DoubleClick;
            lstAvailable.KeyDown += lstAvailable_KeyDown;

            pnlButtons.BackColor = Color.FromArgb(18, 20, 24);
            pnlButtons.Dock = DockStyle.Fill;
            pnlButtons.FlowDirection = FlowDirection.TopDown;
            pnlButtons.Padding = new Padding(10, 76, 10, 10);
            pnlButtons.WrapContents = false;
            pnlButtons.Controls.Add(btnAdd);
            pnlButtons.Controls.Add(btnAddAll);
            pnlButtons.Controls.Add(btnRemove);
            pnlButtons.Controls.Add(btnClearQueue);

            ConfigureQueueButton(btnAdd, "Add Selected  >", Color.FromArgb(40, 100, 80));
            btnAdd.Click += btnAdd_Click;
            ConfigureQueueButton(btnAddAll, "Add All Filtered  >>", Color.FromArgb(50, 75, 95));
            btnAddAll.Click += btnAddAll_Click;
            ConfigureQueueButton(btnRemove, "<  Remove Selected", Color.FromArgb(110, 55, 55));
            btnRemove.Margin = new Padding(3, 20, 3, 4);
            btnRemove.Click += btnRemove_Click;
            ConfigureQueueButton(btnClearQueue, "Clear Queue", Color.FromArgb(55, 58, 65));
            btnClearQueue.Click += btnClearQueue_Click;

            ConfigureListPanel(pnlQueue);
            pnlQueue.Controls.Add(tableQueue);
            tableQueue.ColumnCount = 1;
            tableQueue.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100F));
            tableQueue.Controls.Add(lblQueue, 0, 0);
            tableQueue.Controls.Add(lblQueueHelp, 0, 1);
            tableQueue.Controls.Add(txtSearchQueue, 0, 2);
            tableQueue.Controls.Add(lstQueue, 0, 3);
            tableQueue.Dock = DockStyle.Fill;
            tableQueue.Padding = new Padding(10);
            tableQueue.RowCount = 4;
            tableQueue.RowStyles.Add(new RowStyle(SizeType.Absolute, 32F));
            tableQueue.RowStyles.Add(new RowStyle(SizeType.Absolute, 26F));
            tableQueue.RowStyles.Add(new RowStyle(SizeType.Absolute, 36F));
            tableQueue.RowStyles.Add(new RowStyle(SizeType.Percent, 100F));

            ConfigureSectionLabel(lblQueue, "Copy Queue (0)", Color.FromArgb(80, 180, 140));
            ConfigureHelpLabel(lblQueueHelp, "Ctrl/Shift-click selects multiple; double-click removes");
            ConfigureSearchBox(txtSearchQueue, "Search copy queue...");
            txtSearchQueue.TextChanged += txtSearchQueue_TextChanged;
            ConfigureListView(lstQueue);
            lstQueue.Columns.AddRange(new ColumnHeader[]
            {
                colQueueName,
                colQueueQty,
                colQueueVariant,
                colQueueStatus
            });
            ConfigureColumns(colQueueName, colQueueQty, colQueueVariant, colQueueStatus);
            lstQueue.SelectedIndexChanged += lstQueue_SelectedIndexChanged;
            lstQueue.DoubleClick += lstQueue_DoubleClick;
            lstQueue.KeyDown += lstQueue_KeyDown;

            // Bottom status
            pnlBottom.BackColor = Color.FromArgb(25, 25, 30);
            pnlBottom.Controls.Add(lblVersion);
            pnlBottom.Controls.Add(lblStatus);
            pnlBottom.Controls.Add(progressBar);
            pnlBottom.Controls.Add(btnStartCopy);
            pnlBottom.Dock = DockStyle.Bottom;
            pnlBottom.Padding = new Padding(12);
            pnlBottom.Size = new Size(1180, 86);

            lblStatus.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            lblStatus.Font = new Font("Segoe UI", 9F);
            lblStatus.ForeColor = Color.FromArgb(150, 160, 170);
            lblStatus.Location = new Point(12, 12);
            lblStatus.Size = new Size(988, 22);
            lblStatus.Text = "Ready - load a BOM or select a source folder";

            progressBar.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            progressBar.Location = new Point(12, 43);
            progressBar.Size = new Size(988, 27);

            ConfigureButton(btnStartCopy, Color.FromArgb(40, 100, 80), Color.FromArgb(210, 235, 220));
            btnStartCopy.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnStartCopy.Font = new Font("Segoe UI", 9F, FontStyle.Bold);
            btnStartCopy.Location = new Point(1012, 39);
            btnStartCopy.Size = new Size(154, 35);
            btnStartCopy.Text = "Copy 0 Files";
            btnStartCopy.Click += btnStartCopy_Click;

            // Form
            AllowDrop = true;
            AutoScaleDimensions = new SizeF(8F, 20F);
            AutoScaleMode = AutoScaleMode.Font;
            BackColor = Color.FromArgb(18, 20, 24);
            ClientSize = new Size(1180, 760);
            Controls.Add(pnlMain);
            Controls.Add(pnlBottom);
            Controls.Add(pnlDirectories);
            Controls.Add(pnlTop);
            Font = new Font("Segoe UI", 9F);
            MinimumSize = new Size(1080, 680);
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
            tableMain.ResumeLayout(false);
            pnlAvailable.ResumeLayout(false);
            tableAvailable.ResumeLayout(false);
            tableAvailable.PerformLayout();
            pnlButtons.ResumeLayout(false);
            pnlQueue.ResumeLayout(false);
            tableQueue.ResumeLayout(false);
            tableQueue.PerformLayout();
            pnlBottom.ResumeLayout(false);
            ResumeLayout(false);
        }

        private static void ConfigureButton(Button button, Color backColor, Color foreColor)
        {
            button.BackColor = backColor;
            button.Cursor = Cursors.Hand;
            button.FlatAppearance.BorderColor = Color.FromArgb(75, 85, 95);
            button.FlatAppearance.MouseOverBackColor = Color.FromArgb(
                Math.Min(backColor.R + 15, 255),
                Math.Min(backColor.G + 15, 255),
                Math.Min(backColor.B + 15, 255));
            button.FlatStyle = FlatStyle.Flat;
            button.Font = new Font("Segoe UI", 9F);
            button.ForeColor = foreColor;
            button.UseVisualStyleBackColor = false;
        }

        private static void ConfigureQueueButton(Button button, string text, Color backColor)
        {
            ConfigureButton(button, backColor, Color.FromArgb(220, 230, 235));
            button.Margin = new Padding(3, 4, 3, 4);
            button.Size = new Size(154, 38);
            button.Text = text;
        }

        private static void ConfigureLabel(Label label, string text)
        {
            label.Font = new Font("Segoe UI", 9F);
            label.ForeColor = Color.FromArgb(185, 195, 205);
            label.Text = text;
        }

        private static void ConfigureComboBox(ComboBox comboBox)
        {
            comboBox.BackColor = Color.FromArgb(35, 38, 45);
            comboBox.DropDownStyle = ComboBoxStyle.DropDownList;
            comboBox.FlatStyle = FlatStyle.Flat;
            comboBox.ForeColor = Color.FromArgb(210, 220, 230);
            comboBox.FormattingEnabled = true;
        }

        private static void ConfigurePathTextBox(TextBox textBox)
        {
            textBox.BackColor = Color.FromArgb(35, 38, 45);
            textBox.BorderStyle = BorderStyle.FixedSingle;
            textBox.ForeColor = Color.FromArgb(205, 215, 225);
        }

        private static void ConfigureListPanel(Panel panel)
        {
            panel.BackColor = Color.FromArgb(32, 36, 42);
            panel.Dock = DockStyle.Fill;
            panel.Margin = new Padding(0);
        }

        private static void ConfigureSectionLabel(Label label, string text, Color color)
        {
            label.Dock = DockStyle.Fill;
            label.Font = new Font("Segoe UI", 11F, FontStyle.Bold);
            label.ForeColor = color;
            label.Text = text;
            label.TextAlign = ContentAlignment.MiddleLeft;
        }

        private static void ConfigureHelpLabel(Label label, string text)
        {
            label.Dock = DockStyle.Fill;
            label.Font = new Font("Segoe UI", 8F, FontStyle.Italic);
            label.ForeColor = Color.FromArgb(130, 140, 150);
            label.Text = text;
            label.TextAlign = ContentAlignment.MiddleLeft;
        }

        private static void ConfigureSearchBox(TextBox textBox, string placeholder)
        {
            textBox.BackColor = Color.FromArgb(40, 44, 52);
            textBox.BorderStyle = BorderStyle.FixedSingle;
            textBox.Dock = DockStyle.Fill;
            textBox.ForeColor = Color.FromArgb(200, 210, 220);
            textBox.Margin = new Padding(0, 3, 0, 5);
            textBox.PlaceholderText = placeholder;
        }

        private static void ConfigureListView(ListView listView)
        {
            listView.BackColor = Color.FromArgb(28, 31, 38);
            listView.BorderStyle = BorderStyle.None;
            listView.Dock = DockStyle.Fill;
            listView.ForeColor = Color.FromArgb(210, 220, 225);
            listView.FullRowSelect = true;
            listView.HideSelection = false;
            listView.MultiSelect = true;
            listView.UseCompatibleStateImageBehavior = false;
            listView.View = View.Details;
        }

        private static void ConfigureColumns(
            ColumnHeader name,
            ColumnHeader quantity,
            ColumnHeader variant,
            ColumnHeader status)
        {
            name.Text = "File Name";
            name.Width = 250;
            quantity.Text = "Qty";
            quantity.Width = 48;
            variant.Text = "Variant";
            variant.Width = 72;
            status.Text = "Status";
            status.Width = 108;
        }

        #endregion

        private Panel pnlTop;
        private Button btnLoadBom;
        private Label lblMaterial;
        private ComboBox cmbMaterial;
        private Label lblVariant;
        private ComboBox cmbVariant;
        private Label lblVersion;
        private Label lblFileCount;
        private Button btnSettings;
        private Panel pnlDirectories;
        private Label lblSource;
        private TextBox txtSourceDirectory;
        private Button btnBrowseSource;
        private Button btnScanSource;
        private Label lblTarget;
        private TextBox txtTargetDirectory;
        private Button btnBrowseTarget;
        private Panel pnlMain;
        private TableLayoutPanel tableMain;
        private Panel pnlAvailable;
        private TableLayoutPanel tableAvailable;
        private Label lblAvailable;
        private Label lblAvailableHelp;
        private TextBox txtSearchAvailable;
        private ListView lstAvailable;
        private ColumnHeader colAvailableName;
        private ColumnHeader colAvailableQty;
        private ColumnHeader colAvailableVariant;
        private ColumnHeader colAvailableStatus;
        private FlowLayoutPanel pnlButtons;
        private Button btnAdd;
        private Button btnAddAll;
        private Button btnRemove;
        private Button btnClearQueue;
        private Panel pnlQueue;
        private TableLayoutPanel tableQueue;
        private Label lblQueue;
        private Label lblQueueHelp;
        private TextBox txtSearchQueue;
        private ListView lstQueue;
        private ColumnHeader colQueueName;
        private ColumnHeader colQueueQty;
        private ColumnHeader colQueueVariant;
        private ColumnHeader colQueueStatus;
        private Panel pnlBottom;
        private ProgressBar progressBar;
        private Label lblStatus;
        private Button btnStartCopy;
    }
}
