namespace BomCopier.Forms
{
    partial class SettingsForm
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
            grpColumnMapping = new GroupBox();
            numHeaderRows = new NumericUpDown();
            lblHeaderRows = new Label();
            numQuantityColumn = new NumericUpDown();
            lblQuantityColumn = new Label();
            numMaterialColumn = new NumericUpDown();
            lblMaterialColumn = new Label();
            numDocumentNameColumn = new NumericUpDown();
            lblDocumentNameColumn = new Label();
            grpFileNaming = new GroupBox();
            lblExample = new Label();
            txtTargetExtension = new TextBox();
            lblTargetExtension = new Label();
            txtFilenameSuffix = new TextBox();
            lblFilenameSuffix = new Label();
            txtBomExtension = new TextBox();
            lblBomExtension = new Label();
            grpOptions = new GroupBox();
            chkOverwrite = new CheckBox();
            btnSave = new Button();
            btnCancel = new Button();
            lblColumnHelp = new Label();
            grpColumnMapping.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)numHeaderRows).BeginInit();
            ((System.ComponentModel.ISupportInitialize)numQuantityColumn).BeginInit();
            ((System.ComponentModel.ISupportInitialize)numMaterialColumn).BeginInit();
            ((System.ComponentModel.ISupportInitialize)numDocumentNameColumn).BeginInit();
            grpFileNaming.SuspendLayout();
            grpOptions.SuspendLayout();
            SuspendLayout();
            //
            // grpColumnMapping
            //
            grpColumnMapping.BackColor = Color.FromArgb(40, 44, 52);
            grpColumnMapping.Controls.Add(numHeaderRows);
            grpColumnMapping.Controls.Add(lblHeaderRows);
            grpColumnMapping.Controls.Add(numQuantityColumn);
            grpColumnMapping.Controls.Add(lblQuantityColumn);
            grpColumnMapping.Controls.Add(numMaterialColumn);
            grpColumnMapping.Controls.Add(lblMaterialColumn);
            grpColumnMapping.Controls.Add(numDocumentNameColumn);
            grpColumnMapping.Controls.Add(lblDocumentNameColumn);
            grpColumnMapping.ForeColor = Color.White;
            grpColumnMapping.Location = new Point(12, 12);
            grpColumnMapping.Name = "grpColumnMapping";
            grpColumnMapping.Size = new Size(360, 160);
            grpColumnMapping.TabIndex = 0;
            grpColumnMapping.TabStop = false;
            grpColumnMapping.Text = "Column Mapping (1-based index)";
            //
            // numHeaderRows
            //
            numHeaderRows.BackColor = Color.FromArgb(30, 33, 40);
            numHeaderRows.ForeColor = Color.White;
            numHeaderRows.Location = new Point(180, 120);
            numHeaderRows.Maximum = new decimal(new int[] { 100, 0, 0, 0 });
            numHeaderRows.Minimum = new decimal(new int[] { 0, 0, 0, 0 });
            numHeaderRows.Name = "numHeaderRows";
            numHeaderRows.Size = new Size(80, 27);
            numHeaderRows.TabIndex = 7;
            numHeaderRows.Value = new decimal(new int[] { 2, 0, 0, 0 });
            //
            // lblHeaderRows
            //
            lblHeaderRows.AutoSize = true;
            lblHeaderRows.ForeColor = Color.FromArgb(240, 240, 240);
            lblHeaderRows.Location = new Point(20, 122);
            lblHeaderRows.Name = "lblHeaderRows";
            lblHeaderRows.Size = new Size(140, 20);
            lblHeaderRows.TabIndex = 6;
            lblHeaderRows.Text = "Header Rows to Skip:";
            //
            // numQuantityColumn
            //
            numQuantityColumn.BackColor = Color.FromArgb(30, 33, 40);
            numQuantityColumn.ForeColor = Color.White;
            numQuantityColumn.Location = new Point(180, 88);
            numQuantityColumn.Maximum = new decimal(new int[] { 100, 0, 0, 0 });
            numQuantityColumn.Minimum = new decimal(new int[] { 1, 0, 0, 0 });
            numQuantityColumn.Name = "numQuantityColumn";
            numQuantityColumn.Size = new Size(80, 27);
            numQuantityColumn.TabIndex = 5;
            numQuantityColumn.Value = new decimal(new int[] { 6, 0, 0, 0 });
            //
            // lblQuantityColumn
            //
            lblQuantityColumn.AutoSize = true;
            lblQuantityColumn.ForeColor = Color.FromArgb(240, 240, 240);
            lblQuantityColumn.Location = new Point(20, 90);
            lblQuantityColumn.Name = "lblQuantityColumn";
            lblQuantityColumn.Size = new Size(120, 20);
            lblQuantityColumn.TabIndex = 4;
            lblQuantityColumn.Text = "Quantity Column:";
            //
            // numMaterialColumn
            //
            numMaterialColumn.BackColor = Color.FromArgb(30, 33, 40);
            numMaterialColumn.ForeColor = Color.White;
            numMaterialColumn.Location = new Point(180, 56);
            numMaterialColumn.Maximum = new decimal(new int[] { 100, 0, 0, 0 });
            numMaterialColumn.Minimum = new decimal(new int[] { 1, 0, 0, 0 });
            numMaterialColumn.Name = "numMaterialColumn";
            numMaterialColumn.Size = new Size(80, 27);
            numMaterialColumn.TabIndex = 3;
            numMaterialColumn.Value = new decimal(new int[] { 12, 0, 0, 0 });
            //
            // lblMaterialColumn
            //
            lblMaterialColumn.AutoSize = true;
            lblMaterialColumn.ForeColor = Color.FromArgb(240, 240, 240);
            lblMaterialColumn.Location = new Point(20, 58);
            lblMaterialColumn.Name = "lblMaterialColumn";
            lblMaterialColumn.Size = new Size(115, 20);
            lblMaterialColumn.TabIndex = 2;
            lblMaterialColumn.Text = "Material Column:";
            //
            // numDocumentNameColumn
            //
            numDocumentNameColumn.BackColor = Color.FromArgb(30, 33, 40);
            numDocumentNameColumn.ForeColor = Color.White;
            numDocumentNameColumn.Location = new Point(180, 24);
            numDocumentNameColumn.Maximum = new decimal(new int[] { 100, 0, 0, 0 });
            numDocumentNameColumn.Minimum = new decimal(new int[] { 1, 0, 0, 0 });
            numDocumentNameColumn.Name = "numDocumentNameColumn";
            numDocumentNameColumn.Size = new Size(80, 27);
            numDocumentNameColumn.TabIndex = 1;
            numDocumentNameColumn.Value = new decimal(new int[] { 2, 0, 0, 0 });
            //
            // lblDocumentNameColumn
            //
            lblDocumentNameColumn.AutoSize = true;
            lblDocumentNameColumn.ForeColor = Color.FromArgb(240, 240, 240);
            lblDocumentNameColumn.Location = new Point(20, 26);
            lblDocumentNameColumn.Name = "lblDocumentNameColumn";
            lblDocumentNameColumn.Size = new Size(150, 20);
            lblDocumentNameColumn.TabIndex = 0;
            lblDocumentNameColumn.Text = "Document Name Column:";
            //
            // grpFileNaming
            //
            grpFileNaming.BackColor = Color.FromArgb(40, 44, 52);
            grpFileNaming.Controls.Add(lblExample);
            grpFileNaming.Controls.Add(txtTargetExtension);
            grpFileNaming.Controls.Add(lblTargetExtension);
            grpFileNaming.Controls.Add(txtFilenameSuffix);
            grpFileNaming.Controls.Add(lblFilenameSuffix);
            grpFileNaming.Controls.Add(txtBomExtension);
            grpFileNaming.Controls.Add(lblBomExtension);
            grpFileNaming.ForeColor = Color.White;
            grpFileNaming.Location = new Point(12, 178);
            grpFileNaming.Name = "grpFileNaming";
            grpFileNaming.Size = new Size(360, 150);
            grpFileNaming.TabIndex = 1;
            grpFileNaming.TabStop = false;
            grpFileNaming.Text = "File Naming";
            //
            // txtBomExtension
            //
            txtBomExtension.BackColor = Color.FromArgb(30, 33, 40);
            txtBomExtension.BorderStyle = BorderStyle.FixedSingle;
            txtBomExtension.ForeColor = Color.White;
            txtBomExtension.Location = new Point(180, 24);
            txtBomExtension.Name = "txtBomExtension";
            txtBomExtension.Size = new Size(100, 27);
            txtBomExtension.TabIndex = 1;
            txtBomExtension.Text = ".SLDPRT";
            //
            // lblBomExtension
            //
            lblBomExtension.AutoSize = true;
            lblBomExtension.ForeColor = Color.FromArgb(240, 240, 240);
            lblBomExtension.Location = new Point(20, 27);
            lblBomExtension.Name = "lblBomExtension";
            lblBomExtension.Size = new Size(110, 20);
            lblBomExtension.TabIndex = 0;
            lblBomExtension.Text = "BOM Extension:";
            //
            // txtFilenameSuffix
            //
            txtFilenameSuffix.BackColor = Color.FromArgb(30, 33, 40);
            txtFilenameSuffix.BorderStyle = BorderStyle.FixedSingle;
            txtFilenameSuffix.ForeColor = Color.White;
            txtFilenameSuffix.Location = new Point(180, 56);
            txtFilenameSuffix.Name = "txtFilenameSuffix";
            txtFilenameSuffix.Size = new Size(100, 27);
            txtFilenameSuffix.TabIndex = 3;
            txtFilenameSuffix.Text = "FLO";
            //
            // lblFilenameSuffix
            //
            lblFilenameSuffix.AutoSize = true;
            lblFilenameSuffix.ForeColor = Color.FromArgb(240, 240, 240);
            lblFilenameSuffix.Location = new Point(20, 59);
            lblFilenameSuffix.Name = "lblFilenameSuffix";
            lblFilenameSuffix.Size = new Size(115, 20);
            lblFilenameSuffix.TabIndex = 2;
            lblFilenameSuffix.Text = "Filename Suffix:";
            //
            // txtTargetExtension
            //
            txtTargetExtension.BackColor = Color.FromArgb(30, 33, 40);
            txtTargetExtension.BorderStyle = BorderStyle.FixedSingle;
            txtTargetExtension.ForeColor = Color.White;
            txtTargetExtension.Location = new Point(180, 88);
            txtTargetExtension.Name = "txtTargetExtension";
            txtTargetExtension.Size = new Size(100, 27);
            txtTargetExtension.TabIndex = 5;
            txtTargetExtension.Text = ".dwg";
            //
            // lblTargetExtension
            //
            lblTargetExtension.AutoSize = true;
            lblTargetExtension.ForeColor = Color.FromArgb(240, 240, 240);
            lblTargetExtension.Location = new Point(20, 91);
            lblTargetExtension.Name = "lblTargetExtension";
            lblTargetExtension.Size = new Size(120, 20);
            lblTargetExtension.TabIndex = 4;
            lblTargetExtension.Text = "Target Extension:";
            //
            // lblExample
            //
            lblExample.ForeColor = Color.FromArgb(100, 200, 255);
            lblExample.Location = new Point(20, 122);
            lblExample.Name = "lblExample";
            lblExample.Size = new Size(320, 20);
            lblExample.TabIndex = 6;
            lblExample.Text = "Searches: part.dwg and partFLO.dwg";
            //
            // grpOptions
            //
            grpOptions.BackColor = Color.FromArgb(40, 44, 52);
            grpOptions.Controls.Add(chkOverwrite);
            grpOptions.ForeColor = Color.White;
            grpOptions.Location = new Point(12, 334);
            grpOptions.Name = "grpOptions";
            grpOptions.Size = new Size(360, 60);
            grpOptions.TabIndex = 2;
            grpOptions.TabStop = false;
            grpOptions.Text = "Options";
            //
            // chkOverwrite
            //
            chkOverwrite.AutoSize = true;
            chkOverwrite.Checked = true;
            chkOverwrite.CheckState = CheckState.Checked;
            chkOverwrite.ForeColor = Color.FromArgb(240, 240, 240);
            chkOverwrite.Location = new Point(20, 26);
            chkOverwrite.Name = "chkOverwrite";
            chkOverwrite.Size = new Size(172, 24);
            chkOverwrite.TabIndex = 0;
            chkOverwrite.Text = "Overwrite existing files";
            chkOverwrite.UseVisualStyleBackColor = true;
            //
            // btnSave
            //
            btnSave.BackColor = Color.FromArgb(40, 160, 120);
            btnSave.FlatAppearance.BorderSize = 0;
            btnSave.FlatStyle = FlatStyle.Flat;
            btnSave.ForeColor = Color.White;
            btnSave.Location = new Point(192, 410);
            btnSave.Name = "btnSave";
            btnSave.Size = new Size(90, 35);
            btnSave.TabIndex = 3;
            btnSave.Text = "Save";
            btnSave.UseVisualStyleBackColor = false;
            btnSave.Click += btnSave_Click;
            //
            // btnCancel
            //
            btnCancel.BackColor = Color.FromArgb(70, 75, 85);
            btnCancel.FlatAppearance.BorderColor = Color.FromArgb(100, 105, 115);
            btnCancel.FlatStyle = FlatStyle.Flat;
            btnCancel.ForeColor = Color.White;
            btnCancel.Location = new Point(288, 410);
            btnCancel.Name = "btnCancel";
            btnCancel.Size = new Size(90, 35);
            btnCancel.TabIndex = 4;
            btnCancel.Text = "Cancel";
            btnCancel.UseVisualStyleBackColor = false;
            btnCancel.Click += btnCancel_Click;
            //
            // lblColumnHelp
            //
            lblColumnHelp.ForeColor = Color.FromArgb(100, 200, 255);
            lblColumnHelp.Location = new Point(12, 400);
            lblColumnHelp.Name = "lblColumnHelp";
            lblColumnHelp.Size = new Size(174, 20);
            lblColumnHelp.TabIndex = 5;
            lblColumnHelp.Text = "Column A=1, B=2, C=3...";
            //
            // SettingsForm
            //
            AcceptButton = btnSave;
            AutoScaleDimensions = new SizeF(8F, 20F);
            AutoScaleMode = AutoScaleMode.Font;
            BackColor = Color.FromArgb(28, 31, 38);
            CancelButton = btnCancel;
            ClientSize = new Size(420, 500);
            Font = new Font("Iosevka", 9F, FontStyle.Regular, GraphicsUnit.Point);
            Controls.Add(lblColumnHelp);
            Controls.Add(btnCancel);
            Controls.Add(btnSave);
            Controls.Add(grpOptions);
            Controls.Add(grpFileNaming);
            Controls.Add(grpColumnMapping);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;
            Name = "SettingsForm";
            StartPosition = FormStartPosition.CenterParent;
            Text = "Settings";
            grpColumnMapping.ResumeLayout(false);
            grpColumnMapping.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)numHeaderRows).EndInit();
            ((System.ComponentModel.ISupportInitialize)numQuantityColumn).EndInit();
            ((System.ComponentModel.ISupportInitialize)numMaterialColumn).EndInit();
            ((System.ComponentModel.ISupportInitialize)numDocumentNameColumn).EndInit();
            grpFileNaming.ResumeLayout(false);
            grpFileNaming.PerformLayout();
            grpOptions.ResumeLayout(false);
            grpOptions.PerformLayout();
            ResumeLayout(false);
        }

        #endregion

        private GroupBox grpColumnMapping;
        private NumericUpDown numDocumentNameColumn;
        private Label lblDocumentNameColumn;
        private NumericUpDown numMaterialColumn;
        private Label lblMaterialColumn;
        private NumericUpDown numQuantityColumn;
        private Label lblQuantityColumn;
        private NumericUpDown numHeaderRows;
        private Label lblHeaderRows;
        private GroupBox grpFileNaming;
        private TextBox txtBomExtension;
        private Label lblBomExtension;
        private TextBox txtFilenameSuffix;
        private Label lblFilenameSuffix;
        private TextBox txtTargetExtension;
        private Label lblTargetExtension;
        private Label lblExample;
        private GroupBox grpOptions;
        private CheckBox chkOverwrite;
        private Button btnSave;
        private Button btnCancel;
        private Label lblColumnHelp;
    }
}
