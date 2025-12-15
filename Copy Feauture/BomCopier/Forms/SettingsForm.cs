using BomCopier.Models;
using BomCopier.Services;

namespace BomCopier.Forms
{
    public partial class SettingsForm : Form
    {
        private readonly ConfigService _configService;
        private AppConfig _config;

        public AppConfig Config => _config;

        public SettingsForm(AppConfig config)
        {
            InitializeComponent();
            _configService = new ConfigService();
            _config = config;
            LoadConfigToForm();
        }

        private void LoadConfigToForm()
        {
            numDocumentNameColumn.Value = _config.DocumentNameColumn;
            numMaterialColumn.Value = _config.MaterialColumn;
            numQuantityColumn.Value = _config.QuantityColumn;
            numHeaderRows.Value = _config.HeaderRows;
            txtBomExtension.Text = _config.BomFileExtension;
            txtFilenameSuffix.Text = _config.FilenameSuffix;
            txtTargetExtension.Text = _config.TargetFileExtension;
            chkOverwrite.Checked = _config.OverwriteExisting;
        }

        private void SaveFormToConfig()
        {
            _config.DocumentNameColumn = (int)numDocumentNameColumn.Value;
            _config.MaterialColumn = (int)numMaterialColumn.Value;
            _config.QuantityColumn = (int)numQuantityColumn.Value;
            _config.HeaderRows = (int)numHeaderRows.Value;
            _config.BomFileExtension = txtBomExtension.Text.Trim();
            _config.FilenameSuffix = txtFilenameSuffix.Text.Trim();
            _config.TargetFileExtension = txtTargetExtension.Text.Trim();
            _config.OverwriteExisting = chkOverwrite.Checked;
        }

        private bool ValidateSettings()
        {
            // Check for duplicate columns
            var columns = new[]
            {
                (int)numDocumentNameColumn.Value,
                (int)numMaterialColumn.Value,
                (int)numQuantityColumn.Value
            };

            if (columns.Distinct().Count() != columns.Length)
            {
                MessageBox.Show(
                    "Column indices must be unique. Please use different columns for each field.",
                    "Validation Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning);
                return false;
            }

            // Check BOM extension starts with dot
            if (!txtBomExtension.Text.StartsWith("."))
            {
                txtBomExtension.Text = "." + txtBomExtension.Text;
            }

            // Check target extension starts with dot
            if (!txtTargetExtension.Text.StartsWith("."))
            {
                txtTargetExtension.Text = "." + txtTargetExtension.Text;
            }

            return true;
        }

        private void btnSave_Click(object sender, EventArgs e)
        {
            if (!ValidateSettings())
                return;

            SaveFormToConfig();

            try
            {
                _configService.Save(_config);
                DialogResult = DialogResult.OK;
                Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Failed to save settings: {ex.Message}",
                    "Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            DialogResult = DialogResult.Cancel;
            Close();
        }
    }
}
